# Rajasthan Royals — SupeRR Selector Season 2 (Round 1)
## Match Leverage & Reliability Analytics Engine (2022–2026)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat&logo=python)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.0+-EB5424.svg?style=flat&logo=xgboost)](https://xgboost.readthedocs.io/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4+-FF6384.svg?style=flat&logo=chart.js)](https://www.chartjs.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com/)

---

## 📌 Executive Overview

In modern T20 cricket, traditional cumulative metrics (such as raw averages and overall strike rates) routinely obscure the most vital asset in tournament play: **reliability under extreme match pressure**.

Developed for **Rajasthan Royals SupeRR Selector Season 2 (Round 1)**, this platform is an end-to-end full-stack analytics engine and machine learning simulation suite built across **200,999 legal deliveries** spanning **867 matches** and **141 competitions** (2022–2026). The system isolates **62,655 high-pressure deliveries (31.17%)**, evaluates each player's performance against their own **baseline levels ($\Delta$-differential)**, controls for **match leverage** and **competition tier**, applies **Empirical Bayes shrinkage** to eliminate small-sample noise, and deploys **dual XGBoost delivery-level predictive models** for in-game decision simulation.

---

## ⚡ Quickstart: Launching the Platform

### 1. Prerequisites & Environment Setup
Clone the repository and install dependencies:
```bash
git clone https://github.com/YourOrg/SupeRR_Selectors.git
cd SupeRR_Selectors
pip install -r requirements.txt
```

### 2. Start Full-Stack Web Application
Run the unified server launcher:
```bash
python start_server.py
```
Open your browser at:
```
http://127.0.0.1:8000
```
- **Web Dashboard**: `http://127.0.0.1:8000/`
- **Interactive API Docs (Swagger UI)**: `http://127.0.0.1:8000/docs`
- **Alternative Redoc API**: `http://127.0.0.1:8000/redoc`

---

## 📁 Repository Structure

```
B:\SupeRR_Selectors\
├── backend\                                 # High-Performance FastAPI Backend
│   ├── main.py                              # 17 REST API endpoints & static asset router
│   ├── models\                              # Trained XGBoost Model JSON Artifacts
│   │   ├── m1_batter_xgb.json               # Model 1: Batter Runs Regressor
│   │   ├── m2a_bowler_runs_xgb.json         # Model 2A: Bowler Runs Conceded Regressor
│   │   └── m2b_bowler_wkt_xgb.json          # Model 2B: Bowler Wicket Probability Classifier
│   └── player_details.json                  # Precomputed telemetry & match performance logs
│
├── dashboard\                               # Production Standalone HTML Dashboard
│   └── index.html                           # Self-contained portable interactive application
│
├── frontend\                                # Full-Stack Web App Frontend
│   ├── index.html                           # Glassmorphic dark-theme SPA UI
│   ├── css\
│   │   └── styles.css                       # Design system, glow badges & custom styling
│   └── js\
│       ├── api.js                           # Asynchronous REST client
│       └── app.js                           # State manager, live search, modals & charts
│
├── src\                                     # Core Analytics & Modeling Source Package
│   ├── __init__.py                          # Package initialization
│   ├── config.py                            # Hyperparameters, thresholds & weights
│   ├── state_engine.py                      # Match state, DLS targets & par scoring rates
│   ├── pressure_model.py                    # Situational pressure classification engine
│   ├── metrics.py                           # Baseline vs pressure metrics & relative deltas
│   ├── bayesian_model.py                    # Empirical Bayes shrinkage & composite scoring
│   ├── train_xgboost_models.py              # XGBoost ML Model 1 & Model 2 trainer
│   ├── rebuild_dashboard_data.py            # Master data aggregator & multi-format builder
│   ├── generate_pdf_report.py               # ReportLab PDF executive submission builder
│   └── pipeline.py                          # End-to-end data processing orchestration
│
├── output\                                  # Official Output Tables & Submission CSVs
│   ├── Top_10_Batters_Under_Pressure.csv    # Official Top 10 Batters (Unstop format)
│   ├── Top_10_Bowlers_Under_Pressure.csv    # Official Top 10 Bowlers (Unstop format)
│   ├── All_Batters_Pressure_Rankings.csv    # Complete qualified cohort of 128 batters
│   ├── All_Bowlers_Pressure_Rankings.csv    # Complete qualified cohort of 162 bowlers
│   ├── dashboard_data.json                  # Aggregated payload with multi-format stats
│   └── ml_lab_data.json                     # ML feature importances & simulation payloads
│
├── reports\                                 # Official Submission Reports
│   ├── Methodology_Report.md                # Markdown technical & analytical methodology
│   └── Rajasthan_Royals_SupeRR_Selector_Submission_Report.pdf # Executive PDF Submission
│
├── dataset\                                 # Raw Match Data (2022–2026)
│   ├── ball_by_ball.csv                     # 200,999 legal delivery events
│   ├── matches.csv                          # Match metadata, dates, venues, winners
│   ├── competitions.csv                     # Tournament metadata & competition tiers
│   └── competition_team_player_mapping.csv  # Player ID, country & IPL franchise mappings
│
├── start_server.py                          # Full-Stack Web App Launcher
├── requirements.txt                         # Python dependencies
└── README.md                                # Platform documentation
```

