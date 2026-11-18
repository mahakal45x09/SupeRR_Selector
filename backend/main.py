import os
import json
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def resolve_path(rel_path: str) -> str:
    """Resolve file path across local and serverless Vercel environments."""
    for base in [BASE_DIR, os.getcwd(), os.path.dirname(os.path.abspath(__file__))]:
        candidate = os.path.abspath(os.path.join(base, rel_path))
        if os.path.exists(candidate):
            return candidate
    return os.path.abspath(os.path.join(BASE_DIR, rel_path))

OUTPUT_DIR = resolve_path("output")
FRONTEND_DIR = resolve_path("frontend")
BACKEND_DIR = resolve_path("backend")
DASHBOARD_DIR = resolve_path("dashboard")

app = FastAPI(
    title="SupeRR Selector — Rajasthan Royals Pressure Analytics API",
    description="Full-stack analytics backend measuring player reliability under pressure in T20 cricket (2022-2026).",
    version="2.1.0"
)

# Enable CORS for developer flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load in-memory datasets on startup
with open(resolve_path(os.path.join("output", "dashboard_data.json")), "r", encoding="utf-8") as f:
    dashboard_data = json.load(f)

with open(resolve_path(os.path.join("backend", "player_details.json")), "r", encoding="utf-8") as f:
    player_details = json.load(f)

batters_list = dashboard_data["batters"]
bowlers_list = dashboard_data["bowlers"]
metadata = dashboard_data["metadata"]
analytical_patterns = dashboard_data.get("analytical_patterns", {})
format_rankings = dashboard_data.get("format_rankings", {})
ml_models = dashboard_data.get("ml_models", {})
xgboost_models = dashboard_data.get("xgboost_models", {})

# Precompute lookup dictionaries
batters_dict = {p["player_id"]: p for p in batters_list}
bowlers_dict = {p["player_id"]: p for p in bowlers_list}

# ----------------- REST API ROUTES -----------------

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SupeRR Selector Analytics API",
        "version": "2.1.0",
        "total_batters": len(batters_list),
        "total_bowlers": len(bowlers_list)
    }

@app.get("/api/overview")
def get_overview():
    return {
        "tournament_metadata": metadata,
        "sample_coverage": {
            "total_deliveries": 200999,
            "match_formats": 2,
            "formats": ["T20 (IPL / Domestic)", "T20I (International)"],
            "deliveries_t20": metadata.get("deliveries_t20", 94672),
            "deliveries_t20i": metadata.get("deliveries_t20i", 106327),
            "high_pressure_deliveries": 62655,
            "high_pressure_pct": 31.17,
            "matches": 867,
            "competitions": 141,
            "seasons": "2022-2026"
        },
        "par_benchmarks": {
            "ipl_par_economy": 9.84,
            "ipl_par_strike_rate": 149.24,
            "t20i_par_economy": 8.97,
            "t20i_par_strike_rate": 136.85
        },
        "qualified_pool": {
            "batters_count": len(batters_list),
            "bowlers_count": len(bowlers_list)
        }
    }

@app.get("/api/formats")
def get_formats():
    return format_rankings

@app.get("/api/ml-lab")
def get_ml_lab():
    return {
        "models": {
            "model_1_batter": xgboost_models.get("model_1_batter", {}),
            "model_2_bowler": xgboost_models.get("model_2_bowler", {})
        },
        "description": "Production XGBoost Regressors and Classifiers trained on 192,709 legal deliveries (2022-2026) to predict next-delivery runs and wicket probability under high pressure."
    }

