import numpy as np
import pandas as pd
from scipy.stats import zscore
from . import config

def compute_batting_rankings(bat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies qualification cutoffs, Empirical Bayes shrinkage, volume weighting,
    and composite scoring to rank batters under pressure.
    """
    print(f"Filtering qualified batters (>= {config.BATTER_MIN_TOTAL_BALLS} total balls, >= {config.BATTER_MIN_PRESSURE_BALLS} pressure balls)...")
    qual = bat_df[
        (bat_df['balls_faced_total'] >= config.BATTER_MIN_TOTAL_BALLS) &
        (bat_df['balls_faced_pressure'] >= config.BATTER_MIN_PRESSURE_BALLS)
    ].copy()

    # Empirical Bayes Shrinkage
    mu_sr = qual['pressure_sr'].median()
    mu_avg = qual['pressure_avg'].median()

    qual['bayes_pressure_sr'] = (
        qual['balls_faced_pressure'] * qual['pressure_sr'] + config.BAYES_K_BATTER * mu_sr
    ) / (qual['balls_faced_pressure'] + config.BAYES_K_BATTER)

    qual['bayes_pressure_avg'] = (
        qual['dismissals_pressure'] * qual['pressure_avg'] + config.BAYES_K_WICKETS * mu_avg
    ) / (qual['dismissals_pressure'] + config.BAYES_K_WICKETS)

    # Volume confidence factor (rewards sustained proven performance)
    qual['volume_weight'] = np.sqrt(
        qual['weighted_balls_pressure'] / (qual['weighted_balls_pressure'] + 100.0)
    )

    # Standardized components
    z_va = zscore(qual['va_per_ball_pressure'])
    z_sr = zscore(qual['bayes_pressure_sr'])
    z_delta = zscore(qual['delta_sr'])
    z_avg = zscore(np.log1p(qual['bayes_pressure_avg']))
    z_bnd = zscore(qual['pressure_boundary_pct'])

    # Composite Score:
    # 30% Value Added per ball (Par & Leverage adjusted)
    # 25% Pressure Strike Rate (Shrunk)
    # 20% Delta Strike Rate (Elevation under pressure)
    # 15% Pressure Batting Average (Finishing stability)
    # 10% Boundary Hitting %
    raw_bat_score = (0.30 * z_va + 0.25 * z_sr + 0.20 * z_delta + 0.15 * z_avg + 0.10 * z_bnd)
    qual['composite_score'] = raw_bat_score * qual['volume_weight']

    # Normalize to 0-100 rating scale (mean 50, std 15)
    qual['pressure_rating'] = 50.0 + 15.0 * zscore(qual['composite_score'])

    ranked = qual.sort_values('pressure_rating', ascending=False).reset_index(drop=True)
    ranked['rank'] = range(1, len(ranked) + 1)
    return ranked


def compute_bowling_rankings(bowl_df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies qualification cutoffs, Empirical Bayes shrinkage, volume weighting,
    and composite scoring to rank bowlers under pressure.
    """
    print(f"Filtering qualified bowlers (>= {config.BOWLER_MIN_TOTAL_BALLS} total balls, >= {config.BOWLER_MIN_PRESSURE_BALLS} pressure balls)...")
    qual = bowl_df[
        (bowl_df['legal_balls_total'] >= config.BOWLER_MIN_TOTAL_BALLS) &
        (bowl_df['legal_balls_pressure'] >= config.BOWLER_MIN_PRESSURE_BALLS)
    ].copy()

    # Empirical Bayes Shrinkage
    mu_econ = qual['pressure_econ'].median()
    mu_wsr = qual['pressure_wsr'].median()

    qual['bayes_pressure_econ'] = (
        qual['legal_balls_pressure'] * qual['pressure_econ'] + config.BAYES_K_BOWLER * mu_econ
    ) / (qual['legal_balls_pressure'] + config.BAYES_K_BOWLER)

    qual['bayes_pressure_wsr'] = (
        qual['wickets_pressure'] * qual['pressure_wsr'] + config.BAYES_K_WICKETS * mu_wsr
    ) / (qual['wickets_pressure'] + config.BAYES_K_WICKETS)

    # Volume confidence factor
    qual['volume_weight'] = np.sqrt(
        qual['weighted_balls_pressure'] / (qual['weighted_balls_pressure'] + 100.0)
    )

    # Standardized components (inverted where lower is better)
    z_va = zscore(qual['va_per_ball_pressure'])
    z_econ = -zscore(qual['bayes_pressure_econ'])
    z_wsr = -zscore(np.log(qual['bayes_pressure_wsr']))
    z_delta = zscore(qual['delta_econ'])
    z_dot = zscore(qual['pressure_dot_pct'])

    # Composite Score:
    # 35% Value Added per ball (Runs saved + wickets relative to Par)
    # 25% Pressure Economy Rate (Shrunk)
    # 20% Wicket Strike Rate in Pressure
    # 10% Delta Economy (Tightening up compared to baseline)
    # 10% Dot Ball %
    raw_bowl_score = (0.35 * z_va + 0.25 * z_econ + 0.20 * z_wsr + 0.10 * z_delta + 0.10 * z_dot)
    qual['composite_score'] = raw_bowl_score * qual['volume_weight']

    # Normalize to 0-100 rating scale (mean 50, std 15)
    qual['pressure_rating'] = 50.0 + 15.0 * zscore(qual['composite_score'])

    ranked = qual.sort_values('pressure_rating', ascending=False).reset_index(drop=True)
    ranked['rank'] = range(1, len(ranked) + 1)
    return ranked