---

## 📊 Core Dashboard Sections

The web application is partitioned into **5 intuitive sections**:

### 1. 📊 Section 1: Overview & High-Leverage Telemetry
- **Key Metrics Bar**: Certified summary counters (200,999 deliveries, 62,655 pressure balls, 867 matches, 2 formats, 141 competitions).
- **Format Filter**: One-click toggle between `Combined (Official)`, `T20 (IPL)`, and `T20I`.
- **Verified Leaderboards**: Direct display of Top 10 Batters and Top 10 Bowlers with accurate team codes (e.g. `IND`, `AFG`, `NZ`, `PAK`, `ENG`, `RR`, `KKR`, `MI`).
- **Rajasthan Royals Clutch XI Lineup**: A balanced, high-stakes dream team crafted from the highest-ranked pressure performers across batting, all-rounders, pace, and spin.

### 2. 🏏 Section 2: Batters Hub
- **Top 10 Batter Cards**: Rich visual cards highlighting rank, pressure strike rate, baseline delta ($\Delta \text{SR}$), pressure batting average, and volume sample size.
- **Pressure vs Normal SR Parity Chart ($y = x$)**:
  - Continuous **solid diagonal reference line ($y = x$)** with equal $90\text{--}220$ axis scales ($45^\circ$).
  - 🟢 **Above Solid Line ($y > x$)**: Clutch acceleration ($\Delta \text{SR} > 0$, strikes faster under pressure).
  - ⚪ **On Solid Line ($y = x$)**: Exact parity (no change in scoring velocity).
  - 🔻 **Below Solid Line ($y < x$)**: Deceleration ($\Delta \text{SR} < 0$, slowed down by pressure).
  - Hover tooltips displaying player name, team, rank, normal SR, pressure SR, acceleration, and ball sample size.
- **Contenders & Next Best Finishers**: Cards for ranks 11 through 25.
- **Complete Searchable & Sortable Table**: All 128 qualified batters with instant multi-column sorting and live search.

### 3. 🎯 Section 3: Bowlers Hub
- **Top 10 Bowler Cards**: Detailed profile cards showing pressure economy, baseline delta ($\Delta \text{Econ}$), wicket strike rate (WSR), dot-ball percentage, and clutch rating.
- **Pressure vs Normal Economy Parity Chart ($y = x$)**:
  - Continuous **solid diagonal reference line ($y = x$)** with equal $5.0\text{--}12.5$ axis scales ($45^\circ$).
  - 🟢 **Below Solid Line ($y < x$)**: Elite tightening & choke ($\Delta \text{Econ} > 0$, concedes fewer runs under pressure).
  - ⚪ **On Solid Line ($y = x$)**: Exact parity (economy identical in normal vs pressure overs).
  - ⚠️ **Above Solid Line ($y > x$)**: Leaked runs under pressure ($\Delta \text{Econ} < 0$).
  - Hover tooltips displaying player name, team, rank, normal economy, pressure economy, tightening, pressure wickets, and ball sample size.
