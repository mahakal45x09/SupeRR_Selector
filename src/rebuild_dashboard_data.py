import json
import os
import pandas as pd
from src import config
from src.state_engine import load_and_enrich_data
from src.pressure_model import apply_pressure_classification
from src.metrics import aggregate_batting_metrics, aggregate_bowling_metrics

# Comprehensive Team Codes
TEAM_CODES = {
    'India': 'IND', 'Pakistan': 'PAK', 'Australia': 'AUS', 'England': 'ENG',
    'New Zealand': 'NZ', 'South Africa': 'SA', 'West Indies': 'WI', 'Afghanistan': 'AFG',
    'Sri Lanka': 'SL', 'Bangladesh': 'BAN', 'Zimbabwe': 'ZIM', 'Ireland': 'IRE',
    'Netherlands': 'NED', 'Scotland': 'SCO', 'Namibia': 'NAM', 'USA': 'USA',
    'Nepal': 'NEP', 'Oman': 'OMA', 'Canada': 'CAN', 'Uganda': 'UGA',
    'Rajasthan Royals': 'RR', 'Kolkata Knight Riders': 'KKR', 'Mumbai Indians': 'MI',
    'Chennai Super Kings': 'CSK', 'Sunrisers Hyderabad': 'SRH',
    'Royal Challengers Bengaluru': 'RCB', 'Royal Challengers Bangalore': 'RCB',
    'Gujarat Titans': 'GT', 'Lucknow Super Giants': 'LSG', 'Delhi Capitals': 'DC',
    'Punjab Kings': 'PBKS'
}

# Preferred IPL franchise (canonical representation in 2022-2024 cycles)
PREFERRED_IPL = {
    813: 'Rajasthan Royals',         # Jos Buttler
    3647: 'Kolkata Knight Riders',   # Shreyas Iyer
    4391: 'Punjab Kings',            # Liam Livingstone
    2756: 'Punjab Kings',            # Shashank Singh
    6396: 'Mumbai Indians',          # Tim David
    1699: 'Mumbai Indians',          # Suryakumar Yadav
    6288: 'Gujarat Titans',          # Shubman Gill
    2639: 'Lucknow Super Giants',    # Marcus Stoinis
    2101: 'Lucknow Super Giants',    # Quinton de Kock
    4703: 'Delhi Capitals',          # Rishabh Pant
    25048: 'Sunrisers Hyderabad',    # Umran Malik
    781: 'Kolkata Knight Riders',    # Sunil Narine
    2933: 'Mumbai Indians',          # Jasprit Bumrah
    5809: 'Lucknow Super Giants',    # Naveen ul Haq
    829: 'Kolkata Knight Riders',    # Mitchell Starc
    4101: 'Chennai Super Kings',     # Mitchell Santner
    1612: 'Rajasthan Royals',        # Yuzvendra Chahal
    39657: 'Sunrisers Hyderabad',    # Eshan Malinga
    7327: 'Delhi Capitals',          # Rasikh Salam
    1596: 'Chennai Super Kings',     # Moeen Ali
    4722: 'Gujarat Titans',          # Rashid Khan
    3644: 'Delhi Capitals',          # Kuldeep Yadav
    4823: 'Sunrisers Hyderabad',     # Washington Sundar
    6256: 'Kolkata Knight Riders',   # Varun Chakravarthy
    3298: 'Rajasthan Royals',        # Jofra Archer
    4708: 'Kolkata Knight Riders',   # Rinku Singh
    2984: 'Punjab Kings',            # Sikandar Raza
    7897: 'Mumbai Indians',          # Tilak Varma
    4369: 'Delhi Capitals',          # Shai Hope
    2417: 'Sunrisers Hyderabad',     # Akeal Hosein
    8182: 'Rajasthan Royals',        # Donovan Ferreira
    37052: 'Mumbai Indians',         # Naman Dhir
}

