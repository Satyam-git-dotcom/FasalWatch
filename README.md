# 🌾 FasalWatch: AI Multi-Agent Heat-Wave & Drought Early Warning System for Smallholder Farmers

[![Strands Agents SDK](https://img.shields.io/badge/Built%20with-Strands%20Agents%20SDK-orange.svg)](https://github.com/strands-agents/harness-sdk)
[![AWS Powered](https://img.shields.io/badge/AWS-DynamoDB%20%7C%20Translate%20%7C%20SNS-232F3E.svg)](https://aws.amazon.com)
[![Social Good](https://img.shields.io/badge/Focus-Climate%20Resilience%20%26%20Food%20Security-green.svg)](#social-impact)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Built for the **AWS Builder Center Hackathon: Building AI Agents with Strands SDK**.  
> Delivering **measurable climate resilience** for underserved smallholder farmers across India and the developing world.

---

## 🌍 The Social Good Challenge

Over **500 million smallholder farms** produce ~70% of the food in Asia and Sub-Saharan Africa. With intensifying climate volatility:
- A sudden heat wave exceeding **35°C during wheat flowering or rice transplanting causes spikelet sterility and pollen death**, resulting in **30%–50% yield loss in just 48 hours**.
- Most smallholder farmers are **digitally marginalized**: they do not speak English, lack smartphones or agronomy degrees, and only have basic feature phones capable of receiving standard SMS.
- By the time a farmer notices physical leaf curling, the physiological damage is irreversible.

**FasalWatch** bridges this gap: a multi-agent system powered by the **Strands Agents SDK** and **AWS services** that autonomously tracks 7-day microclimate forecasts, detects crop-specific threshold violations, synthesizes actionable non-jargon mitigation steps, and dispatches Grade-5 reading-level advisories in the farmer's native language over SMS before heat waves strike.

---

## 🏛️ Architecture: Multi-Agent Swarm

FasalWatch implements a 6-layer agent swarm built on the **Strands Agents SDK**:

```
                       [ Smallholder Farmer Profile ]
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  1. Profile Layer (AWS DynamoDB)│
                    │  Table: 'FasalWatch_Farmers'     │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  2. Data Layer (Open-Meteo API) │
                    │  7-Day Hourly Forecast & ERA5   │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  3. Risk Layer (Deterministic)  │
                    │  Crop Heat/Drought Thresholds   │
                    │  + Strands Risk Agent           │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  4. Advisor Agent (Strands)     │
                    │  2-3 Practical Mitigations      │
                    │  (Banned: agronomic jargon)     │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  5. Localizer Agent             │
                    │  (AWS Amazon Translate)         │
                    │  Grade 5 Reading Level, <160 ch │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  6. Reviewer Agent (Strands)    │
                    │  Safety Audit, Anti-alarmism    │
                    └────────────────┬────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────────┐
                    │  7. Alert Layer (AWS Amazon SNS)│
                    │  Topic: 'FasalWatch_Alerts'      │
                    │  Feature Phone SMS Delivery     │
                    └─────────────────────────────────┘
```

---

## 🤖 Strands Agent Roles

| Agent | Technology | Responsibility |
|---|---|---|
| **Data Agent** | Strands `@tool` + Open-Meteo | Fetches 7-day temperature, precipitation, and wind speeds without API friction. |
| **Risk Agent** | Strands SDK + `crop_thresholds.json` | Computes consecutive heat-stress days against crop growth stages (e.g., wheat flowering: >35°C for 2 days). |
| **Advisor Agent** | Strands SDK | Synthesizes 2–3 actionable farm interventions (pre-dawn irrigation, organic straw mulching, shading). |
| **Localizer Agent** | AWS Amazon Translate | Formats advisory for SMS (<160 chars) and translates into Hindi, Marathi, Tamil, or 75+ regional dialects. |
| **Reviewer Agent** | Strands SDK | Quality gate that inspects advisories for contradictions, alarmist tone, and length limits before delivery. |

---

## ☁️ AWS Services Integration

1. **Amazon DynamoDB**: Stores persistent farmer profiles (`farmer_id`, GPS coordinates, active crop, stage, preferred dialect, phone number).
2. **Amazon Translate**: Low-latency, culturally accurate translation into regional Indian languages without LLM translation hallucinations.
3. **Amazon SNS (Simple Notification Service)**: Manages message topics (`FasalWatch_Alerts`) and dispatches outbound alerts to farmers' mobile devices.
4. **Amazon Bedrock (Optional / Cloud)**: Enterprise foundation model hosting for Claude & Nova agents.

---

## 📊 Measurable Social Impact

| Metric | Baseline (Without FasalWatch) | With FasalWatch |
|---|---|---|
| **Warning Lead Time** | 0 days (reactive after damage occurs) | **7 days advance warning** |
| **Language Accessibility** | English / complex agronomic jargon | **Native regional language** (Hindi, Marathi, etc.) at **Grade 5 reading level** |
| **Delivery Medium** | Smartphone apps requiring 4G data | **Plain SMS** on basic feature phones (≤160 characters) |
| **Crop Loss Avoided** | 30%–50% loss during severe heat waves | **Estimated 60%+ damage reduction** via pre-heat root moisture conservation |

### 📜 Historical Verification (Rajasthan 2022 Replay)
During the catastrophic **June 2022 North India Heat Wave**, Jaipur recorded **43.0°C** for 7 consecutive days with 0mm rainfall.
- **FasalWatch Replay Evaluation**: Triggered **CRITICAL RISK** alert 7 days prior to peak heat.
- **Delivered Advisory**: Prompted farmers to apply 3cm organic straw mulch and schedule pre-sunrise shallow furrow irrigation before flowering spikelets dehydrated.

---

## 🚀 Quickstart & Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/fasalwatch.git
cd fasalwatch
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials
Ensure your AWS credentials have permissions for Translate, DynamoDB, and SNS:
```bash
aws configure
# Region: us-east-1
```

### 4. Run CLI Pipeline
```bash
# Run FasalWatch for Ramesh Kumar (wheat farmer in Jaipur)
python3 main.py farmer_001
```

### 5. Launch the React Web Application (Recommended)
FasalWatch includes a full **React dashboard** styled with the **Instrument Serif & Inter** agricultural design system:
```bash
# Start backend & serve compiled React app
python3 server.py
# Open http://localhost:8000 in your browser
```

Or run frontend in Vite development mode:
```bash
cd frontend && npm run dev
```

*(Alternatively, the Streamlit dashboard remains available via `streamlit run demo/app.py`)*

---

## 📁 Repository Structure

```
fasalwatch/
├── agents/                    # Strands Agents SDK Swarm
│   ├── advisor_agent.py       # Practical mitigation advisor
│   ├── data_agent.py          # Weather retrieval agent
│   ├── localizer_agent.py     # AWS Translate localization
│   ├── reviewer_agent.py      # Quality assurance gate
│   └── risk_agent.py          # Crop threshold evaluation agent
├── tools/                     # Strands @tool implementations
│   ├── alert_tool.py          # Alert simulator
│   ├── crop_tool.py           # Threshold query tool
│   ├── dynamo_tool.py         # AWS DynamoDB client
│   ├── profile_tool.py        # Farmer profile lookup
│   ├── risk_calculator.py     # Deterministic risk engine
│   ├── sns_tool.py            # AWS Amazon SNS dispatcher
│   └── weather_tool.py        # Open-Meteo API wrapper
├── data/                      # Crop data & seeds
│   ├── crop_thresholds.json   # Agronomic temperature & rainfall thresholds
│   └── farmer_profiles.json   # Seed profiles for DynamoDB
├── demo/
│   └── app.py                 # Streamlit visual dashboard
├── tests/
│   └── historical_replay.py   # Rajasthan 2022 ERA5 replay
├── main.py                    # Multi-agent orchestrator entry point
├── config.py                  # Environment & toggle configuration
└── requirements.txt           # Dependencies
```

---

## 🏆 Hackathon Alignment

- **Strands Agents SDK**: Built exclusively on Strands Agent structures, `@tool` wrappers, and multi-agent coordination.
- **Social Good Focus**: Climate resilience and food security for underserved smallholder farmers.
- **Originality**: Combines meteorological APIs, deterministic agronomic thresholds, and AWS cloud infrastructure (DynamoDB, Translate, SNS).

---

## 📄 License
This project is licensed under the MIT License.

