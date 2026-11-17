import numpy as np
import pandas as pd
from . import config

def aggregate_batting_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates delivery-level batting performances into player-level
    baseline, pressure, and delta differential statistics.
    """
    print("Aggregating batting metrics across baseline and pressure phases...")
    bat_df = df[df['extras_type'] != 'wide'].copy()
    bat_df['is_boundary'] = bat_df['is_four'] | bat_df['is_six']
    bat_df['is_dot'] = (bat_df['runs'] == 0) & (bat_df['extras1_runs'] == 0)

    # 1. Total Career in Dataset (2022-2026)
    b_all = bat_df.groupby(['striker_id', 'striker_name']).agg(
        balls_faced_total=('runs', 'count'),
        runs_total=('runs', 'sum'),
        dismissals_total=('is_striker_out', 'sum'),
        matches_total=('match_id', 'nunique')
    ).reset_index()

    # 2. Baseline (Non-Pressure)
    b_norm = bat_df[~bat_df['is_high_pressure']].groupby(['striker_id', 'striker_name']).agg(
        balls_faced_baseline=('runs', 'count'),
        runs_baseline=('runs', 'sum'),
        dismissals_baseline=('is_striker_out', 'sum')
    ).reset_index()

    # 3. High Pressure
    b_press = bat_df[bat_df['is_high_pressure']].groupby(['striker_id', 'striker_name']).agg(
        balls_faced_pressure=('runs', 'count'),
        runs_pressure=('runs', 'sum'),
        dismissals_pressure=('is_striker_out', 'sum'),
        dots_pressure=('is_dot', 'sum'),
        boundaries_pressure=('is_boundary', 'sum'),
        va_pressure=('bat_value_added', 'sum'),
        weighted_balls_pressure=('ball_leverage', 'sum'),
        matches_pressure=('match_id', 'nunique')
    ).reset_index()

    bat = b_all.merge(b_norm, on=['striker_id', 'striker_name'], how='left').merge(
        b_press, on=['striker_id', 'striker_name'], how='left'
    ).fillna(0)

    # Calculate baseline rates
    bat['baseline_sr'] = (bat['runs_baseline'] / np.maximum(1, bat['balls_faced_baseline'])) * 100.0
    bat['baseline_avg'] = bat['runs_baseline'] / np.maximum(1, bat['dismissals_baseline'])

    # Calculate pressure rates
    bat['pressure_sr'] = np.where(
        bat['balls_faced_pressure'] > 0,
        (bat['runs_pressure'] / bat['balls_faced_pressure']) * 100.0,
        0.0
    )
    bat['pressure_avg'] = np.where(
        bat['balls_faced_pressure'] > 0,
        bat['runs_pressure'] / np.maximum(1, bat['dismissals_pressure']),
        0.0
    )
    bat['pressure_dot_pct'] = np.where(
        bat['balls_faced_pressure'] > 0,
        (bat['dots_pressure'] / bat['balls_faced_pressure']) * 100.0,
        0.0
    )
    bat['pressure_boundary_pct'] = np.where(
        bat['balls_faced_pressure'] > 0,
        (bat['boundaries_pressure'] / bat['balls_faced_pressure']) * 100.0,
        0.0
    )

    # Relative deltas
    bat['delta_sr'] = bat['pressure_sr'] - bat['baseline_sr']
    bat['delta_avg'] = bat['pressure_avg'] - bat['baseline_avg']
    bat['va_per_ball_pressure'] = np.where(
        bat['balls_faced_pressure'] > 0,
        bat['va_pressure'] / bat['balls_faced_pressure'],
        0.0
    )

    return bat.rename(columns={'striker_id': 'player_id', 'striker_name': 'player_name'})


def aggregate_bowling_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates delivery-level bowling performances into player-level
    baseline, pressure, and delta differential statistics.
    """
    print("Aggregating bowling metrics across baseline and pressure phases...")
    bowl_df = df.copy()
    bowl_df['is_dot'] = (bowl_df['is_bowler_run'] == 0) & bowl_df['is_legal_ball']
    bowl_df['is_boundary'] = bowl_df['is_four'] | bowl_df['is_six']

    # 1. Total Career in Dataset (2022-2026)
    bw_all = bowl_df.groupby(['bowler_id', 'bowler_name']).agg(
        legal_balls_total=('is_legal_ball', 'sum'),
        runs_total=('is_bowler_run', 'sum'),
        wickets_total=('is_bowler_wicket', 'sum'),
        matches_total=('match_id', 'nunique')
    ).reset_index()

    # 2. Baseline (Non-Pressure)
    bw_norm = bowl_df[~bowl_df['is_high_pressure']].groupby(['bowler_id', 'bowler_name']).agg(
        legal_balls_baseline=('is_legal_ball', 'sum'),
        runs_baseline=('is_bowler_run', 'sum'),
        wickets_baseline=('is_bowler_wicket', 'sum')
    ).reset_index()

    # 3. High Pressure
    bw_press = bowl_df[bowl_df['is_high_pressure']].groupby(['bowler_id', 'bowler_name']).agg(
        legal_balls_pressure=('is_legal_ball', 'sum'),
        runs_pressure=('is_bowler_run', 'sum'),
        wickets_pressure=('is_bowler_wicket', 'sum'),
        dots_pressure=('is_dot', 'sum'),
        boundaries_pressure=('is_boundary', 'sum'),
        va_pressure=('bowl_value_added', 'sum'),
        weighted_balls_pressure=('ball_leverage', 'sum'),
        matches_pressure=('match_id', 'nunique')
    ).reset_index()

    bowl = bw_all.merge(bw_norm, on=['bowler_id', 'bowler_name'], how='left').merge(
        bw_press, on=['bowler_id', 'bowler_name'], how='left'
    ).fillna(0)

    # Calculate baseline rates
    bowl['baseline_econ'] = (bowl['runs_baseline'] / np.maximum(1, bowl['legal_balls_baseline'])) * 6.0

    # Calculate pressure rates
    bowl['pressure_econ'] = np.where(
        bowl['legal_balls_pressure'] > 0,
        (bowl['runs_pressure'] / bowl['legal_balls_pressure']) * 6.0,
        0.0
    )
    bowl['pressure_wsr'] = np.where(
        bowl['wickets_pressure'] > 0,
        bowl['legal_balls_pressure'] / bowl['wickets_pressure'],
        50.0
    )
    bowl['pressure_dot_pct'] = np.where(
        bowl['legal_balls_pressure'] > 0,
        (bowl['dots_pressure'] / bowl['legal_balls_pressure']) * 100.0,
        0.0
    )
    bowl['pressure_boundary_pct'] = np.where(
        bowl['legal_balls_pressure'] > 0,
        (bowl['boundaries_pressure'] / bowl['legal_balls_pressure']) * 100.0,
        0.0
    )

    # Relative deltas: positive delta_econ means the bowler tightened up under pressure
    bowl['delta_econ'] = bowl['baseline_econ'] - bowl['pressure_econ']
    bowl['va_per_ball_pressure'] = np.where(
        bowl['legal_balls_pressure'] > 0,
        bowl['va_pressure'] / bowl['legal_balls_pressure'],
        0.0
    )

    return bowl.rename(columns={'bowler_id': 'player_id', 'bowler_name': 'player_name'})