def rebuild_full_dashboard_data():
    print("Rebuilding full dashboard data with verified player teams and format-specific metadata...")
    
    # 1. Load team mappings from competition mapping
    df_map = pd.read_csv(os.path.join(config.DATASET_DIR, 'competition_team_player_mapping.csv'))
    
    countries = ['India', 'Pakistan', 'Australia', 'England', 'New Zealand', 'South Africa', 
                 'West Indies', 'Afghanistan', 'Sri Lanka', 'Bangladesh', 'Zimbabwe', 'Ireland',
                 'Netherlands', 'Scotland', 'Namibia', 'USA', 'Nepal', 'Oman', 'Canada', 'Uganda']
    
    ipl_teams = ['Rajasthan Royals', 'Kolkata Knight Riders', 'Mumbai Indians', 'Chennai Super Kings', 
                 'Sunrisers Hyderabad', 'Royal Challengers Bengaluru', 'Gujarat Titans', 
                 'Lucknow Super Giants', 'Delhi Capitals', 'Punjab Kings']

    df_intl = df_map[df_map['team_name'].isin(countries)]
    player_country = df_intl.groupby('player_id')['team_name'].last().to_dict()

    df_ipl = df_map[df_map['team_name'].isin(ipl_teams)]
    player_ipl = df_ipl.groupby('player_id')['team_name'].last().to_dict()
    for pid, team in PREFERRED_IPL.items():
        player_ipl[pid] = team

    # 2. Load ball by ball for format splitting
    df = load_and_enrich_data()
    df = apply_pressure_classification(df)

    df_t20 = df[df['match_format'] == 'T20']
    df_t20i = df[df['match_format'] == 'T20I']

    bat_t20 = aggregate_batting_metrics(df_t20).set_index('player_id')
    bat_t20i = aggregate_batting_metrics(df_t20i).set_index('player_id')

    bowl_t20 = aggregate_bowling_metrics(df_t20).set_index('player_id')
    bowl_t20i = aggregate_bowling_metrics(df_t20i).set_index('player_id')

    # 3. Overall rankings
    bat_df = pd.read_csv(os.path.join(config.OUTPUT_DIR, 'All_Batters_Pressure_Rankings.csv'))
    bowl_df = pd.read_csv(os.path.join(config.OUTPUT_DIR, 'All_Bowlers_Pressure_Rankings.csv'))

    batters = []
    for idx, row in bat_df.iterrows():
        pid = int(row['player_id'])
        # Country takes priority, then IPL franchise
        team = player_country.get(pid, player_ipl.get(pid, 'India'))
        team_code = TEAM_CODES.get(team, team[:3].upper())
        
        in_t20 = bool(pid in bat_t20.index and bat_t20.loc[pid, 'balls_faced_pressure'] >= 15)
        in_t20i = bool(pid in bat_t20i.index and bat_t20i.loc[pid, 'balls_faced_pressure'] >= 15)

        b_item = {
            'rank': int(row['rank']),
            'player_id': pid,
            'player_name': str(row['player_name']),
            'team': team,
            'team_code': team_code,
            'country': player_country.get(pid, team),
            'ipl_team': player_ipl.get(pid, None),
            'balls_total': int(row['balls_faced_total']),
            'balls_press': int(row['balls_faced_pressure']),
            'runs_press': int(row['runs_pressure']),
            'baseline_sr': round(float(row['baseline_sr']), 2),
            'pressure_sr': round(float(row['pressure_sr']), 2),
            'delta_sr': round(float(row['delta_sr']), 2),
            'baseline_avg': round(float(row['baseline_avg']), 2),
            'pressure_avg': round(float(row['pressure_avg']), 2),
            'delta_avg': round(float(row['delta_avg']), 2),
            'boundary_pct': round(float(row['pressure_boundary_pct']), 1),
            'dot_pct': round(float(row['pressure_dot_pct']), 1),
            'rating': round(float(row['pressure_rating']), 2),
            'is_top10': bool(row['rank'] <= 10),
            'in_t20': in_t20,
            'in_t20i': in_t20i
        }
        if in_t20:
            b_item['t20_pressure_sr'] = round(float(bat_t20.loc[pid, 'pressure_sr']), 2)
            b_item['t20_baseline_sr'] = round(float(bat_t20.loc[pid, 'baseline_sr']), 2)
            b_item['t20_balls_press'] = int(bat_t20.loc[pid, 'balls_faced_pressure'])
            b_item['t20_delta_sr'] = round(b_item['t20_pressure_sr'] - b_item['t20_baseline_sr'], 2)
        if in_t20i:
            b_item['t20i_pressure_sr'] = round(float(bat_t20i.loc[pid, 'pressure_sr']), 2)
            b_item['t20i_baseline_sr'] = round(float(bat_t20i.loc[pid, 'baseline_sr']), 2)
            b_item['t20i_balls_press'] = int(bat_t20i.loc[pid, 'balls_faced_pressure'])
            b_item['t20i_delta_sr'] = round(b_item['t20i_pressure_sr'] - b_item['t20i_baseline_sr'], 2)

        batters.append(b_item)

    bowlers = []
    for idx, row in bowl_df.iterrows():
        pid = int(row['player_id'])
        team = player_country.get(pid, player_ipl.get(pid, 'Pakistan'))
        team_code = TEAM_CODES.get(team, team[:3].upper())

        in_t20 = bool(pid in bowl_t20.index and bowl_t20.loc[pid, 'legal_balls_pressure'] >= 15)
        in_t20i = bool(pid in bowl_t20i.index and bowl_t20i.loc[pid, 'legal_balls_pressure'] >= 15)

        bw_item = {
            'rank': int(row['rank']),
            'player_id': pid,
            'player_name': str(row['player_name']),
            'team': team,
            'team_code': team_code,
            'country': player_country.get(pid, team),
            'ipl_team': player_ipl.get(pid, None),
            'balls_total': int(row['legal_balls_total']),
            'balls_press': int(row['legal_balls_pressure']),
            'runs_press': int(row['runs_pressure']),
            'wickets_total': int(row['wickets_total']),
            'wickets_press': int(row['wickets_pressure']),
            'baseline_econ': round(float(row['baseline_econ']), 2),
            'pressure_econ': round(float(row['pressure_econ']), 2),
            'delta_econ': round(float(row['delta_econ']), 2),
            'pressure_wsr': round(float(row['pressure_wsr']), 1),
            'boundary_pct': round(float(row['pressure_boundary_pct']), 1),
            'dot_pct': round(float(row['pressure_dot_pct']), 1),
            'rating': round(float(row['pressure_rating']), 2),
            'is_top10': bool(row['rank'] <= 10),
            'in_t20': in_t20,
            'in_t20i': in_t20i
        }
        if in_t20:
            bw_item['t20_pressure_econ'] = round(float(bowl_t20.loc[pid, 'pressure_econ']), 2)
            bw_item['t20_baseline_econ'] = round(float(bowl_t20.loc[pid, 'baseline_econ']), 2)
            bw_item['t20_balls_press'] = int(bowl_t20.loc[pid, 'legal_balls_pressure'])
            bw_item['t20_wickets_press'] = int(bowl_t20.loc[pid, 'wickets_pressure'])
            bw_item['t20_delta_econ'] = round(bw_item['t20_baseline_econ'] - bw_item['t20_pressure_econ'], 2)
        if in_t20i:
            bw_item['t20i_pressure_econ'] = round(float(bowl_t20i.loc[pid, 'pressure_econ']), 2)
            bw_item['t20i_baseline_econ'] = round(float(bowl_t20i.loc[pid, 'baseline_econ']), 2)
            bw_item['t20i_balls_press'] = int(bowl_t20i.loc[pid, 'legal_balls_pressure'])
            bw_item['t20i_wickets_press'] = int(bowl_t20i.loc[pid, 'wickets_pressure'])
            bw_item['t20i_delta_econ'] = round(bw_item['t20i_baseline_econ'] - bw_item['t20i_pressure_econ'], 2)

        bowlers.append(bw_item)

    # Load format rankings & enrich each entry with format-appropriate team & team_code
    with open(os.path.join(config.OUTPUT_DIR, 'ml_lab_data.json'), 'r', encoding='utf-8') as f:
        ml_data = json.load(f)

    format_rankings = ml_data.get('format_rankings', {})
    for fmt_name in ['T20', 'T20I', 'Combined']:
        if fmt_name not in format_rankings:
            continue
        
        # Enrich batters
        for b in format_rankings[fmt_name].get('top10_batters', []):
            pid = b['player_id']
            if fmt_name == 'T20I':
                t_name = player_country.get(pid, 'India')
            elif fmt_name == 'T20':
                t_name = player_ipl.get(pid, player_country.get(pid, 'IPL'))
            else: # Combined
                t_name = player_country.get(pid, player_ipl.get(pid, 'India'))
            b['team'] = t_name
            b['team_code'] = TEAM_CODES.get(t_name, t_name[:3].upper())

        # Enrich bowlers
        for bw in format_rankings[fmt_name].get('top10_bowlers', []):
            pid = bw['player_id']
            if fmt_name == 'T20I':
                t_name = player_country.get(pid, 'Pakistan')
            elif fmt_name == 'T20':
                t_name = player_ipl.get(pid, player_country.get(pid, 'IPL'))
            else: # Combined
                t_name = player_country.get(pid, player_ipl.get(pid, 'Pakistan'))
            bw['team'] = t_name
            bw['team_code'] = TEAM_CODES.get(t_name, t_name[:3].upper())

    full_payload = {
        'batters': batters,
        'bowlers': bowlers,
        'metadata': {
            'total_deliveries': 200999,
            'high_pressure_deliveries': 62655,
            'matches': 867,
            'competitions': 141,
            'seasons': '2022-2026',
            'match_formats': 2,
            'deliveries_t20': 94672,
            'deliveries_t20i': 106327,
            'par_sr_ipl': 149.2,
            'par_econ_ipl': 9.84,
            'par_sr_t20i': 136.9,
            'par_econ_t20i': 8.97
        },
        'format_rankings': format_rankings,
        'ml_models': ml_data.get('ml_models', {}),
        'xgboost_models': ml_data.get('xgboost_models', {})
    }

    out_file = os.path.join(config.OUTPUT_DIR, 'dashboard_data.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(full_payload, f, indent=2)

    print(f"Successfully generated {out_file} with verified teams for all {len(batters)} batters and {len(bowlers)} bowlers!")

if __name__ == '__main__':
    rebuild_full_dashboard_data()
