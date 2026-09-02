from pydantic import BaseModel
from typing import Optional, List, Literal

class TicketInput(BaseModel):
	text: str

class TriageResult(BaseModel):
	is_valid_ticket: bool
	category: Literal["network", "security", "hardware", "access", "billing", "other"]
	priority: Literal["P1", "P2", "P3", "P4"]
	sla_response_minutes: int
	sla_resolve_hours: int
	priority_reasoning: str
	drafted_reply: str

class AuditResult(BaseModel):
	approved: bool
	priority_ok: bool
	category_ok: bool
	popia_flag: bool
	popia_details: Optional[str] = None
	sla_ok: bool
	reasons: List[str]

class RoutingResult(BaseModel):
	team: str
	assigned: str
	channel: Optional[str] = None

class TriageResponse(BaseModel):
	original_ticket: str
	triage_result: TriageResult
	audit_result: AuditResult
	retried: bool
	routing_result: Optional[RoutingResult] = None
	flagged: bool