- **Contenders & High-Stakes Specialists**: Cards for ranks 11 through 25.
- **Complete Searchable & Sortable Table**: All 162 qualified bowlers with live filtering and sorting.

### 4. 🧪 Section 4: ML Prediction Lab
- **Real-Time Interactive Match Simulator**:
  - Select any qualified player.
  - Adjust contextual levers: Balls to face / bowl (6 to 45 balls), Required Run Rate (6.0 to 18.0 RPO), Wickets in Hand (1 to 9 wickets), Match Phase (Powerplay, Middle, Death), Bowler Type (Pace vs Spin).
  - **Dynamic Inferences**:
    - **Batters**: Predicted runs scored, implied strike rate, expected boundaries, expected dot balls, win probability contribution.
    - **Bowlers**: Predicted runs conceded, implied economy rate, Model 2B single-ball wicket probability, over wicket probability, dot-ball choke rate, pressure defense index.
  - **AI Tactical Verdict**: Natural-language analytical summary of the simulated matchup.
  - **Feature Importance Breakdown**: Visual bar charts showing the top drivers of the trained XGBoost models.

### 5. 📐 Section 5: Methodology & Mathematical Architecture
- Complete documentation of the 5 pillars: Dynamic Pressure Definitions, Eligibility Cutoffs, Empirical Bayes Shrinkage, Composite Scoring Formulas, and ML Specifications & Limitations.
- Download buttons for official submission CSVs and reports.

---

## 🧮 Mathematical Architecture & Formulation

### 1. Dynamic Match Pressure Classification
A delivery is flagged as **High Pressure** if it satisfies any of the following live context conditions:
- **Innings 2 (Chasing)**:
  - $\text{RRR} \ge 9.50$ (Overs 9–20) with $\text{Runs Needed} \le 3.0 \times \text{Balls Remaining}$.
  - Clutch finish window: $\le 30$ balls remaining with $\text{Runs Needed} \le 2.5 \times \text{Balls Remaining}$.
  - Resource crisis: Wickets in hand $\le 4$ and $\text{Runs Needed} > \text{Balls Remaining}$.
  - Super Overs: Maximum leverage ($1.00$).
- **Innings 1 (Setting Total)**:
  - Death overs crucible (Overs 16–20) where par score rate exceeds $10.5$ RPO.
  - Top-order collapse recovery ($\ge 3$ wickets lost in Overs 1–6).
- **Match Stakes Multipliers**:
  $$\text{Ball Leverage} = \text{Base Pressure} \times S_{\text{stage}} \times W_{\text{comp}}$$
  - $S_{\text{stage}} = 1.30\times$ for Playoff, Eliminator, Qualifier, and Final matches ($1.00\times$ for League).
  - $W_{\text{comp}} = 1.30\times$ (Tier 1 IPL), $1.10\times$ (Tier 1.5 Top Bilaterals), $0.90\times$ (Tier 2 Standard T20I).

### 2. Sample Size Qualification Cutoffs
- **Batters**: Minimum **300 career legal balls faced** and **$\ge 100$ high-pressure balls faced** (**128 qualified candidates**).
- **Bowlers**: Minimum **300 career legal balls bowled** and **$\ge 100$ high-pressure balls bowled** (**162 qualified candidates**).
- **Format Sub-Filters**: Scaled to $\ge 150$ total balls and $\ge 50$ pressure balls for single-format analysis.

