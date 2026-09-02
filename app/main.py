from dotenv import load_dotenv
from app.models import TicketInput, TriageResult, AuditResult
from app.agents.triage import triage_ticket
from app.agents.auditor import audit_triage
from app.routing import route_ticket
from app.notify import dispatch_notification

load_dotenv()

from fastapi import FastAPI

app = FastAPI(title="Ticket Triage Agents")

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/")
def root():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/triage")
def process_ticket(ticket: TicketInput):
    triage_raw = triage_ticket(ticket.text)
    triage_result = TriageResult(**triage_raw)

    audit_raw = audit_triage(ticket.text, triage_raw)
    audit_result = AuditResult(**audit_raw)

    retried = False
    flagged = False

    if not audit_result.approved:
        retried = True
        feedback = "; ".join(audit_result.reasons)
        triage_raw = triage_ticket(ticket.text, feedback=feedback)
        triage_result = TriageResult(**triage_raw)

        audit_raw = audit_triage(ticket.text, triage_raw)
        audit_result = AuditResult(**audit_raw)

        if not audit_result.approved:
            flagged = True

    routing_result = None

    if audit_result.approved:
        routing_raw = route_ticket(triage_result.category, triage_result.priority)
        notified_via = dispatch_notification(
            routing_raw["channel"],
            ticket_summary=ticket.text[:200],
            priority=triage_result.priority,
            category=triage_result.category,
        )
        routing_raw["channel"] = notified_via
        routing_result = routing_raw

    return {
        "triage": triage_result,
        "audit": audit_result,
        "retried": retried,
        "flagged": flagged,
        "routing": routing_result,
    }