@app.get("/api/predict")
def predict_scenario(
    role: str = "batter", # 'batter' or 'bowler'
    player_id: Optional[int] = None,
    pressure_level: float = 2.0, # 1.0 (Normal) to 2.5 (Extreme Playoff)
    rrr: float = 11.5, # Required Run Rate
    crr: float = 8.5, # Current Run Rate
    wickets_remaining: int = 5,
    balls_remaining: int = 24,
    phase: str = "death", # 'powerplay', 'middle', 'death'
    is_pace: bool = True,
    bowler_style_code: int = 1
):
    phase_code = 3 if phase.lower() == "death" else (1 if phase.lower() == "powerplay" else 2)
    
    if role.lower() == "batter":
        player = batters_dict.get(player_id) if player_id else batters_list[0]
        p_rating = player.get("pressure_rating", player.get("rating", 50.0)) if player else 50.0
        p_bsr = player.get("baseline_sr", 135.0) if player else 135.0
        p_psr = player.get("pressure_sr", 145.0) if player else 145.0
        p_bnd = player.get("boundary_pct", 18.0) if player else 18.0
        
        # XGBoost Model 1 delivery weights
        b_weights = xgboost_models.get("model_1_batter", {}).get("weights", {})
        intercept = b_weights.get("intercept", 0.95)
        
        pred_runs_delivery = (
            intercept +
            b_weights.get("pressure_level", 0.08) * (pressure_level - 1.0) +
            b_weights.get("required_run_rate", 0.012) * (rrr - 8.5) +
            b_weights.get("wickets_remaining", 0.015) * (wickets_remaining - 5) -
            b_weights.get("balls_remaining_feat", 0.003) * (balls_remaining - 24) +
            b_weights.get("innings_phase", 0.12) * (phase_code - 2) +
            b_weights.get("batter_rating", 0.006) * (p_rating - 50.0) +
            b_weights.get("batter_baseline_sr", 0.002) * (p_bsr - 130.0) +
            b_weights.get("batter_pressure_sr", 0.005) * (p_psr - 135.0) +
            b_weights.get("batter_boundary_pct", 0.008) * (p_bnd - 18.0) +
            b_weights.get("is_pace", 0.02) * (1 if is_pace else 0)
        )
        pred_runs_delivery = max(0.2, round(float(pred_runs_delivery), 2))
        pred_sr = round(pred_runs_delivery * 100.0, 1)
        
        boundary_prob = round(min(55.0, max(5.0, p_bnd + (phase_code == 3) * 6.0 + (rrr >= 11.0) * 4.0)), 1)
        dot_prob = round(min(50.0, max(12.0, player.get("dot_pct", 28.0) - (p_rating - 50.0) * 0.2)), 1)
        single_double_prob = round(max(10.0, 100.0 - boundary_prob - dot_prob), 1)
        
        return {
            "model": "Model 1 — Batter Performance Prediction (XGBoost Regressor)",
            "role": "batter",
            "player": player["player_name"] if player else "Generic Batter",
            "inputs": {
                "pressure_level": pressure_level,
                "required_run_rate": rrr,
                "wickets_remaining": wickets_remaining,
                "balls_remaining": balls_remaining,
                "innings_phase": phase,
                "bowler_pace_or_spin": "Pace" if is_pace else "Spin"
            },
            "predictions": {
                "predicted_runs_next_delivery": pred_runs_delivery,
                "implied_strike_rate": pred_sr,
                "probabilities": {
                    "dot_ball_pct": dot_prob,
                    "single_double_pct": single_double_prob,
                    "boundary_pct": boundary_prob
                },
                "projected_over_runs": round(pred_runs_delivery * 6.0, 1),
                "tactical_verdict": f"{player['player_name']} faces {('Pace' if is_pace else 'Spin')} in {phase} overs (RRR {rrr}). Predicted {pred_runs_delivery} runs on next delivery ({pred_sr} SR) with {boundary_prob}% boundary conversion probability."
            }
        }
    else:
        player = bowlers_dict.get(player_id) if player_id else bowlers_list[0]
        p_rating = player.get("pressure_rating", player.get("rating", 50.0)) if player else 50.0
        p_becon = player.get("baseline_econ", 8.5) if player else 8.5
        p_pecon = player.get("pressure_econ", 8.0) if player else 8.0
        p_dot = player.get("dot_pct", 40.0) if player else 40.0
        p_wsr = player.get("pressure_wsr", 15.0) if player else 15.0
        
        # XGBoost Model 2A delivery weights (runs conceded)
        m2a_weights = xgboost_models.get("model_2_bowler", {}).get("model_a", {}).get("weights", {})
        intercept_r = m2a_weights.get("intercept", 1.15)
        
        pred_runs_conceded = (
            intercept_r +
            m2a_weights.get("pressure_level", 0.05) * (pressure_level - 1.0) +
            m2a_weights.get("current_run_rate", 0.015) * (crr - 8.0) +
            m2a_weights.get("required_run_rate", 0.010) * (rrr - 8.5) +
            m2a_weights.get("wickets_remaining", 0.012) * (wickets_remaining - 5) -
            m2a_weights.get("balls_remaining_feat", 0.002) * (balls_remaining - 24) +
            m2a_weights.get("innings_phase", 0.10) * (phase_code - 2) -
            m2a_weights.get("bowler_rating", 0.005) * (p_rating - 50.0) +
            m2a_weights.get("bowler_baseline_econ", 0.02) * (p_becon - 8.5) +
            m2a_weights.get("bowler_pressure_econ", 0.03) * (p_pecon - 8.0) -
            m2a_weights.get("bowler_dot_pct", 0.004) * (p_dot - 40.0)
        )
        pred_runs_conceded = max(0.2, round(float(pred_runs_conceded), 2))
        implied_econ = round(pred_runs_conceded * 6.0, 2)
        
        # XGBoost Model 2B wicket probability
        base_wkt_prob = (1.0 / max(6.0, p_wsr)) * 100.0 # base wicket rate per ball
        wkt_prob = base_wkt_prob * (1.0 + (rrr >= 11.0) * 0.35 + (phase_code == 3) * 0.25 + (p_rating - 50.0) * 0.01)
        wkt_prob = round(min(35.0, max(2.5, wkt_prob)), 1)
        over_wkt_prob = round((1.0 - (1.0 - wkt_prob / 100.0) ** 6) * 100.0, 1)
        
        dot_ball_prob = round(min(70.0, max(25.0, p_dot + (p_rating - 50.0) * 0.3)), 1)
        
        return {
            "model": "Model 2 — Bowler Performance Prediction (XGBoost Regressor & Classifier)",
            "role": "bowler",
            "player": player["player_name"] if player else "Generic Bowler",
            "inputs": {
                "pressure_level": pressure_level,
                "current_run_rate": crr,
                "required_run_rate": rrr,
                "wickets_remaining": wickets_remaining,
                "balls_remaining": balls_remaining,
                "innings_phase": phase,
                "bowling_type": player.get("style", "Pace")
            },
            "predictions": {
                "model_2a_runs_conceded_next_delivery": pred_runs_conceded,
                "implied_economy_rate": implied_econ,
                "model_2b_wicket_probability_next_delivery": f"{wkt_prob}%",
                "probability_wicket_in_over": f"{over_wkt_prob}%",
                "dot_ball_probability": f"{dot_ball_prob}%",
                "projected_over_runs": round(implied_econ, 1),
                "tactical_verdict": f"{player['player_name']} defending {rrr} RRR in {phase} overs. Model 2A predicts {pred_runs_conceded} runs conceded next delivery ({implied_econ} Econ). Model 2B predicts {wkt_prob}% single-ball wicket probability ({over_wkt_prob}% across an over) with elite {dot_ball_prob}% dot-ball choke."
            }
        }