### 3. Empirical Bayes Shrinkage Formulation
To prevent small-sample volatility, raw pressure metrics are shrunk toward the cohort median ($\mu$) using $K = 50.0$ pseudo-balls and $K_{\text{wkt}} = 3.0$ pseudo-wickets:

$$\text{Bayes SR} = \frac{N_{\text{press}} \cdot \text{SR}_{\text{press}} + 50.0 \cdot \mu_{\text{SR}}}{N_{\text{press}} + 50.0} \quad (\mu_{\text{SR}} = 135.0)$$

$$\text{Bayes Econ} = \frac{N_{\text{press}} \cdot \text{Econ}_{\text{press}} + 50.0 \cdot \mu_{\text{Econ}}}{N_{\text{press}} + 50.0} \quad (\mu_{\text{Econ}} = 8.50)$$

$$\text{Bayes WSR} = \frac{W_{\text{press}} \cdot \text{WSR}_{\text{press}} + 3.0 \cdot \mu_{\text{WSR}}}{W_{\text{press}} + 3.0} \quad (\mu_{\text{WSR}} = 15.0)$$

### 4. Composite Scoring Formulas

#### Batters Formula
$$\text{Raw Bat Score} = 0.30 \cdot Z_{\text{VA}} + 0.25 \cdot Z_{\text{Bayes SR}} + 0.20 \cdot Z_{\Delta \text{SR}} + 0.15 \cdot Z_{\log(\text{Bayes Avg})} + 0.10 \cdot Z_{\text{Boundary \%}}$$

- **30% Value Added per ball ($Z_{\text{VA}}$)**: Runs scored above phase par adjusted for match leverage.
- **25% Shrunk Pressure Strike Rate ($Z_{\text{Bayes SR}}$)**: Scoring velocity under pressure.
- **20% Clutch Acceleration ($Z_{\Delta \text{SR}}$)**: $\text{Pressure SR} - \text{Normal SR}$.
- **15% Pressure Batting Average ($Z_{\log(\text{Bayes Avg})}$)**: Wicket preservation and innings stabilization.
- **10% Boundary Hitting % ($Z_{\text{Boundary \%}}$)**: Ability to clear the ropes under pressure.

#### Bowlers Formula
$$\text{Raw Bowl Score} = 0.35 \cdot Z_{\text{VA}} + 0.25 \cdot (-Z_{\text{Bayes Econ}}) + 0.20 \cdot (-Z_{\log(\text{Bayes WSR})}) + 0.10 \cdot Z_{\Delta \text{Econ}} + 0.10 \cdot Z_{\text{Dot \%}}$$

- **35% Value Added per ball ($Z_{\text{VA}}$)**: Runs saved below par $+ 15 \times (\text{Wkts} - \text{Par Wkts})$ adjusted for leverage.
- **25% Shrunk Pressure Economy Rate ($-Z_{\text{Bayes Econ}}$)**: Strict containment under pressure.
- **20% Wicket Strike Rate ($-Z_{\log(\text{Bayes WSR})}$)**: Balls needed per wicket under pressure.
- **10% Clutch Tightening ($Z_{\Delta \text{Econ}}$)**: $\text{Normal Econ} - \text{Pressure Econ}$.
- **10% Dot Ball Choke % ($Z_{\text{Dot \%}}$)**: Proportion of non-scoring deliveries bowled under pressure.

#### Volume Confidence & Final 0–100 Rating
$$W_{\text{volume}} = \sqrt{\frac{\sum \text{Ball Leverage}}{\sum \text{Ball Leverage} + 100.0}}$$

$$\text{Pressure Rating} = 50.0 + 15.0 \cdot Z(\text{Raw Score} \times W_{\text{volume}})$$

---

## 🏆 Official Results: Top 10 Rankings

### Top 10 Batters Under Pressure (Official Unstop Submission)

