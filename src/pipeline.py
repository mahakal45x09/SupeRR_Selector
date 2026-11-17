import os
import pandas as pd
from . import config
from .state_engine import load_and_enrich_data
from .pressure_model import apply_pressure_classification
from .metrics import aggregate_batting_metrics, aggregate_bowling_metrics
from .bayesian_model import compute_batting_rankings, compute_bowling_rankings

def run_pipeline():
    """
    Executes the entire Rajasthan Royals SupeRR Selector analytics pipeline.
    """
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    print("=" * 70)
    print("  Rajasthan Royals SupeRR Selector Season 2 — Analytics Pipeline")
    print("=" * 70)

    # 1. State Engine
    df = load_and_enrich_data()

    # 2. Pressure Model
    df = apply_pressure_classification(df)

    # 3. Aggregations
    bat_agg = aggregate_batting_metrics(df)
    bowl_agg = aggregate_bowling_metrics(df)

    # 4. Bayesian Models & Composite Scoring
    bat_ranked = compute_batting_rankings(bat_agg)
    bowl_ranked = compute_bowling_rankings(bowl_agg)

    # 5. Extract Top 10 Lists
    top_10_batters = bat_ranked.head(10)[[
        'rank', 'player_id', 'player_name', 'balls_faced_total', 'balls_faced_pressure',
        'baseline_sr', 'pressure_sr', 'delta_sr', 'baseline_avg', 'pressure_avg',
        'pressure_boundary_pct', 'pressure_dot_pct', 'pressure_rating'
    ]]

    top_10_bowlers = bowl_ranked.head(10)[[
        'rank', 'player_id', 'player_name', 'legal_balls_total', 'legal_balls_pressure',
        'baseline_econ', 'pressure_econ', 'delta_econ', 'wickets_pressure', 'pressure_wsr',
        'pressure_dot_pct', 'pressure_boundary_pct', 'pressure_rating'
    ]]

    # 6. Export Results
    print(f"\nExporting results to: {config.OUTPUT_DIR}")
    top_10_batters.round(2).to_csv(config.TOP_10_BATTERS_CSV, index=False)
    top_10_bowlers.round(2).to_csv(config.TOP_10_BOWLERS_CSV, index=False)
    bat_ranked.round(2).to_csv(config.ALL_BATTERS_CSV, index=False)
    bowl_ranked.round(2).to_csv(config.ALL_BOWLERS_CSV, index=False)

    print("\n" + "=" * 70)
    print("  FINAL TOP 10 BATTERS UNDER PRESSURE (Selected on Unstop)")
    print("=" * 70)
    print(top_10_batters.round(2).to_string(index=False))

    print("\n" + "=" * 70)
    print("  FINAL TOP 10 BOWLERS UNDER PRESSURE (Selected on Unstop)")
    print("=" * 70)
    print(top_10_bowlers.round(2).to_string(index=False))
    print("\nPipeline execution complete! CSV files generated in output/ directory.")

if __name__ == '__main__':
    run_pipeline()
