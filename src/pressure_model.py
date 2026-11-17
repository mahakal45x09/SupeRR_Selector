import numpy as np
import pandas as pd
from . import config

def apply_pressure_classification(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifies every delivery into High Pressure vs Normal Baseline,
    computes situational leverage, and evaluates Value Added Above Par.
    """
    print("Classifying delivery-level pressure states...")

    # 1. Innings 2 (Chasing Pressure)
    inn2_pressure = (
        (df['innings'] == 2) &
        (
            # Close Finish Window (Overs 16-20, balls remaining <= 30 and game is tight)
            ((df['balls_remaining'] <= 30) & (df['runs_needed'] > 0) & (df['runs_needed'] <= df['balls_remaining'] * 2.5)) |
            # Steep Required Run Rate (Back 10 overs with RRR >= 9.5)
            ((df['balls_remaining'] <= 72) & (df['rrr'] >= 9.5) & (df['runs_needed'] <= df['balls_remaining'] * 3.0)) |
            # Resource Pressure (4 or fewer wickets in hand and runs needed > balls remaining)
            ((df['wickets_in_hand'] <= 4) & (df['runs_needed'] > df['balls_remaining']) & (df['runs_needed'] <= df['balls_remaining'] * 2.5))
        )
    )

    # 2. Innings 1 (Target-Setting Pressure)
    inn1_pressure = (
        (df['innings'] == 1) &
        (
            # Death Overs Crucible (Overs 16-20)
            (df['overid'] >= 16) |
            # Early Collapse Recovery (>=3 wickets lost in Powerplay or >=4 before Over 10)
            ((df['cur_wickets'] >= 3) & (df['overid'] <= 6)) |
            ((df['cur_wickets'] >= 4) & (df['overid'] <= 10))
        )
    )

    # 3. Super Overs (Innings 3 & 4)
    super_over_pressure = (df['innings'] >= 3)

    # Unified Pressure Flag
    df['is_high_pressure'] = inn2_pressure | inn1_pressure | super_over_pressure

    # Match Stakes Multiplier (Knockout/Playoff boost)
    df['stage_weight'] = np.where(df['knock_out'] == 1, config.KNOCKOUT_STAGE_WEIGHT, config.LEAGUE_STAGE_WEIGHT)
    df['ball_leverage'] = df['comp_weight'] * df['stage_weight']

    # Empirical Par Baseline by Competition Tier, Innings, and Pressure State
    par_table = df.groupby(['comp_tier', 'innings', 'is_high_pressure']).agg(
        par_bat_runs=('runs', 'mean'),
        par_bowl_runs=('is_bowler_run', 'mean'),
        par_wicket_prob=('is_bowler_wicket', 'mean')
    ).reset_index()

    df = df.merge(par_table, on=['comp_tier', 'innings', 'is_high_pressure'], how='left')

    # Value Added Above Par per Delivery
    df['bat_value_added'] = (df['runs'] - df['par_bat_runs']) * df['ball_leverage']
    df['bowl_value_added'] = (
        (df['par_bowl_runs'] - df['is_bowler_run']) +
        config.WICKET_RUN_VALUE * (df['is_bowler_wicket'] - df['par_wicket_prob'])
    ) * df['ball_leverage']

    hp_count = df['is_high_pressure'].sum()
    hp_pct = (hp_count / len(df)) * 100
    print(f"Pressure classification complete: {hp_count} deliveries ({hp_pct:.2f}%) tagged as High Pressure.")

    return df