| Rank | Player Name | Team | Pressure Balls | Baseline SR | Pressure SR | $\Delta$ SR | Pressure Avg | Boundary % | Rating |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **#1** | **Suryakumar Yadav** | 🇮🇳 IND / MI | **779** | 154.39 | **197.05** | **+42.66** | 39.36 | 30.42% | **86.06** |
| **#2** | **Naman Dhir** | 🇮🇳 IND / MI | 213 | 152.39 | **196.71** | **+44.32** | 26.19 | 30.05% | **77.14** |
| **#3** | **Najibullah Zadran** | 🇦🇫 AFG | 164 | 93.66 | **177.44** | **+83.78** | **72.75** | 24.39% | **76.92** |
| **#4** | **Shubman Gill** | 🇮🇳 IND / GT | 355 | 143.38 | **189.30** | **+45.92** | 37.33 | 23.94% | **76.51** |
| **#5** | **Shashank Singh** | 🇮🇳 PBKS | 350 | 126.19 | **182.86** | **+56.67** | **45.71** | 24.57% | **76.00** |
| **#6** | **Tim David** | 🇦🇺 AUS / MI | 696 | 164.72 | **187.50** | +22.78 | 31.07 | 27.16% | **71.44** |
| **#7** | **Jos Buttler** | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 RR / ENG | 468 | 149.98 | **182.69** | **+32.71** | 34.20 | 25.85% | **71.27** |
| **#8** | **Donovan Ferreira** | 🇿🇦 SA / RR | 210 | 133.08 | **183.33** | **+50.25** | 27.50 | 25.71% | **70.20** |
| **#9** | **Shreyas Iyer** | 🇮🇳 IND / KKR | 557 | 141.59 | **180.25** | **+38.66** | 34.62 | 22.98% | **69.97** |
| **#10** | **Babar Azam** | 🇵🇰 PAK | 196 | 124.37 | **177.55** | **+53.19** | **43.50** | 23.47% | **69.84** |

---

### Top 10 Bowlers Under Pressure (Official Unstop Submission)

| Rank | Player Name | Team | Pressure Balls | Baseline Econ | Pressure Econ | $\Delta$ Econ | Pressure Wkts | Pressure WSR | Dot % | Rating |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **#1** | **Sufiyan Muqeem** | 🇵🇰 PAK | 204 | 6.59 | **5.09** | **+1.50** | 17 | **12.00** | **57.84%** | **95.90** |
| **#2** | **Sunil Narine** | 🌴 KKR | 475 | 7.07 | **6.40** | **+0.67** | 32 | 14.84 | 38.53% | **86.24** |
| **#3** | **Mohammad Nawaz** | 🇵🇰 PAK | 227 | 7.37 | **6.26** | **+1.11** | 18 | 12.61 | 40.97% | **81.98** |
| **#4** | **Akeal Hosein** | 🌴 WI / SRH | 272 | 7.85 | **7.15** | **+0.70** | 24 | **11.33** | 36.40% | **81.59** |
| **#5** | **Jasprit Bumrah** | 🇮🇳 IND / MI | **652** | 7.15 | **7.44** | -0.28 | **47** | 13.87 | 36.04% | **76.90** |
| **#6** | **Haris Rauf** | 🇵🇰 PAK | 429 | 8.80 | 8.49 | **+0.31** | **41** | **10.46** | 40.79% | **76.42** |
| **#7** | **Abrar Ahmed** | 🇵🇰 PAK | 239 | 6.88 | **6.25** | **+0.63** | 16 | 14.94 | 44.35% | **76.24** |
| **#8** | **Zakary Foulkes** | 🇳🇿 NZ | 114 | 10.25 | **7.47** | **+2.78** | 10 | 11.40 | 38.60% | **76.18** |
| **#9** | **Umran Malik** | 🇮🇳 IND / SRH | 166 | 9.81 | 9.54 | **+0.27** | 17 | **9.76** | 45.18% | **75.73** |
| **#10** | **Mitchell Starc** | 🇦🇺 AUS / KKR | 232 | 9.86 | 9.83 | **+0.03** | 26 | **8.92** | 36.21% | **74.54** |

