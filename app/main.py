from dotenv import load_dotenv
from app.models import TicketInput, TriageResult
from app.agents.triage import triage_ticket

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
    return triage_result
