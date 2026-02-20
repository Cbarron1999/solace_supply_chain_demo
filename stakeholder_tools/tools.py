import os
from datetime import datetime
from typing import Any, Dict, Optional

def send_slack_notification(
    shipment_id: str,
    severity: str,
    subject: str,
    message: str,
    stakeholders_notified: list[str],
    action_items: list[str],
    tool_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Sends a Slack notification to the #supply-chain-alerts channel.

    Args:
        shipment_id: The shipment ID
        severity: LOW, MED, HIGH, or CRITICAL
        subject: Notification subject line
        message: Main notification message body
        stakeholders_notified: List of stakeholder groups notified
        action_items: List of recommended action items
    """
    try:
        import requests
        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        if not webhook_url:
            return {"status": "error", "message": "SLACK_WEBHOOK_URL not set"}

        severity_emoji = {"LOW": "🟡", "MED": "🟠", "HIGH": "🔴", "CRITICAL": "🚨"}.get(severity.upper(), "⚠️")
        action_text = "\n".join([f"• {item}" for item in action_items]) if action_items else "• No actions required"
        stakeholders_text = ", ".join(stakeholders_notified) if stakeholders_notified else "Operations"

        payload = {
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": f"{severity_emoji} Supply Chain Alert: {subject}"}},
                {"type": "section", "fields": [
                    {"type": "mrkdwn", "text": f"*Shipment ID:*\n{shipment_id}"},
                    {"type": "mrkdwn", "text": f"*Severity:*\n{severity_emoji} {severity}"},
                    {"type": "mrkdwn", "text": f"*Stakeholders:*\n{stakeholders_text}"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"}
                ]},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Summary:*\n{message}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Action Items:*\n{action_text}"}},
                {"type": "divider"},
                {"type": "context", "elements": [{"type": "mrkdwn", "text": "🤖 Automated alert from Solace Agent Mesh"}]}
            ]
        }

        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            return {"status": "success", "message": f"Slack notification sent for {shipment_id}"}
        else:
            return {"status": "error", "message": f"Slack returned {response.status_code}: {response.text}"}

    except Exception as e:
        return {"status": "error", "message": f"Tool exception: {str(e)}"}
