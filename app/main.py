from dotenv import load_dotenv
from app.models import TicketInput, TriageResult, AuditResult
from app.agents.triage import triage_ticket
from app.agents.auditor import audit_triage

load_dotenv()

from fastapi import FastAPI

app = FastAPI(title="Ticket Triage Agents")

@app.get("/")
def root():
    return {"message": "Ticket Triage Agents is running"}

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

     return {
        "triage": triage_result,
        "audit": audit_result,
        "retried": retried,
        "flagged": flagged,
     }