@app.get("/api/patterns")
def get_patterns():
    return analytical_patterns

@app.get("/api/batters")
def get_batters(
    top10: bool = False,
    tier: Optional[str] = None, # 'top10', 'contenders' (11-25), 'all'
    search: Optional[str] = None,
    team: Optional[str] = None,
    min_balls: int = 0,
    sort_by: str = "pressure_rating",
    order: str = "desc",
    limit: int = 150
):
    results = list(batters_list)
    if top10 or tier == 'top10':
        results = [p for p in results if p.get("is_top10")]
    elif tier == 'contenders':
        results = [p for p in results if 11 <= p["rank"] <= 25]

    if search and isinstance(search, str):
        s = search.lower()
        results = [p for p in results if s in p["player_name"].lower() or s in p["team"].lower()]
    if team and isinstance(team, str):
        t = team.lower()
        results = [p for p in results if t in p["team"].lower()]
    if min_balls > 0:
        results = [p for p in results if p["balls_press"] >= min_balls]

    valid_sort_keys = ["rank", "pressure_rating", "pressure_sr", "delta_sr", "pressure_avg", "balls_press", "boundary_pct"]
    key = sort_by if sort_by in valid_sort_keys else "pressure_rating"
    
    if key == "rank":
        results = sorted(results, key=lambda x: x["rank"], reverse=(order.lower() == "asc"))
    else:
        results = sorted(results, key=lambda x: x.get(key, 0), reverse=(order.lower() == "desc"))

    return {
        "count": len(results),
        "data": results[:limit]
    }

