import json
import os
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, roc_auc_score, log_loss

from src import config
from src.state_engine import load_and_enrich_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from src.pressure_model import apply_pressure_classification
from src.metrics import aggregate_batting_metrics, aggregate_bowling_metrics
from src.bayesian_model import compute_batting_rankings, compute_bowling_rankings

def train_and_export_xgboost_models():
    print("=" * 75)
    print("  Training Official Delivery-Level XGBoost Models for Rajasthan Royals")
    print("  Model 1: Batter Runs Regression")
    print("  Model 2A: Bowler Runs Conceded Regression")
    print("  Model 2B: Bowler Next-Ball Wicket Binary Classification")
    print("=" * 75)

    df = load_and_enrich_data()
    df = apply_pressure_classification(df)

    bat_agg = aggregate_batting_metrics(df)
    bowl_agg = aggregate_bowling_metrics(df)
    bat_ranked = compute_batting_rankings(bat_agg)
    bowl_ranked = compute_bowling_rankings(bowl_agg)

    bat_map = bat_ranked.set_index('player_id')
    bowl_map = bowl_ranked.set_index('player_id')

    # Continuous pressure level and situational variables
    df['pressure_level'] = np.where(df['is_high_pressure'], 2.0, 1.0) * df['ball_leverage']
    df['required_run_rate'] = df['rrr'].fillna(8.5).clip(0.0, 30.0)
    df['current_run_rate'] = np.where(
        df['cur_legal_balls'] > 0,
        (df['cur_runs'] * 6.0) / df['cur_legal_balls'],
        7.5
    ).clip(0.0, 24.0)
    df['wickets_remaining'] = df['wickets_in_hand'].clip(1, 10)
    df['balls_remaining_feat'] = df['balls_remaining'].clip(0, 120)
    df['innings_phase'] = np.where(df['overid'] <= 6, 1, np.where(df['overid'] <= 15, 2, 3))
    df['is_pace'] = np.where(df['pace_or_spin'] == 'Pace', 1, 0)

    # Bowler style encoding
    top_styles = [
        'Right-arm medium-fast', 'Left-arm medium-fast', 'Slow left-arm orthodox',
        'Right-arm Leg-Break', 'Right-arm fast-medium', 'Left-arm fast-medium',
        'Right-arm Fast', 'Right-arm offbreak', 'Left-arm Fast'
    ]
    style_map = {s: i + 1 for i, s in enumerate(top_styles)}
    df['bowler_style_code'] = df['bowling_type'].map(lambda x: style_map.get(x, 0))

    # Player lookups
    df['batter_rating'] = df['striker_id'].map(lambda pid: bat_map.loc[pid, 'pressure_rating'] if pid in bat_map.index else 50.0)
    df['batter_baseline_sr'] = df['striker_id'].map(lambda pid: bat_map.loc[pid, 'baseline_sr'] if pid in bat_map.index else 130.0)
    df['batter_pressure_sr'] = df['striker_id'].map(lambda pid: bat_map.loc[pid, 'pressure_sr'] if pid in bat_map.index else 135.0)
    df['batter_boundary_pct'] = df['striker_id'].map(lambda pid: bat_map.loc[pid, 'pressure_boundary_pct'] if pid in bat_map.index else 18.0)

    df['bowler_rating'] = df['bowler_id'].map(lambda pid: bowl_map.loc[pid, 'pressure_rating'] if pid in bowl_map.index else 50.0)
    df['bowler_baseline_econ'] = df['bowler_id'].map(lambda pid: bowl_map.loc[pid, 'baseline_econ'] if pid in bowl_map.index else 8.5)
    df['bowler_pressure_econ'] = df['bowler_id'].map(lambda pid: bowl_map.loc[pid, 'pressure_econ'] if pid in bowl_map.index else 8.0)
    df['bowler_dot_pct'] = df['bowler_id'].map(lambda pid: bowl_map.loc[pid, 'pressure_dot_pct'] if pid in bowl_map.index else 40.0)
    df['bowler_pressure_wsr'] = df['bowler_id'].map(lambda pid: bowl_map.loc[pid, 'pressure_wsr'] if pid in bowl_map.index else 16.0)

    # Filter legal deliveries
    leg_df = df[df['is_legal_ball']].copy()
    print(f"Dataset ready: {len(leg_df)} legal deliveries for XGBoost training.")

    # -------------------------------------------------------------
    # MODEL 1: BATTER PERFORMANCE PREDICTION (Next Delivery Runs)
    # -------------------------------------------------------------
    print("\n--- Training Model 1: Batter Performance XGBoost Regressor ---")
    feat_bat = [
        'pressure_level', 'required_run_rate', 'wickets_remaining',
        'balls_remaining_feat', 'innings_phase', 'batter_rating',
        'batter_baseline_sr', 'batter_pressure_sr', 'batter_boundary_pct',
        'is_pace', 'bowler_style_code'
    ]
    feat_bat_labels = [
        'Pressure Level (Leverage)', 'Required Run Rate', 'Wickets Remaining',
        'Balls Remaining in Innings', 'Innings Phase (PP/Mid/Death)', 'Batter Clutch Rating',
        'Batter Baseline SR', 'Batter Pressure SR', 'Batter Boundary %',
        'Bowler Pace vs Spin', 'Bowler Style Code'
    ]

    X_b = leg_df[feat_bat]
    y_b = leg_df['runs']

    X_tr_b, X_te_b, y_tr_b, y_te_b = train_test_split(X_b, y_b, test_size=0.2, random_state=42)

    m1_xgb = xgb.XGBRegressor(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=-1
    )
    m1_xgb.fit(X_tr_b, y_tr_b)
    pred_b = m1_xgb.predict(X_te_b)

    m1_mae = float(mean_absolute_error(y_te_b, pred_b))
    m1_rmse = float(np.sqrt(mean_squared_error(y_te_b, pred_b)))
    m1_r2 = float(r2_score(y_te_b, pred_b))

    m1_importances = [
        {'feature': lbl, 'key': k, 'importance': round(float(imp * 100), 2)}
        for lbl, k, imp in sorted(zip(feat_bat_labels, feat_bat, m1_xgb.feature_importances_), key=lambda x: x[2], reverse=True)
    ]
    print(f"Model 1: MAE = {m1_mae:.3f}, RMSE = {m1_rmse:.3f}, R2 = {m1_r2:.4f}")

    # -------------------------------------------------------------
    # MODEL 2: BOWLER PERFORMANCE PREDICTION
    # Model 2A: Runs Conceded (Regression)
    # Model 2B: Wicket Probability (Binary Classification)
    # -------------------------------------------------------------
    print("\n--- Training Model 2A: Bowler Runs Conceded XGBoost Regressor ---")
    feat_bowl = [
        'pressure_level', 'current_run_rate', 'required_run_rate',
        'wickets_remaining', 'balls_remaining_feat', 'bowler_rating',
        'bowler_baseline_econ', 'bowler_pressure_econ', 'bowler_dot_pct',
        'bowler_pressure_wsr', 'is_pace', 'bowler_style_code', 'innings_phase'
    ]
    feat_bowl_labels = [
        'Pressure Level (Leverage)', 'Current Run Rate (CRR)', 'Required Run Rate (RRR)',
        'Wickets Remaining', 'Balls Remaining in Innings', 'Bowler Clutch Rating',
        'Bowler Baseline Economy', 'Bowler Pressure Economy', 'Bowler Dot Ball %',
        'Bowler Pressure WSR', 'Bowler Pace vs Spin', 'Bowling Style Code', 'Innings Phase'
    ]

    X_bw = leg_df[feat_bowl]
    y_bw_r = leg_df['is_bowler_run']
    y_bw_w = leg_df['is_bowler_wicket'].astype(int)

    X_tr_bw, X_te_bw, y_tr_r, y_te_r = train_test_split(X_bw, y_bw_r, test_size=0.2, random_state=42)
    _, _, y_tr_w, y_te_w = train_test_split(X_bw, y_bw_w, test_size=0.2, random_state=42)

    # Model 2A: Runs conceded
    m2a_xgb = xgb.XGBRegressor(
        n_estimators=120,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=-1
    )
    m2a_xgb.fit(X_tr_bw, y_tr_r)
    pred_bw_r = m2a_xgb.predict(X_te_bw)

    m2a_mae = float(mean_absolute_error(y_te_r, pred_bw_r))
    m2a_rmse = float(np.sqrt(mean_squared_error(y_te_r, pred_bw_r)))
    m2a_r2 = float(r2_score(y_te_r, pred_bw_r))

    m2a_importances = [
        {'feature': lbl, 'key': k, 'importance': round(float(imp * 100), 2)}
        for lbl, k, imp in sorted(zip(feat_bowl_labels, feat_bowl, m2a_xgb.feature_importances_), key=lambda x: x[2], reverse=True)
    ]
    print(f"Model 2A: MAE = {m2a_mae:.3f}, RMSE = {m2a_rmse:.3f}, R2 = {m2a_r2:.4f}")

    print("\n--- Training Model 2B: Bowler Wicket Probability XGBoost Classifier ---")
    m2b_xgb = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=5.0, # Handle class imbalance
        random_state=42,
        n_jobs=-1
    )
    m2b_xgb.fit(X_tr_bw, y_tr_w)
    pred_bw_w_prob = m2b_xgb.predict_proba(X_te_bw)[:, 1]

    m2b_auc = float(roc_auc_score(y_te_w, pred_bw_w_prob))
    m2b_logloss = float(log_loss(y_te_w, pred_bw_w_prob))

    m2b_importances = [
        {'feature': lbl, 'key': k, 'importance': round(float(imp * 100), 2)}
        for lbl, k, imp in sorted(zip(feat_bowl_labels, feat_bowl, m2b_xgb.feature_importances_), key=lambda x: x[2], reverse=True)
    ]
    print(f"Model 2B: ROC-AUC = {m2b_auc:.3f}, LogLoss = {m2b_logloss:.3f}, Baseline Wicket Rate = {np.mean(y_te_w)*100:.2f}%")

    # Save models in backend/
    os.makedirs(os.path.join(BASE_DIR, 'backend', 'models'), exist_ok=True)
    m1_xgb.save_model(os.path.join(BASE_DIR, 'backend', 'models', 'm1_batter_xgb.json'))
    m2a_xgb.save_model(os.path.join(BASE_DIR, 'backend', 'models', 'm2a_bowler_runs_xgb.json'))
    m2b_xgb.save_model(os.path.join(BASE_DIR, 'backend', 'models', 'm2b_bowler_wkt_xgb.json'))
    print("XGBoost model files saved to backend/models/")

    # Also extract linear surrogate parameters for zero-latency client simulator
    from sklearn.linear_model import Ridge, LogisticRegression
    ridge_bat = Ridge(alpha=1.0).fit(X_tr_b, y_tr_b)
    ridge_bowl = Ridge(alpha=1.0).fit(X_tr_bw, y_tr_r)
    logit_wkt = LogisticRegression(max_iter=500).fit(X_tr_bw, y_tr_w)

    bat_weights = {k: float(c) for k, c in zip(feat_bat, ridge_bat.coef_)}
    bat_weights['intercept'] = float(ridge_bat.intercept_)

    bowl_runs_weights = {k: float(c) for k, c in zip(feat_bowl, ridge_bowl.coef_)}
    bowl_runs_weights['intercept'] = float(ridge_bowl.intercept_)

    bowl_wkt_weights = {k: float(c) for k, c in zip(feat_bowl, logit_wkt.coef_[0])}
    bowl_wkt_weights['intercept'] = float(logit_wkt.intercept_[0])

    # Compile official JSON
    xgboost_spec = {
        'model_1_batter': {
            'name': 'Model 1 — Batter Performance Prediction',
            'objective': 'Predict how many runs a batter may score on the next delivery.',
            'type': 'Regression',
            'algorithm': 'XGBoost Regressor (xgb.XGBRegressor)',
            'alternative': 'Random Forest Regressor',
            'target': 'Batter runs on the delivery (runs: 0, 1, 2, 3, 4, 6)',
            'metrics': {
                'mae': round(m1_mae, 3),
                'rmse': round(m1_rmse, 3),
                'r2_score': round(m1_r2, 4),
                'dataset_deliveries': len(leg_df),
                'test_samples': len(X_te_b)
            },
            'feature_importance': m1_importances,
            'weights': bat_weights,
            'input_features': [
                'Pressure level', 'Required run rate', 'Wickets remaining',
                'Balls remaining', 'Innings phase', 'Batter ID and historical performance',
                'Bowler type and pace/spin'
            ]
        },
        'model_2_bowler': {
            'name': 'Model 2 — Bowler Performance Prediction',
            'objective': 'Predict runs conceded and the probability of taking a wicket.',
            'model_a': {
                'type': 'Regression for runs conceded on next delivery',
                'algorithm': 'XGBoost Regressor (xgb.XGBRegressor)',
                'target': 'Runs conceded on delivery (is_bowler_run)',
                'metrics': {
                    'mae': round(m2a_mae, 3),
                    'rmse': round(m2a_rmse, 3),
                    'r2_score': round(m2a_r2, 4)
                },
                'feature_importance': m2a_importances,
                'weights': bowl_runs_weights
            },
            'model_b': {
                'type': 'Binary classification for wicket probability on next delivery',
                'algorithm': 'XGBoost Classifier (xgb.XGBClassifier)',
                'target': 'Wicket on delivery (is_bowler_wicket)',
                'metrics': {
                    'roc_auc': round(m2b_auc, 3),
                    'log_loss': round(m2b_logloss, 3),
                    'mean_prob_pct': round(float(np.mean(pred_bw_w_prob) * 100), 2)
                },
                'feature_importance': m2b_importances,
                'weights': bowl_wkt_weights
            },
            'input_features': [
                'Pressure level', 'Current run rate and required run rate',
                'Wickets remaining', 'Balls remaining',
                'Bowler ID and historical economy', 'Bowling type and pace/spin',
                'Innings phase'
            ]
        }
    }

    # Update output JSON files
    with open(os.path.join(config.OUTPUT_DIR, 'dashboard_data.json'), 'r', encoding='utf-8') as f:
        d = json.load(f)
    d['xgboost_models'] = xgboost_spec
    with open(os.path.join(config.OUTPUT_DIR, 'dashboard_data.json'), 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2)

    with open(os.path.join(config.OUTPUT_DIR, 'ml_lab_data.json'), 'r', encoding='utf-8') as f:
        ml_d = json.load(f)
    ml_d['xgboost_models'] = xgboost_spec
    with open(os.path.join(config.OUTPUT_DIR, 'ml_lab_data.json'), 'w', encoding='utf-8') as f:
        json.dump(ml_d, f, indent=2)

    print("\nSuccessfully updated dashboard_data.json and ml_lab_data.json with XGBoost specs!")

if __name__ == '__main__':
    train_and_export_xgboost_models()
