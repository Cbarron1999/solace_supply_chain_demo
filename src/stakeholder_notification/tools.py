import httpx
import os
import json
from datetime import datetime
from typing import Any, Dict, Optional
from google.adk.tools import ToolContext
from solace_ai_connector.common.log import log


async def send_slack_notification(
    shipment_id: str,
    severity: str,
    subject: str,
    message: str,
    stakeholders_notified: list,
    action_items: list,
    tool_context: Optional[ToolContext] = None,
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Sends a shipment delay notification to the Slack #supply-chain-alerts channel.

    Args:
        shipment_id: The shipment identifier
        severity: LOW, MED, HIGH, or CRITICAL
        subject: Notification subject line
        message: Full notification message
        stakeholders_notified: List of stakeholder groups notified
        action_items: List of recommended action items
    """
    log.info("[SlackNotification] Sending notification for shipment: %s", shipment_id)

    webhook_url = (tool_config or {}).get("webhook_url") or os.getenv("SLACK_WEBHOOK_URL")

    if not webhook_url:
        return {"status": "error", "message": "No Slack webhook URL configured"}

    # Severity emoji mapping
    severity_emoji = {
        "LOW": "🟡",
        "MED": "🟠", 
        "HIGH": "🔴",
        "CRITICAL": "🚨"
    }
    emoji = severity_emoji.get(severity.upper(), "⚠️")

    # Format action items as bullet points
    action_text = "\n".join([f"• {item}" for item in action_items]) if action_items else "• No actions required"
    stakeholders_text = ", ".join(stakeholders_notified) if stakeholders_notified else "Operations"

    # Build Slack Block Kit message for rich formatting
    slack_payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Supply Chain Alert: {subject}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Shipment ID:*\n{shipment_id}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{emoji} {severity}"},
                    {"type": "mrkdwn", "text": f"*Notified:*\n{stakeholders_text}"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details:*\n{message}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Action Items:*\n{action_text}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "🤖 Automated alert from *Solace Agent Mesh* — Supply Chain Orchestration System"
                    }
                ]
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json=slack_payload,
                timeout=10
            )
            if response.status_code == 200:
                log.info("[SlackNotification] Successfully sent to #supply-chain-alerts")
                return {
                    "status": "success",
                    "channel": "#supply-chain-alerts",
                    "shipment_id": shipment_id,
                    "severity": severity,
                    "notification_sent": True,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                log.error("[SlackNotification] Failed with status %s", response.status_code)
                return {
                    "status": "error",
                    "message": f"Slack returned {response.status_code}: {response.text}"
                }
    except Exception as e:
        log.error("[SlackNotification] Error: %s", str(e))
        return {"status": "error", "message": str(e)}
