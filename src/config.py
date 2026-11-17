import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(BASE_DIR, "Dataset")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Dataset File Paths
BBB_PATH = os.path.join(DATASET_DIR, "ball_by_ball.csv")
MATCHES_PATH = os.path.join(DATASET_DIR, "matches.csv")
COMPS_PATH = os.path.join(DATASET_DIR, "competitions.csv")
MAPPING_PATH = os.path.join(DATASET_DIR, "competition_team_player_mapping.csv")
P11_PATH = os.path.join(DATASET_DIR, "playing_eleven.csv")
TEAMS_PATH = os.path.join(DATASET_DIR, "teams.csv")

# Output File Paths
TOP_10_BATTERS_CSV = os.path.join(OUTPUT_DIR, "Top_10_Batters_Under_Pressure.csv")
TOP_10_BOWLERS_CSV = os.path.join(OUTPUT_DIR, "Top_10_Bowlers_Under_Pressure.csv")
ALL_BATTERS_CSV = os.path.join(OUTPUT_DIR, "All_Batters_Pressure_Rankings.csv")
ALL_BOWLERS_CSV = os.path.join(OUTPUT_DIR, "All_Bowlers_Pressure_Rankings.csv")

# Sample Size Qualification Thresholds
BATTER_MIN_TOTAL_BALLS = 300
BATTER_MIN_PRESSURE_BALLS = 100

BOWLER_MIN_TOTAL_BALLS = 300
BOWLER_MIN_PRESSURE_BALLS = 100

# Bayesian Shrinkage Hyperparameters
BAYES_K_BATTER = 50.0   # Effective pseudo-balls for prior shrinkage
BAYES_K_BOWLER = 50.0   # Effective pseudo-balls for prior shrinkage
BAYES_K_WICKETS = 3.0   # Effective pseudo-wickets for strike rate shrinkage

# Stakes & Competition Weights
KNOCKOUT_STAGE_WEIGHT = 1.30
LEAGUE_STAGE_WEIGHT = 1.00

TIER_IPL_WEIGHT = 1.30
TIER_TOP_BILATERAL_WEIGHT = 1.10
TIER_STANDARD_T20I_WEIGHT = 0.90
TIER_EMERGING_ASSOCIATE_WEIGHT = 0.75

# Wicket Run Equivalent in Pressure Phases
WICKET_RUN_VALUE = 15.0
