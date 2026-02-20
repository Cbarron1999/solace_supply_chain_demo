# 🚚 Solace Supply Chain Delay Detection Demo

An AI-powered, event-driven supply chain monitoring system built with **Solace Agent Mesh (SAM)**. This demo showcases multi-agent orchestration over a Solace event broker, automatically detecting shipment delays, assessing inventory impact, and dispatching real-time stakeholder notifications to Slack.

---

## 🏗️ Architecture

```
Shipment Event (simulate_shipment_delay.py)
        │
        ▼
┌─────────────────────────┐
│  Supply Chain           │
│  Orchestrator Agent     │  ← Coordinates all agents
└────────────┬────────────┘
             │ (parallel dispatch via Solace broker)
    ┌────────┴──────────┬──────────────────┐
    ▼                   ▼                  ▼
┌──────────┐    ┌───────────────┐   ┌─────────────────────┐
│  Delay   │    │  Inventory    │   │  Stakeholder        │
│Detection │    │  Impact Agent │   │  Notification Agent │
│  Agent   │    └───────────────┘   └──────────┬──────────┘
└──────────┘                                   │
                                               ▼
                                        📲 Slack Alert
                                   (#supply-chain-alerts)
```

**Key architectural principles demonstrated:**
- **Event-driven triggers** — agents react to events published on the Solace broker
- **Decoupled agents** — each agent operates independently, subscribing to relevant topics
- **Parallel processing** — Delay Detection, Inventory Impact, and Stakeholder Notification agents execute simultaneously
- **Real external integration** — live Slack webhook notifications confirm end-to-end delivery

---

## 🤖 Agents

| Agent | Role |
|-------|------|
| **Supply Chain Orchestrator** | Receives delay events, coordinates parallel agent execution, aggregates results |
| **Delay Detection Agent** | Classifies delay severity (LOW / MED / HIGH / CRITICAL) based on hours delayed, customer tier, and ETA vs must-arrive-by date |
| **Inventory Impact Agent** | Assesses risk to safety stock levels, identifies affected SKUs, recommends EXPEDITE / MONITOR / STANDARD response |
| **Stakeholder Notification Agent** | Composes professional notifications, identifies stakeholder groups, fires Slack webhook |

---

## 🛠️ Tech Stack

- **[Solace Agent Mesh (SAM)](https://github.com/SolaceLabs/solace-agent-mesh)** v1.17.0 — multi-agent orchestration framework
- **Solace PubSub+ Broker** — event broker (Docker)
- **OpenAI GPT** — LLM backbone for all agents
- **Python** — event simulator and Slack tool
- **Slack Webhooks** — real-time stakeholder notifications

---

## 📁 Project Structure

```
├── configs/
│   ├── agents/
│   │   ├── main_orchestrator.yaml          # Supply chain orchestrator
│   │   ├── delay_detection_agent.yaml      # Delay classification agent
│   │   ├── inventory_impact_agent.yaml     # Inventory risk agent
│   │   └── stakeholder_notification_agent.yaml  # Notification agent
│   ├── gateways/
│   │   └── webui.yaml                      # SAM web UI gateway
│   ├── services/
│   │   └── platform.yaml                   # Platform services config
│   ├── shared_config.yaml                  # Shared broker + model config
│   └── logging_config.yaml
├── stakeholder_tools/
│   └── tools.py                            # Slack webhook Python tool
├── src/
│   └── stakeholder_notification/
│       └── tools.py                        # Original tools (reference)
├── infra/
│   └── docker-compose.yml                  # Solace broker container
├── simulate_shipment_delay.py              # Event simulator script
├── requirements.txt
└── .env.example                            # Environment variable template
```

---

## 🚀 Setup & Running

### Prerequisites

- Docker + Docker Compose
- Python 3.12+
- SAM CLI: `pip install solace-agent-mesh`
- OpenAI API key
- Slack webhook URL

### 1. Start the Solace Broker

```bash
cd infra
docker-compose up -d
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
```
OPENAI_API_KEY=sk-...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
NAMESPACE=supply_chain_demo
SOLACE_BROKER_URL=ws://localhost:8008
SOLACE_BROKER_USERNAME=admin
SOLACE_BROKER_PASSWORD=admin
SOLACE_BROKER_VPN=default
LLM_SERVICE_PLANNING_MODEL_NAME=openai/gpt-5-mini
LLM_SERVICE_GENERAL_MODEL_NAME=openai/gpt-5-mini
```

### 3. Start SAM

```bash
sam run
```

Wait for all 4 agents to initialize, then navigate to **http://localhost:8000** for the web UI.

### 4. Trigger a Shipment Delay Event

**Via script (recommended for demos):**
```bash
python3 simulate_shipment_delay.py high
```

Severity options: `low`, `medium`, `high`, `critical`

**Via web UI:**
Paste the following into the chat:

```
A shipment delay has been detected. Please analyze and respond:

{
  "shipment_id": "SH-2026-001",
  "origin": "Houston, TX",
  "destination": "Chicago, IL",
  "customer": "Acme Corp",
  "customer_tier": "PREMIUM",
  "old_eta": "2026-02-19 08:00",
  "new_eta": "2026-02-19 22:00",
  "must_arrive_by": "2026-02-19 20:00",
  "delay_hours": 14,
  "delay_reason": "Port congestion at Houston terminal",
  "delayed_skus": ["SKU-4421", "SKU-8873", "SKU-2291"]
}

Please analyze this delay, assess inventory impact, and send stakeholder notifications.
```

---

## 📲 Expected Output

Within ~60 seconds of triggering an event:

1. **Delay Detection Agent** classifies severity (e.g., HIGH — 14hr delay, premium customer, past must-arrive-by)
2. **Inventory Impact Agent** returns risk assessment and recommended action (e.g., EXPEDITE)
3. **Stakeholder Notification Agent** fires a formatted Slack alert to `#supply-chain-alerts`

Example Slack notification:
```
🔴 Supply Chain Alert: URGENT — Shipment SH-2026-001 Delayed 14 Hours
Shipment ID: SH-2026-001 | Severity: 🔴 HIGH
Stakeholders: Operations, Customer Success, Procurement
Summary: Port congestion at Houston terminal has caused a 14-hour delay...
Action Items:
  • Expedite alternate routing
  • Notify Acme Corp customer success team
  • Review safety stock for SKU-4421, SKU-8873, SKU-2291
```

---

## 📝 Notes

- `.env` is excluded from version control — never commit API keys
- Database files (`.db`) are runtime artifacts and excluded from the repo
- The `stakeholder_tools/` module is the active Slack integration; `src/stakeholder_notification/` is kept for reference
- For production, agents would connect to an ERP (SAP, Oracle) via Solace's native connectors — the event-driven architecture makes the data source swappable without changing agent logic

---

## 👤 Author

**Christian Barron** — [github.com/Cbarron1999](https://github.com/Cbarron1999)

Built as a technical demo for Solace Solutions Architect interview, February 2026.