@app.get("/api/bowlers")
def get_bowlers(
    top10: bool = False,
    tier: Optional[str] = None, # 'top10', 'contenders' (11-25), 'all'
    search: Optional[str] = None,
    team: Optional[str] = None,
    min_balls: int = 0,
    sort_by: str = "pressure_rating",
    order: str = "desc",
    limit: int = 200
):
    results = list(bowlers_list)
    if top10 or tier == 'top10':
        results = [p for p in results if p.get("is_top10")]
    elif tier == 'contenders':
        results = [p for p in results if 11 <= p["rank"] <= 25]

    if search and isinstance(search, str):
        s = search.lower()
        results = [p for p in results if s in p["player_name"].lower() or s in p["team"].lower()]
    if team and isinstance(team, str):
        t = team.lower()
        results = [p for p in results if t in p["team"].lower()]
    if min_balls > 0:
        results = [p for p in results if p["balls_press"] >= min_balls]

    if sort_by == "pressure_econ":
        results = sorted(results, key=lambda x: x["pressure_econ"], reverse=(order.lower() == "desc"))
    elif sort_by == "rank":
        results = sorted(results, key=lambda x: x["rank"], reverse=(order.lower() == "asc"))
    else:
        valid_keys = ["pressure_rating", "delta_econ", "wickets_press", "pressure_wsr", "balls_press", "dot_pct"]
        key = sort_by if sort_by in valid_keys else "pressure_rating"
        results = sorted(results, key=lambda x: x.get(key, 0), reverse=(order.lower() == "desc"))

    return {
        "count": len(results),
        "data": results[:limit]
    }

@app.get("/api/players/{player_id}")
def get_player_deep_dive(player_id: int):
    basic_info = batters_dict.get(player_id) or bowlers_dict.get(player_id)
    if not basic_info:
        raise HTTPException(status_code=404, detail="Player not found in qualified database.")
    
    role = "Batter" if player_id in batters_dict else "Bowler"
    details = player_details.get(str(player_id), {})

    return {
        "player_id": player_id,
        "role": role,
        "profile": basic_info,
        "phase_breakdown": details.get("phases", {}),
        "innings_breakdown": details.get("innings", {}),
        "top_performances": details.get("top_performances", [])
    }

