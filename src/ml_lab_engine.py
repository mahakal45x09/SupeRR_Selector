import json
import os
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from src import config
from src.state_engine import load_and_enrich_data
from src.pressure_model import apply_pressure_classification
from src.metrics import aggregate_batting_metrics, aggregate_bowling_metrics
from src.bayesian_model import compute_batting_rankings, compute_bowling_rankings

def run_ml_and_format_analysis():
    print("=" * 70)
    print("  Rajasthan Royals SupeRR Selector — ML Engine & Multi-Format Rankings")
    print("=" * 70)

    # 1. Load data
    df = load_and_enrich_data()
    df = apply_pressure_classification(df)

    # 2. Overall Rankings
    print("\n--- Computing Overall Rankings ---")
    bat_agg_all = aggregate_batting_metrics(df)
    bowl_agg_all = aggregate_bowling_metrics(df)
    bat_ranked_all = compute_batting_rankings(bat_agg_all)
    bowl_ranked_all = compute_bowling_rankings(bowl_agg_all)

    # 3. Format Specific Rankings: T20 vs T20I
    print("\n--- Computing Format-Specific Rankings ---")
    format_rankings = {}
    for fmt in ['T20', 'T20I']:
        df_fmt = df[df['match_format'] == fmt].copy()
        b_agg = aggregate_batting_metrics(df_fmt)
        bw_agg = aggregate_bowling_metrics(df_fmt)
        
        # Qualified cutoffs scaled to single format (>= 150 total balls, >= 50 pressure balls)
        qual_bat = b_agg[
            (b_agg['balls_faced_total'] >= 150) &
            (b_agg['balls_faced_pressure'] >= 50)
        ].copy()
        qual_bowl = bw_agg[
            (bw_agg['legal_balls_total'] >= 150) &
            (bw_agg['legal_balls_pressure'] >= 50)
        ].copy()

        b_rk = compute_batting_rankings(qual_bat if len(qual_bat) >= 15 else b_agg)
        bw_rk = compute_bowling_rankings(qual_bowl if len(qual_bowl) >= 15 else bw_agg)

        format_rankings[fmt] = {
            'top10_batters': b_rk.head(10).to_dict(orient='records'),
            'top10_bowlers': bw_rk.head(10).to_dict(orient='records')
        }

    # 4. Build Dataset for ML Batter Runs Prediction
    print("\n--- Training Batter Pressure Runs ML Model ---")
    press_df = df[df['is_high_pressure']].copy()

    # Batter lookup map
    bat_map = bat_ranked_all.set_index('player_id')
    bowl_map = bowl_ranked_all.set_index('player_id')

    # Aggregating batter pressure innings
    bat_spells = press_df.groupby(['match_id', 'innings', 'striker_id', 'striker_name']).agg(
        balls=('runs', 'count'),
        runs=('runs', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        dots=('runs', lambda x: (x == 0).sum()),
        mean_rrr=('rrr', 'mean'),
        mean_wickets_in_hand=('wickets_in_hand', 'mean'),
        death_balls=('overid', lambda x: (x >= 16).sum()),
        pp_balls=('overid', lambda x: (x <= 6).sum())
    ).reset_index()

    bat_spells = bat_spells[bat_spells['balls'] >= 4].copy()
    bat_spells['mean_rrr'] = bat_spells['mean_rrr'].fillna(8.5).clip(4.0, 24.0)
    bat_spells['mean_wickets_in_hand'] = bat_spells['mean_wickets_in_hand'].fillna(6.0).clip(1.0, 10.0)
    bat_spells['death_ratio'] = bat_spells['death_balls'] / bat_spells['balls']
    bat_spells['pp_ratio'] = bat_spells['pp_balls'] / bat_spells['balls']

    # Attach player ratings
    bat_spells['player_rating'] = bat_spells['striker_id'].map(
        lambda pid: bat_map.loc[pid, 'pressure_rating'] if pid in bat_map.index else 50.0
    )
    bat_spells['baseline_sr'] = bat_spells['striker_id'].map(
        lambda pid: bat_map.loc[pid, 'baseline_sr'] if pid in bat_map.index else 130.0
    )
    bat_spells['pressure_sr_hist'] = bat_spells['striker_id'].map(
        lambda pid: bat_map.loc[pid, 'pressure_sr'] if pid in bat_map.index else 135.0
    )

    X_bat = bat_spells[[
        'balls', 'mean_rrr', 'mean_wickets_in_hand', 'death_ratio',
        'player_rating', 'baseline_sr', 'pressure_sr_hist'
    ]]
    y_bat = bat_spells['runs']

    X_train_b, X_test_b, y_train_b, y_test_b = train_test_split(X_bat, y_bat, test_size=0.2, random_state=42)

    bat_model = GradientBoostingRegressor(n_estimators=120, max_depth=4, learning_rate=0.08, random_state=42)
    bat_model.fit(X_train_b, y_train_b)

    y_pred_b = bat_model.predict(X_test_b)
    bat_r2 = float(r2_score(y_test_b, y_pred_b))
    bat_mae = float(mean_absolute_error(y_test_b, y_pred_b))
    bat_rmse = float(np.sqrt(mean_squared_error(y_test_b, y_pred_b)))

    bat_feature_names = [
        'Balls Faced (Volume)',
        'Required Run Rate (Leverage)',
        'Wickets In Hand (Resource)',
        'Death Overs Ratio (Phase)',
        'Pressure Clutch Rating',
        'Baseline Strike Rate',
        'Historical Pressure SR'
    ]
    bat_importances = bat_model.feature_importances_
    bat_feat_imp = [
        {'feature': name, 'importance': round(float(imp * 100), 2)}
        for name, imp in sorted(zip(bat_feature_names, bat_importances), key=lambda x: x[1], reverse=True)
    ]

    print(f"Batter Model: R2 = {bat_r2:.3f}, MAE = {bat_mae:.2f}, RMSE = {bat_rmse:.2f}")

    # 5. Build Dataset for ML Bowler Performance Prediction
    print("\n--- Training Bowler Performance ML Model ---")
    bowl_spells = press_df.groupby(['match_id', 'innings', 'bowler_id', 'bowler_name']).agg(
        legal_balls=('is_legal_ball', 'sum'),
        runs_conceded=('is_bowler_run', 'sum'),
        wickets=('is_bowler_wicket', 'sum'),
        dots=('runs', lambda x: (x == 0).sum()),
        mean_rrr=('rrr', 'mean'),
        mean_wickets_in_hand=('wickets_in_hand', 'mean'),
        death_balls=('overid', lambda x: (x >= 16).sum())
    ).reset_index()

    bowl_spells = bowl_spells[bowl_spells['legal_balls'] >= 4].copy()
    bowl_spells['mean_rrr'] = bowl_spells['mean_rrr'].fillna(8.5).clip(4.0, 24.0)
    bowl_spells['mean_wickets_in_hand'] = bowl_spells['mean_wickets_in_hand'].fillna(6.0).clip(1.0, 10.0)
    bowl_spells['death_ratio'] = bowl_spells['death_balls'] / bowl_spells['legal_balls']
    bowl_spells['overs'] = bowl_spells['legal_balls'] / 6.0

    bowl_spells['player_rating'] = bowl_spells['bowler_id'].map(
        lambda pid: bowl_map.loc[pid, 'pressure_rating'] if pid in bowl_map.index else 50.0
    )
    bowl_spells['baseline_econ'] = bowl_spells['bowler_id'].map(
        lambda pid: bowl_map.loc[pid, 'baseline_econ'] if pid in bowl_map.index else 8.5
    )
    bowl_spells['pressure_econ_hist'] = bowl_spells['bowler_id'].map(
        lambda pid: bowl_map.loc[pid, 'pressure_econ'] if pid in bowl_map.index else 9.0
    )
    bowl_spells['pressure_wsr_hist'] = bowl_spells['bowler_id'].map(
        lambda pid: bowl_map.loc[pid, 'pressure_wsr'] if pid in bowl_map.index else 18.0
    )

    X_bowl = bowl_spells[[
        'overs', 'mean_rrr', 'mean_wickets_in_hand', 'death_ratio',
        'player_rating', 'baseline_econ', 'pressure_econ_hist'
    ]]
    y_bowl_runs = bowl_spells['runs_conceded']
    y_bowl_wkts = bowl_spells['wickets']

    X_tr_bw, X_te_bw, y_tr_r, y_te_r = train_test_split(X_bowl, y_bowl_runs, test_size=0.2, random_state=42)
    _, _, y_tr_w, y_te_w = train_test_split(X_bowl, y_bowl_wkts, test_size=0.2, random_state=42)

    bowl_run_model = GradientBoostingRegressor(n_estimators=100, max_depth=3, learning_rate=0.08, random_state=42)
    bowl_run_model.fit(X_tr_bw, y_tr_r)
    y_pred_runs = bowl_run_model.predict(X_te_bw)

    bowl_wkt_model = RandomForestRegressor(n_estimators=100, max_depth=4, random_state=42)
    bowl_wkt_model.fit(X_tr_bw, y_tr_w)
    y_pred_wkts = bowl_wkt_model.predict(X_te_bw)

    bowl_r2 = float(r2_score(y_te_r, y_pred_runs))
    bowl_mae = float(mean_absolute_error(y_te_r, y_pred_runs))
    bowl_rmse = float(np.sqrt(mean_squared_error(y_te_r, y_pred_runs)))

    wkt_mae = float(mean_absolute_error(y_te_w, y_pred_wkts))

    bowl_feature_names = [
        'Overs Bowled (Quota)',
        'Required Run Rate (Defending)',
        'Wickets In Hand (Opposition)',
        'Death Overs Ratio (Phase)',
        'Bowler Clutch Rating',
        'Baseline Economy Rate',
        'Historical Pressure Economy'
    ]
    bowl_feat_imp = [
        {'feature': name, 'importance': round(float(imp * 100), 2)}
        for name, imp in sorted(zip(bowl_feature_names, bowl_run_model.feature_importances_), key=lambda x: x[1], reverse=True)
    ]

    print(f"Bowler Model: R2 = {bowl_r2:.3f}, MAE = {bowl_mae:.2f}, RMSE = {bowl_rmse:.2f}, Wickets MAE = {wkt_mae:.2f}")

    # 6. Linear Coefficients / Weights for lightweight client simulation
    # Also fit Ridge models for fast interpretable inference
    ridge_bat = Ridge(alpha=1.0).fit(X_train_b, y_train_b)
    ridge_bowl = Ridge(alpha=1.0).fit(X_tr_bw, y_tr_r)

    bat_coef_dict = {feat: float(c) for feat, c in zip(X_bat.columns, ridge_bat.coef_)}
    bat_coef_dict['intercept'] = float(ridge_bat.intercept_)

    bowl_coef_dict = {feat: float(c) for feat, c in zip(X_bowl.columns, ridge_bowl.coef_)}
    bowl_coef_dict['intercept'] = float(ridge_bowl.intercept_)

    # 7. Compile Final ML Lab & Multi-Format Package
    ml_data = {
        'metadata': {
            'total_deliveries': 200999,
            'match_formats': 2,
            'formats': ['T20 (IPL / Domestic)', 'T20I (International)'],
            'deliveries_t20': int(df[df['match_format'] == 'T20'].shape[0]),
            'deliveries_t20i': int(df[df['match_format'] == 'T20I'].shape[0]),
            'matches_total': 867,
            'high_pressure_deliveries': 62655,
            'pressure_ratio_pct': 31.17
        },
        'format_rankings': {
            'T20': format_rankings['T20'],
            'T20I': format_rankings['T20I'],
            'Combined': {
                'top10_batters': bat_ranked_all.head(10).to_dict(orient='records'),
                'top10_bowlers': bowl_ranked_all.head(10).to_dict(orient='records')
            }
        },
        'ml_models': {
            'batter_model': {
                'name': 'Gradient Boosted Batter Runs Regressor',
                'accuracy': {
                    'r2_score': round(bat_r2, 3),
                    'mae': round(bat_mae, 2),
                    'rmse': round(bat_rmse, 2),
                    'sample_size': len(bat_spells)
                },
                'feature_importance': bat_feat_imp,
                'ridge_coefficients': bat_coef_dict
            },
            'bowler_model': {
                'name': 'Gradient Boosted Bowler Runs & Wicket Regressor',
                'accuracy': {
                    'r2_score': round(bowl_r2, 3),
                    'runs_mae': round(bowl_mae, 2),
                    'runs_rmse': round(bowl_rmse, 2),
                    'wickets_mae': round(wkt_mae, 2),
                    'sample_size': len(bowl_spells)
                },
                'feature_importance': bowl_feat_imp,
                'ridge_coefficients': bowl_coef_dict
            }
        }
    }

    out_path = os.path.join(config.OUTPUT_DIR, 'ml_lab_data.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(ml_data, f, indent=2)
    print(f"\nML Lab data exported successfully to: {out_path}")

    # Also merge format & ML lab data into dashboard_data.json
    dash_path = os.path.join(config.OUTPUT_DIR, 'dashboard_data.json')
    with open(dash_path, 'r', encoding='utf-8') as f:
        dash_data = json.load(f)
    
    dash_data['format_rankings'] = ml_data['format_rankings']
    dash_data['ml_models'] = ml_data['ml_models']
    dash_data['metadata']['match_formats'] = 2
    dash_data['metadata']['deliveries_t20'] = ml_data['metadata']['deliveries_t20']
    dash_data['metadata']['deliveries_t20i'] = ml_data['metadata']['deliveries_t20i']

    with open(dash_path, 'w', encoding='utf-8') as f:
        json.dump(dash_data, f, indent=2)
    print(f"Updated {dash_path} with format rankings and ML models!")

if __name__ == '__main__':
    run_ml_and_format_analysis()
