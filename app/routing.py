"""
Routing decides WHO gets a ticket once it's been triaged and approved
by the auditor. Plain code, not an LLM call — routing
rules should be deterministic and auditable, not probabilistic.

"""

# category -> which team owns it
CATEGORY_QUEUES = {
	"network": "Network Team",
	"security": "Security Team",
	"hardware": "Field Support",
	"access": "Identity & Access Team",
	"billing": "Accounts Team",
	"other": "General Service Desk",
}

# priority -> who it's assigned to and what notification fires
PRIORITY_ROUTING = {
    "P1": {"assigned": "On-call Engineer", "channel": "slack_urgent"},
    "P2": {"assigned": "Specialist Queue", "channel": "slack_normal"},
    "P3": {"assigned": "General Queue", "channel": None},
    "P4": {"assigned": "General Queue", "channel": None},
}

def route_ticket(category: str, priority: str) -> dict:
	team = CATEGORY_QUEUES.get(category, CATEGORY_QUEUES["other"])
	priority_rule = PRIORITY_ROUTING.get(priority, PRIORITY_ROUTING["P4"])

	return {
		"team": team,
		"assigned": priority_rule["assigned"],
		"channel": priority_rule["channel"],
	}