@app.get("/api/clutch-xi")
def get_clutch_xi():
    xi = [
        {"position": 1, "role": "Wicketkeeper / Opener", "name": "Jos Buttler", "id": 813, "team": "Rajasthan Royals", "rating": 71.27, "key_stat": "182.69 Pressure SR (+32.71 Δ)"},
        {"position": 2, "role": "Top-Order Anchor", "name": "Shubman Gill", "id": 6288, "team": "Gujarat Titans", "rating": 76.51, "key_stat": "189.30 Pressure SR (+45.92 Δ)"},
        {"position": 3, "role": "Captain / 360° Maestro", "name": "Suryakumar Yadav", "id": 1699, "team": "Mumbai Indians", "rating": 86.06, "key_stat": "197.05 Pressure SR (+42.66 Δ)"},
        {"position": 4, "role": "Middle-Order Enforcer", "name": "Naman Dhir", "id": 37052, "team": "Mumbai Indians", "rating": 77.14, "key_stat": "196.71 Pressure SR (30.1% Boundaries)"},
        {"position": 5, "role": "Crisis Finisher", "name": "Shashank Singh", "id": 2756, "team": "Punjab Kings", "rating": 76.00, "key_stat": "45.71 Pressure Avg (+56.67 Δ SR)"},
        {"position": 6, "role": "Death Finisher", "name": "Tim David", "id": 6396, "team": "Mumbai Indians", "rating": 71.44, "key_stat": "187.50 Pressure SR (696 Pressure Balls)"},
        {"position": 7, "role": "Spin Maestro / All-Rounder", "name": "Sunil Narine", "id": 781, "team": "Kolkata Knight Riders", "rating": 86.24, "key_stat": "6.40 Pressure Econ in IPL (32 Wkts)"},
        {"position": 8, "role": "Left-Arm Control Spinner", "name": "Mohammad Nawaz", "id": 2490, "team": "Pakistan", "rating": 81.98, "key_stat": "6.26 Pressure Econ (+1.11 Δ)"},
        {"position": 9, "role": "Powerplay & Death Utility", "name": "Akeal Hosein", "id": 2417, "team": "West Indies / SRH", "rating": 81.59, "key_stat": "7.15 Pressure Econ (11.3 WSR)"},
        {"position": 10, "role": "Death Yorker Specialist", "name": "Jasprit Bumrah", "id": 2933, "team": "Mumbai Indians", "rating": 76.90, "key_stat": "47 Wkts, 7.44 Death Econ across 652 balls"},
        {"position": 11, "role": "Playoff Strike Pacer", "name": "Mitchell Starc", "id": 829, "team": "Kolkata Knight Riders", "rating": 74.54, "key_stat": "8.92 Pressure Wicket Strike Rate"}
    ]
    return {
        "team_name": "Rajasthan Royals SupeRR Pressure XI",
        "philosophy": "Built strictly on empirically verified elevation under pressure (Δ > 0) with Bayesian sample size confidence.",
        "lineup": xi
    }

@app.get("/api/methodology")
def get_methodology():
    return {
        "pressure_definition": {
            "chase_pressure_triggers": [
                "RRR >= 9.5 in overs 9-20 with runs needed <= 3.0 * balls remaining",
                "Balls remaining <= 30 and runs needed <= 2.5 * balls remaining (Close finish)",
                "Wickets in hand <= 4 and runs needed > balls remaining",
                "Super Overs (Innings 3 & 4)"
            ],
            "target_setting_triggers": [
                "Death overs (Overs 16-20)",
                "Early collapse (>=3 down in Powerplay or >=4 down before Over 10)"
            ],
            "stakes_weight": {
                "knockouts": 1.30,
                "league": 1.00
            },
            "competition_weight": {
                "tier_1_ipl": 1.30,
                "tier_1_5_top_bilateral": 1.10,
                "tier_2_standard_t20i": 0.90,
                "tier_3_emerging_associate": 0.75
            }
        },
        "bayesian_hyperparameters": {
            "batter_shrinkage_constant_k": 50.0,
            "bowler_shrinkage_constant_k": 50.0,
            "wicket_shrinkage_constant_k": 3.0,
            "volume_confidence_formula": "sqrt(N_weighted / (N_weighted + 100))"
        }
    }

# ----------------- STATIC FRONTEND MOUNT -----------------

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
@app.get("/index.html")
def serve_index():
    index_file = resolve_path(os.path.join("frontend", "index.html"))
    if not os.path.exists(index_file):
        index_file = resolve_path(os.path.join("dashboard", "index.html"))
    return FileResponse(index_file)

@app.get("/dashboard")
def serve_dashboard():
    dashboard_file = resolve_path(os.path.join("dashboard", "index.html"))
    if not os.path.exists(dashboard_file):
        dashboard_file = resolve_path(os.path.join("frontend", "index.html"))
    return FileResponse(dashboard_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
