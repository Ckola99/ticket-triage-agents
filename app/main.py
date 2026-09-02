from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

app = FastAPI(title="Ticket Triage Agents")


@app.get("/")
def root():
    return {"message": "Ticket Triage Agents is running"}
