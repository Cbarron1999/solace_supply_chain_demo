#!/usr/bin/env python3
"""
Shipment Delay Event Simulator
Publishes a shipment delay event using the A2A protocol directly to SAM,
triggering the full multi-agent pipeline and Slack notification.
"""

import json
import uuid
import requests
from datetime import datetime
import sys

# ── Configuration ──────────────────────────────────────────────────────────────
WEBUI_URL = "http://127.0.0.1:8000"

SCENARIOS = {
    "high": {
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
    },
    "medium": {
        "shipment_id": "SH-2026-002",
        "origin": "Los Angeles, CA",
        "destination": "Dallas, TX",
        "customer": "Beta Manufacturing",
        "customer_tier": "STANDARD",
        "old_eta": "2026-02-20 10:00",
        "new_eta": "2026-02-20 16:00",
        "must_arrive_by": "2026-02-20 18:00",
        "delay_hours": 6,
        "delay_reason": "Weather conditions on I-10",
        "delayed_skus": ["SKU-7732"]
    }
}

def simulate(scenario_name: str = "high"):
    scenario = SCENARIOS[scenario_name]

    print(f"\n{'='*60}")
    print(f"  SUPPLY CHAIN EVENT SIMULATOR")
    print(f"  Solace Agent Mesh — Live Demo")
    print(f"{'='*60}")
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Firing shipment delay event...")
    print(f"  Shipment  : {scenario['shipment_id']}")
    print(f"  Customer  : {scenario['customer']} ({scenario['customer_tier']})")
    print(f"  Route     : {scenario['origin']} → {scenario['destination']}")
    print(f"  Delay     : {scenario['delay_hours']} hours")
    print(f"  Reason    : {scenario['delay_reason']}")
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Publishing via A2A protocol to SAM gateway...")

    prompt = f"""A shipment delay has occurred with the following details:
{json.dumps(scenario, indent=2)}

Please analyze this delay, assess inventory impact, and send stakeholder notifications."""

    # A2A JSON-RPC 2.0 payload
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": prompt
                    }
                ],
                "messageId": str(uuid.uuid4()),
                "metadata": {"agent_name": "supply_chain_orchestrator"}
            },
            "configuration": {
                "accepted_output_modes": ["text"],
                "blocking": False
            }
        }
    }

    try:
        response = requests.post(
            f"{WEBUI_URL}/api/v1/message:send",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code in [200, 201, 202]:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Event published successfully!")
            print(f"\n👉 Watch the agent workflow at : {WEBUI_URL}")
            print(f"👉 Check #supply-chain-alerts  : Slack notification incoming\n")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Status {response.status_code}: {response.text[:200]}")
            _manual_fallback(prompt)

    except requests.exceptions.ConnectionError:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Could not reach SAM gateway — is sam run active?")
        _manual_fallback(prompt)

def _manual_fallback(prompt):
    print(f"\n{'─'*60}")
    print("Paste this into the SAM chat at localhost:8000:")
    print('─'*60)
    print(prompt)
    print('─'*60)

if __name__ == "__main__":
    scenario = sys.argv[1] if len(sys.argv) > 1 else "high"
    if scenario not in SCENARIOS:
        print(f"Unknown scenario. Use: {list(SCENARIOS.keys())}")
        sys.exit(1)
    simulate(scenario)
