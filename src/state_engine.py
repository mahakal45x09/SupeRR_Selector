import os
import numpy as np
import pandas as pd
from . import config

def get_comp_tier_info(comp_name: str):
    """
    Categorizes each competition into tiers with associated leverage weights:
    - Tier 1: IPL (Highest concentration of global talent & 10.0+ death par economy)
    - Tier 1.5: Top Bilaterals & Asia Cup (India, Australia, England, SA, Pak, NZ, WI)
    - Tier 2: Standard T20I matches
    - Tier 3: Emerging teams, Associate Tri-series, and Qualifiers
    """
    c = str(comp_name).lower()
    if 'ipl' in c or 'indian premier league' in c:
        return config.TIER_IPL_WEIGHT, 'Tier 1 (IPL)'
    if any(k in c for k in ['emerging', 'rising stars', 'qualifier', 'tri-nation', 'tri series']):
        return config.TIER_EMERGING_ASSOCIATE_WEIGHT, 'Tier 3 (Emerging/Associate)'
    
    top_teams = ['india', 'australia', 'england', 'south africa', 'pakistan', 'new zealand', 'west indies']
    top_count = sum(team in c for team in top_teams)
    if 'asia cup' in c or top_count >= 2:
        return config.TIER_TOP_BILATERAL_WEIGHT, 'Tier 1.5 (Top Bilateral / Asia Cup)'
    
    return config.TIER_STANDARD_T20I_WEIGHT, 'Tier 2 (Standard T20I)'


def load_and_enrich_data():
    """
    Loads ball_by_ball, matches, and competitions data, then builds the
    cumulative dynamic match state for every single delivery.
    """
    print("Loading raw dataset files...")
    bbb = pd.read_csv(config.BBB_PATH)
    matches = pd.read_csv(config.MATCHES_PATH)
    comps = pd.read_csv(config.COMPS_PATH)

    # Classify competition tiers
    tier_info = comps['comp_name'].apply(get_comp_tier_info)
    comps['comp_weight'] = [t[0] for t in tier_info]
    comps['comp_tier'] = [t[1] for t in tier_info]

    # Merge matches with competition info
    m_info = matches[[
        'match_id', 'comp_id', 'stage', 'knock_out',
        'first_inn_revised_overs', 'second_inn_revised_overs',
        'revised_target', 'win_team_id'
    ]].copy()
    m_info = m_info.merge(
        comps[['comp_id', 'comp_name', 'match_format', 'season', 'comp_weight', 'comp_tier']],
        on='comp_id', how='left'
    )

    # Delivery-level indicators
    bbb['total_ball_runs'] = bbb['runs'] + bbb['extras1_runs'] + bbb['extras_2_runs']
    bbb['is_legal_ball'] = ~bbb['extras_type'].isin(['wide', 'Overstep'])
    bbb['is_bowler_run'] = bbb['runs'] + np.where(
        bbb['extras_type'].isin(['wide', 'Overstep']), bbb['extras1_runs'], 0
    )
    bbb['is_bowler_wicket'] = bbb['is_wicket'] & bbb['dismissal_type'].isin(
        ['Bowled', 'Caught', 'LBW', 'Stump', 'Hit Wicket']
    )

    # Batter dismissal indicator (excluding run outs and non-striker outs)
    bbb['is_striker_out'] = bbb['is_wicket'] & (bbb['dismissed_player_id'] == bbb['striker_id'])
    bbb['is_striker_out'] = bbb['is_striker_out'] | (
        bbb['is_wicket'] & bbb['dismissed_player_id'].isnull() & (bbb['dismissal_type'] != 'RunOut')
    )

    # Calculate 1st innings total runs per match
    inn1_totals = bbb[bbb['innings'] == 1].groupby('match_id')['total_ball_runs'].sum().reset_index(name='inn1_total')
    m_info = m_info.merge(inn1_totals, on='match_id', how='left')

    # Determine chase targets (DLS revised target if present, else inn1_total + 1)
    m_info['target'] = np.where(
        m_info['revised_target'].notnull() & (m_info['revised_target'] > 0),
        m_info['revised_target'],
        m_info['inn1_total'] + 1
    )

    bbb = bbb.merge(m_info, on='match_id', how='left')

    # Cumulative running state before each delivery
    bbb['cur_runs'] = bbb.groupby(['match_id', 'innings'])['total_ball_runs'].cumsum() - bbb['total_ball_runs']
    bbb['cur_wickets'] = bbb.groupby(['match_id', 'innings'])['is_wicket'].cumsum() - bbb['is_wicket'].astype(int)
    bbb['cur_legal_balls'] = bbb.groupby(['match_id', 'innings'])['is_legal_ball'].cumsum() - bbb['is_legal_ball'].astype(int)

    # Determine maximum balls allocated per innings (revised_overs stores legal balls, 120 standard)
    bbb['max_balls'] = 120
    bbb.loc[(bbb['innings'] == 1) & (bbb['first_inn_revised_overs'].notnull()), 'max_balls'] = bbb['first_inn_revised_overs']
    bbb.loc[(bbb['innings'] == 2) & (bbb['second_inn_revised_overs'].notnull()), 'max_balls'] = bbb['second_inn_revised_overs']

    bbb['balls_remaining'] = np.maximum(0, bbb['max_balls'] - bbb['cur_legal_balls'])
    bbb['wickets_in_hand'] = 10 - bbb['cur_wickets']

    # Runs needed and RRR for 2nd innings chases
    bbb['runs_needed'] = np.where(bbb['innings'] == 2, np.maximum(0, bbb['target'] - bbb['cur_runs']), np.nan)
    bbb['rrr'] = np.where(
        (bbb['innings'] == 2) & (bbb['balls_remaining'] > 0),
        (bbb['runs_needed'] * 6.0) / bbb['balls_remaining'],
        np.where((bbb['innings'] == 2) & (bbb['runs_needed'] <= 0), 0.0, 36.0)
    )

    print(f"Dataset successfully enriched: {len(bbb)} deliveries across {bbb['match_id'].nunique()} matches.")
    return bbb