---

## 🤖 Machine Learning Architecture (Model 1 & Model 2)

Trained across **192,709 delivery events** using 80/20 train/test evaluation:

```
+-----------------------------------------------------------------------------------------+
|                                    XGBOOST ML SUITE                                     |
+------------------------------+----------------------------------+-----------------------+
| Model 1: Batter Runs         | Model 2A: Bowler Runs Conceded   | Model 2B: Wicket Prob |
+------------------------------+----------------------------------+-----------------------+
| Objective: Regression        | Objective: Regression            | Objective: Classifier |
| Target: Batter delivery runs | Target: Runs conceded on ball    | Target: Dismissal (0/1)|
| Test MAE: 1.303 runs         | Test MAE: 1.304 runs             | ROC-AUC: 0.584        |
| Test RMSE: 1.725 runs        | Test RMSE: 1.725 runs            | Base Rate: 5.23%      |
+------------------------------+----------------------------------+-----------------------+
```

### Key Predictive Features
1. **Pressure Level & Leverage Weight**
2. **Required Run Rate (RRR) & Current Run Rate (CRR)**
3. **Wickets in Hand & Balls Remaining**
4. **Match Phase** (Powerplay, Middle Overs, Death Overs)
5. **Historical Player Metrics** (Bayes Pressure SR, Bayes Economy)
6. **Bowler Style** (Pace vs Spin)

---

## 🌐 FastAPI REST API Reference

The backend exposes **17 production endpoints**:

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/overview` | Core counters, certified deliveries, format rankings summary. |
| `GET` | `/api/format-rankings` | Format-specific rankings for Combined, T20 (IPL), and T20I. |
| `GET` | `/api/batters` | Full table of 128 qualified batters with baseline & pressure stats. |
| `GET` | `/api/batters/top10` | Official Top 10 Batters Under Pressure. |
| `GET` | `/api/bowlers` | Full table of 162 qualified bowlers with economy & wicket metrics. |
| `GET` | `/api/bowlers/top10` | Official Top 10 Bowlers Under Pressure. |
| `GET` | `/api/clutch-xi` | Rajasthan Royals Clutch XI balanced squad. |
| `GET` | `/api/player/{id}` | Detailed historical telemetry and match logs for a single player. |
| `GET` | `/api/ml-lab` | Model specifications, feature importances, and simulation config. |
| `GET` | `/api/predict` | Real-time delivery outcome inference using Model 1 & Model 2. |
| `GET` | `/health` | Application health and data integrity check. |

---

## 📄 Official Submissions & Documentation

- **Official PDF Submission Report**: [reports/Rajasthan_Royals_SupeRR_Selector_Submission_Report.pdf](file:///b:/SupeRR_Selectors/reports/Rajasthan_Royals_SupeRR_Selector_Submission_Report.pdf)
- **Technical Methodology Documentation**: [reports/Methodology_Report.md](file:///b:/SupeRR_Selectors/reports/Methodology_Report.md)
- **Official Top 10 Batters CSV**: [output/Top_10_Batters_Under_Pressure.csv](file:///b:/SupeRR_Selectors/output/Top_10_Batters_Under_Pressure.csv)
- **Official Top 10 Bowlers CSV**: [output/Top_10_Bowlers_Under_Pressure.csv](file:///b:/SupeRR_Selectors/output/Top_10_Bowlers_Under_Pressure.csv)

---

## 👥 Authors & Team
- **Project**: Rajasthan Royals — SupeRR Selector Season 2 (Round 1)
- **Submission Track**: Match Leverage & Reliability Analytics Engine
- **Engine Version**: 2.5 (Fully Verified & Tested)
- **License**: MIT
#   S u p e R R _ S e l e c t o r  
 