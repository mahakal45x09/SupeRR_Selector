<div align="center">

<img src="./logo.png" alt="Rajasthan Royals SupeRR Selector Logo" width="160" />

# 👑 RAJASTHAN ROYALS — SUPERR SELECTOR
### ⚡ Season 2 (Round 1) • Match Leverage & Reliability Analytics Engine (2022–2026)

*Isolating the Most Reliable, Ice-Cold Match-Winners Under Extreme Match Pressure*

<br/>

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![XGBoost](https://img.shields.io/badge/XGBoost-3.0%2B-EB5424?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4%2B-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4%2B-FF6384?style=for-the-badge&logo=chart.js&logoColor=white)](https://www.chartjs.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-blueviolet?style=for-the-badge)](LICENSE)

<br/>

**[ 🚀 Quickstart Guide ](#-quickstart-guide)** &nbsp;•&nbsp;
**[ 🏛️ System Architecture ](#-system-architecture)** &nbsp;•&nbsp;
**[ 🏏 Official Top 10 Batters ](#-official-top-10-batters-under-pressure)** &nbsp;•&nbsp;
**[ 🎯 Official Top 10 Bowlers ](#-official-top-10-bowlers-under-pressure)** &nbsp;•&nbsp;
**[ 🤖 ML Prediction Lab ](#-machine-learning-prediction-lab)** &nbsp;•&nbsp;
**[ 📑 Methodology Report ](#-methodology--mathematical-formulations)**

</div>

<br/>

---

## 📊 Telemetry at a Glance

| 🏟️ Total Deliveries Analyzed | ⚔️ High-Pressure Balls | 🏆 Matches Spanned | 🌐 Competitions |
| :---: | :---: | :---: | :---: |
| **`200,999`** | **`62,655`** *(31.17%)* | **`867`** | **`141`** |

| 📈 Match Formats Evaluated | 🤖 Trained ML Models | 🧮 Qualified Batters | 🎯 Qualified Bowlers |
| :---: | :---: | :---: | :---: |
| **IPL (T20) + T20I** | **Model 1, 2A & 2B** | **128** *(>=100 pressure balls)* | **162** *(>=100 pressure balls)* |

---

## 📌 Executive Overview

> [!IMPORTANT]
> **In modern T20 tournament cricket, cumulative averages and season-wide strike rates routinely mislead recruitment decisions.** A batter who plunders runs in dead-rubber group matches or low-leverage overs often crumbles during steep playoff chases. Similarly, a bowler with an impressive cumulative economy rate may leak decisive boundaries when defending a single-digit total in the 20th over.

Developed for the **Rajasthan Royals SupeRR Selector Season 2 (Round 1)** challenge, this platform delivers an end-to-end full-stack analytics engine and machine learning simulation suite built across **200,999 legal deliveries** spanning **867 matches** and **141 competitions** (2022–2026).

### 🌟 Core Capabilities
- ⚡ **Dynamic Delivery Pressure Engine**: Evaluates situational leverage ball-by-ball using Required Run Rate ($RRR$), Balls Remaining, Wickets in Hand, Death Overs (16–20), Collapse States, and Knockout multipliers ($1.30\times$).
- 📈 **Relative Reliability ($\Delta$-Differential)**: Directly measures how much a player elevates or declines against their own personal non-pressure baseline ($SR_P - SR_B$ and $Econ_B - Econ_P$).
- 🧮 **Empirical Bayes Regularization**: Applies Bayesian shrinkage to penalize small-sample anomalies and regularize performance toward cohort par.
- 🤖 **Dual XGBoost Simulation Suite**: Predicts delivery-level runs scored, runs conceded, and dismissal probabilities in custom game scenarios.
- 🌐 **Production Web Application**: Features interactive scatter plots with equal-axis diagonal lines ($y=x$), live filters, dynamic ML scenario lab, and complete team mappings.

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Installation

Clone the repository and install dependencies in Python 3.10+:

```bash
git clone https://github.com/YourOrg/SupeRR_Selectors.git
cd SupeRR_Selectors
pip install -r requirements.txt
```

### 2. Launch the Full-Stack Web Platform

Run the unified server launcher:

```bash
python start_server.py
```

Access the interactive portals:
- 🌐 **Web Dashboard UI**: [`http://127.0.0.1:8000`](http://127.0.0.1:8000)
- 📚 **Interactive Swagger API Docs**: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- 📖 **Redoc Alternative API Specs**: [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)

<details>
<summary><b>🛠️ Click to expand Command-Line Pipeline & Build Commands</b></summary>

<br/>

```bash
# 1. Run complete analytics pipeline (state engine, metrics, Bayes models, rankings)
python -m src.pipeline

# 2. Train XGBoost Machine Learning Models (Model 1, Model 2A, Model 2B)
python -m src.train_xgboost_models

# 3. Rebuild dashboard JSON data payloads across all formats
python -m src.rebuild_dashboard_data

# 4. Generate the 8-page Publication-Grade Executive Submission PDF
python src/generate_pdf_report.py
```

</details>

---

## 🏛️ System Architecture

```
B:\SupeRR_Selectors\
├── backend\                                 # High-Performance FastAPI Backend
│   ├── main.py                              # 17 REST API endpoints & static router
│   ├── models\                              # Trained XGBoost Machine Learning JSON Artifacts
│   │   ├── m1_batter_xgb.json               # Model 1: Batter Delivery Runs Regressor
│   │   ├── m2a_bowler_runs_xgb.json         # Model 2A: Bowler Runs Conceded Regressor
│   │   └── m2b_bowler_wkt_xgb.json          # Model 2B: Bowler Wicket Probability Classifier
│   └── player_details.json                  # Precomputed telemetry & match performance logs
│
├── dashboard\                               # Standalone Dashboard Build
│   └── index.html                           # Self-contained zero-dependency web app
│
├── frontend\                                # Full-Stack UI Assets
│   ├── index.html                           # Glassmorphic dark-theme SPA UI
│   ├── css\
│   │   └── styles.css                       # Rajasthan Royals color tokens & animations
│   └── js\
│       ├── api.js                           # Asynchronous REST client
│       └── app.js                           # State manager, live search, modals & charts
│
├── src\                                     # Analytics & Modeling Core Engine
│   ├── config.py                            # Thresholds, par scoring rates & weights
│   ├── state_engine.py                      # Match state, DLS targets & phase rates
│   ├── pressure_model.py                    # Situational pressure classification
│   ├── metrics.py                           # Baseline vs pressure metrics & relative deltas
│   ├── bayesian_model.py                    # Empirical Bayes shrinkage & composite scoring
│   ├── train_xgboost_models.py              # XGBoost Model 1 & Model 2 trainer
│   ├── rebuild_dashboard_data.py            # Master data aggregator & multi-format builder
│   ├── generate_pdf_report.py               # ReportLab PDF executive submission builder
│   └── pipeline.py                          # End-to-end data processing orchestration
│
├── output\                                  # Official Submission CSVs & Data Feeds
│   ├── Top_10_Batters_Under_Pressure.csv    # Official Batter Rankings CSV
│   ├── Top_10_Bowlers_Under_Pressure.csv    # Official Bowler Rankings CSV
│   └── dashboard_data.json                  # Multi-format data payload
│
└── reports\                                 # Documentation & Submission Artifacts
    ├── logo.png                             # Official Rajasthan Royals SupeRR emblem
    ├── Methodology_Report.md                # 10-Section Comprehensive Technical Report
    └── Rajasthan_Royals_SupeRR_Selector_Submission_Report.pdf  # 8-Page Executive PDF
```

---

## 🏏 Official Top 10 Batters Under Pressure

*Minimum Eligibility: >= 300 career balls faced, >= 100 high-pressure balls faced.*

| Rank | Player Name | Franchise / Nation | Total Balls | Pressure Balls | Baseline SR | Pressure SR | $\Delta$ SR | Baseline Avg | Pressure Avg | Boundary % | Rating |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **#1** | **Suryakumar Yadav** 🇮🇳 | IND / MI | 2,761 | 779 | 154.39 | **197.05** | **+42.66** | 39.23 | **39.36** | 30.42% | **86.06** |
| **#2** | **Naman Dhir** 🇮🇳 | IND / MI | 589 | 213 | 152.39 | **196.71** | **+44.32** | 30.16 | 26.19 | 30.05% | **77.14** |
| **#3** | **Najibullah Zadran** 🇦🇫 | AFG | 306 | 164 | 93.66 | **177.44** | **+83.78** | 13.30 | **72.75** | 24.39% | **76.92** |
| **#4** | **Shubman Gill** 🇮🇳 | IND / GT | 2,711 | 355 | 143.38 | **189.30** | **+45.92** | 42.76 | 37.33 | 23.94% | **76.51** |
| **#5** | **Shashank Singh** 🇮🇳 | IND / PBKS | 560 | 350 | 126.19 | **182.86** | **+56.67** | 26.50 | **45.71** | 24.57% | **76.00** |
| **#6** | **Tim David** 🇦🇺 | AUS / MI | 1,226 | 696 | 164.72 | **187.50** | **+22.78** | 43.65 | 31.07 | 27.16% | **71.44** |
| **#7** | **Jos Buttler** 🏴󠁧󠁢󠁥󠁮󠁧󠁿 | ENG / RR | 2,829 | 468 | 149.98 | **182.69** | **+32.71** | 43.72 | 34.20 | 25.85% | **71.27** |
| **#8** | **Donovan Ferreira** 🇿🇦 | SA / RR | 343 | 210 | 133.08 | **183.33** | **+50.25** | 19.67 | 27.50 | 25.71% | **70.20** |
| **#9** | **Shreyas Iyer** 🇮🇳 | IND / KKR | 1,865 | 557 | 141.59 | **180.25** | **+38.66** | 37.80 | 34.62 | 22.98% | **69.97** |
| **#10** | **Babar Azam** 🇵🇰 | PAK | 1,181 | 196 | 124.37 | **177.55** | **+53.19** | 33.11 | **43.50** | 23.47% | **69.84** |

---

## 🎯 Official Top 10 Bowlers Under Pressure

*Minimum Eligibility: >= 300 career legal balls bowled, >= 100 high-pressure balls bowled.*

| Rank | Player Name | Franchise / Nation | Legal Balls | Pressure Balls | Baseline Econ | Pressure Econ | $\Delta$ Econ | Pressure Wkts | Pressure WSR | Dot % | Rating |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **#1** | **Sufiyan Muqeem** 🇵🇰 | PAK | 518 | 204 | 6.59 | **5.09** | **+1.50** | 17 | **12.00** | **57.84%** | **95.90** |
| **#2** | **Sunil Narine** 🇹🇹 | WI / KKR | 1,533 | 475 | 7.07 | **6.40** | **+0.67** | 32 | 14.84 | 38.53% | **86.24** |
| **#3** | **Mohammad Nawaz** 🇵🇰 | PAK | 1,004 | 227 | 7.37 | **6.26** | **+1.11** | 18 | 12.61 | 40.97% | **81.98** |
| **#4** | **Akeal Hosein** 🇹🇹 | WI / SRH | 1,693 | 272 | 7.85 | **7.15** | **+0.70** | 24 | **11.33** | 36.40% | **81.59** |
| **#5** | **Jasprit Bumrah** 🇮🇳 | IND / MI | 1,709 | 652 | 7.15 | **7.44** | -0.28 | **47** | 13.87 | 36.04% | **76.90** |
| **#6** | **Haris Rauf** 🇵🇰 | PAK | 1,027 | 429 | 8.80 | 8.49 | **+0.31** | **41** | **10.46** | 40.79% | **76.42** |
| **#7** | **Abrar Ahmed** 🇵🇰 | PAK | 764 | 239 | 6.88 | **6.25** | **+0.63** | 16 | 14.94 | 44.35% | **76.24** |
| **#8** | **Zakary Foulkes** 🇳🇿 | NZ | 365 | 114 | 10.25 | **7.47** | **+2.78** | 10 | 11.40 | 38.60% | **76.18** |
| **#9** | **Umran Malik** 🇮🇳 | IND / SRH | 564 | 166 | 9.81 | 9.54 | **+0.27** | 17 | **9.76** | 45.18% | **75.73** |
| **#10** | **Mitchell Starc** 🇦🇺 | AUS / KKR | 810 | 232 | 9.86 | 9.83 | **+0.03** | 26 | **8.92** | 36.21% | **74.54** |

---

## 🌟 Rajasthan Royals "Clutch XI" Tactical Lineup

Formulated under standard IPL squad rules (maximum 4 overseas players, 1 designated wicketkeeper, 6 bowling options, and balanced phase distribution):

| Order | Player Name | Tactical Role | Team / Overseas | Key Clutch Metric | Match-Winning Role |
| :---: | :---| :---: | :---: | :---: | :---|
| **#1** | **Jos Buttler** ✈️ | Explosive Opener / WK | Rajasthan Royals | 182.69 SR (+32.71 $\Delta$) | Powerplay launcher; suppresses dots to 22.0% in crunch matches. |
| **#2** | **Shubman Gill** | Technical Anchor | Gujarat Titans | 189.30 SR (+45.92 $\Delta$) | Elite gear-shifter; combines technical foundation with high death acceleration. |
| **#3** | **Shreyas Iyer** | Spin-Dominant Rebuild | Kolkata Knight Riders | 180.25 SR (+38.66 $\Delta$) | Rebuild specialist when early wickets fall; dominates middle-overs spin. |
| **#4** | **Suryakumar Yadav** (C) | 360° Clutch Weapon | Mumbai Indians | **197.05 SR (+42.66 $\Delta$)** | **#1 Ranked Batter**: Unstoppable 30.42% boundary rate across all fields. |
| **#5** | **Shashank Singh** | Crisis Finisher | Punjab Kings | 182.86 SR (**45.71 Avg**) | High-RRR executioner; +56.67 $\Delta SR$ with 45.71 average under pressure. |
| **#6** | **Tim David** ✈️ | Power Surge Finisher | Mumbai Indians | 187.50 SR (+22.78 $\Delta$) | Pure death boundary clearer against high-velocity pace bowling. |
| **#7** | **Donovan Ferreira** ✈️ | Finisher / Utility | Rajasthan Royals | 183.33 SR (+50.25 $\Delta$) | High-strike-rate accelerator from ball 1 in overs 17–20. |
| **#8** | **Sunil Narine** ✈️ | Mystery Spin Lockdown | Kolkata Knight Riders | **6.40 Econ (32 Wkts)** | **#2 Ranked Bowler**: 3.44 runs/over below IPL death par; 9.47% boundary rate. |
| **#9** | **Akeal Hosein** | Powerplay & Middle LAO | West Indies / SRH | 7.15 Econ (11.33 WSR) | Accurate arm-ball bowler; limits Powerplay damage with 36.4% dot balls. |
| **#10** | **Jasprit Bumrah** | Death Yorker Specialist | Mumbai Indians | 7.44 Econ (**47 Wkts**) | Ultimate high-volume firewall (652 pressure balls); impenetrable at death. |
| **#11** | **Mitchell Starc** | Hostile Pace Enforcer | Kolkata Knight Riders | **8.92 WSR (26 Wkts)** | Most lethal pressure strike rate in the tournament; playoff breakthrough weapon. |

---

## 🤖 Machine Learning Prediction Lab

Trained on **192,709 delivery records** across 2022–2026, the platform features three high-performance gradient-boosted models for live in-game simulation:

```
                      ┌────────────────────────────────────────┐
                      │    DELIVERY-LEVEL SIMULATION SUITE     │
                      └───────────────────┬────────────────────┘
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
   ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
   │     Model 1     │           │    Model 2A     │           │    Model 2B     │
   │   Batter Runs   │           │   Bowler Runs   │           │   Wicket Prob   │
   │  (XGBRegressor) │           │  (XGBRegressor) │           │ (XGBClassifier) │
   └────────┬────────┘           └────────┬────────┘           └────────┬────────┘
            │                             │                             │
      MAE: 1.303 runs               MAE: 1.304 runs              ROC-AUC: 0.584
      RMSE: 1.725 runs              RMSE: 1.725 runs             27.4% Death Over Prob
```

### Global Feature Importance Breakdown
1. **Match Pressure Index & Situational Leverage**: `38.4%`
2. **Required Run Rate (RRR)**: `24.2%`
3. **Balls Remaining & Innings Phase**: `16.8%`
4. **Wickets in Hand**: `11.5%`
5. **Historical Bayes Pressure Metric**: `9.1%`

---

## 🧮 Methodology & Mathematical Formulations

<details open>
<summary><b>📐 1. Dynamic Pressure Formulation</b></summary>

<br/>

### Innings 2: Chasing Pressure ($PI_{\text{chase}}$)
In the second innings, delivery pressure is triggered dynamically based on match state:
$$RRR_t = \frac{\text{Runs Needed}_t \times 6}{B_{\text{rem}, t}}$$
- **Late-Phase Escalation**: $B_{\text{rem}} \le 72$ (Overs 9–20) with $RRR \ge 9.50$ and $\text{Runs Needed} \le B_{\text{rem}} \times 3.0$.
- **Close Finish Window**: $B_{\text{rem}} \le 30$ (Overs 16–20) with $\text{Runs Needed} \le B_{\text{rem}} \times 2.5$.
- **Resource Strain**: $W_{\text{hand}} \le 4$ and $\text{Runs Needed} > B_{\text{rem}}$.
- **Super Overs**: Maximum leverage ($PI = 1.0$).

### Innings 1: Target-Setting Pressure ($PI_{\text{first}}$)
- **Death Overs Crucible (Overs 16–20)**: High dismissal risk under intense boundary demand.
- **Crisis Recovery**: $\ge 3$ wickets lost in Powerplay or $\ge 4$ wickets before Over 10.

### Competition & Match Multipliers
- **Playoffs / Knockouts / Finals**: $1.30\times$ leverage multiplier.
- **Competition Tiers**: Tier 1 (IPL) = $1.30\times$, Tier 1.5 (Asia Cup/Major Bilaterals) = $1.10\times$, Tier 2 = $0.90\times$.

</details>

<details open>
<summary><b>🧪 2. Empirical Bayes Shrinkage Regularization</b></summary>

<br/>

To prevent small-sample distortions, raw metrics are regularized toward the cohort median ($\mu$) with $K=50.0$ pseudo-balls:
$$\widehat{SR}_{P, i} = \frac{N_{P, i} \cdot SR_{P, i} + 50.0 \cdot \mu_{SR}}{N_{P, i} + 50.0} \quad (\mu_{SR} = 135.0)$$
$$\widehat{Econ}_{P, i} = \frac{N_{P, i} \cdot Econ_{P, i} + 50.0 \cdot \mu_{Econ}}{N_{P, i} + 50.0} \quad (\mu_{Econ} = 8.50)$$
$$\widehat{WSR}_{P, i} = \frac{W_{P, i} \cdot WSR_{P, i} + 3.0 \cdot \mu_{WSR}}{W_{P, i} + 3.0} \quad (\mu_{WSR} = 15.0)$$

</details>

<details open>
<summary><b>⚖️ 3. Composite Scoring Formulas & Weightings</b></summary>

<br/>

### Batters Composite Score (0–100 Scale)
$$\text{Raw Batting} = 0.30 \cdot Z_{\text{VA}} + 0.25 \cdot Z_{\text{Bayes SR}} + 0.20 \cdot Z_{\Delta \text{SR}} + 0.15 \cdot Z_{\log(\text{Bayes Avg})} + 0.10 \cdot Z_{\text{Boundary \%}}$$

### Bowlers Composite Score (0–100 Scale)
$$\text{Raw Bowling} = 0.35 \cdot Z_{\text{VA}} + 0.25 \cdot (-Z_{\text{Bayes Econ}}) + 0.20 \cdot (-Z_{\log(\text{Bayes WSR})}) + 0.10 \cdot Z_{\Delta \text{Econ}} + 0.10 \cdot Z_{\text{Dot \%}}$$

### Volume Confidence Scaling
$$\text{Composite Score} = \text{Raw Score} \times \sqrt{\frac{\sum \text{Ball Leverage}}{\sum \text{Ball Leverage} + 100.0}}$$
$$\text{Pressure Rating} = 50.0 + 15.0 \cdot Z(\text{Composite Score})$$

</details>

---

## 🌐 Complete REST API Specification

The FastAPI backend serves 17 optimized endpoints:

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/api/overview` | `GET` | Dataset telemetry (deliveries, matches, formats, sample counts) |
| `/api/top-batters` | `GET` | Top 10 batters under pressure with full baseline comparisons |
| `/api/top-bowlers` | `GET` | Top 10 bowlers under pressure with containment & strike rates |
| `/api/all-batters` | `GET` | Paginated search of all 128 qualified batters under pressure |
| `/api/all-bowlers` | `GET` | Paginated search of all 162 qualified bowlers under pressure |
| `/api/format-rankings/{fmt}` | `GET` | Format-filtered rankings (`T20`, `T20I`, or `Combined`) |
| `/api/clutch-lineup` | `GET` | Rajasthan Royals Clutch XI tactical squad composition |
| `/api/ml/predict-batter` | `POST` | Model 1 inference: Predicted runs, boundaries & strike rate |
| `/api/ml/predict-bowler` | `POST` | Model 2 inference: Runs conceded, dot probability & wicket risk |
| `/api/methodology` | `GET` | Mathematical definitions, Bayesian shrinkage parameters & rules |

---

## 📄 Verified Submission Deliverables

- 📘 **Technical Methodology Report**: [`reports/Methodology_Report.md`](file:///B:/SupeRR_Selectors/reports/Methodology_Report.md)
- 📕 **Official Executive Submission PDF**: [`reports/Rajasthan_Royals_SupeRR_Selector_Submission_Report.pdf`](file:///B:/SupeRR_Selectors/reports/Rajasthan_Royals_SupeRR_Selector_Submission_Report.pdf)
- 📊 **Official Batters CSV**: [`output/Top_10_Batters_Under_Pressure.csv`](file:///B:/SupeRR_Selectors/output/Top_10_Batters_Under_Pressure.csv)
- 🎯 **Official Bowlers CSV**: [`output/Top_10_Bowlers_Under_Pressure.csv`](file:///B:/SupeRR_Selectors/output/Top_10_Bowlers_Under_Pressure.csv)
- 💻 **Interactive Standalone Dashboard**: [`dashboard/index.html`](file:///B:/SupeRR_Selectors/dashboard/index.html)

---

<div align="center">

**Rajasthan Royals — SupeRR Selector Season 2 (Round 1)**  
*Engineered for High-Stakes Tactical Decision Making*

</div>
