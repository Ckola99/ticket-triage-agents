import os
import requests
from dotenv import load_dotenv

load_dotenv()
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")


def notify_slack(ticket_summary: str, priority: str, category: str) -> bool:
    """Fires a Slack message. Returns True if it actually sent."""
    if not SLACK_WEBHOOK_URL:
        print("[notify] No SLACK_WEBHOOK_URL set — skipping.")
        return False

    payload = {
        "text": f":rotating_light: *{priority} ticket* ({category})\n{ticket_summary}"
    }

    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        return resp.status_code == 200
    except requests.RequestException as e:
        print(f"[notify] Slack webhook failed: {e}")
        return False


def dispatch_notification(channel: str | None, ticket_summary: str, priority: str, category: str) -> str | None:
    """Looks at the routing decision's channel and fires the right adapter."""
    
    if channel in ("slack_urgent", "slack_normal"):
        sent = notify_slack(ticket_summary, priority, category)
        return "slack" if sent else None
    return None
