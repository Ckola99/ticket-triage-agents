# Ticket Triage Agents

A multi-agent system that takes a raw, unstructured support ticket and:
1. **Triages** it (category, ITIL-style priority P1-P4, SLA targets, drafted reply)
2. **Audits** that triage before it's accepted — checks priority/category/SLA logic and scans for POPIA-relevant personal info in the drafted reply. Rejects and retries once with feedback if wrong.
3. **Routes** approved tickets to a team and fires a Slack alert for urgent ones.

Built for the BroadVision FDE challenge in ~3 hours.

## Running it
pip install -r requirements.txt, set up `.env` with `OPENAI_API_KEY` and `SLACK_WEBHOOK_URL`, then `uvicorn app.main:app --reload`.

## What works
Full pipeline end to end, POPIA-style flagging, reject-retry loop, live Slack notification for P1s.

## What I didn't get to
Only Slack is wired as a notification adapter — in a real system this would be per-client (Teams/PagerDuty/email). No persistence — no ticket history or duplicate detection. No auth on the API.

## What's next with 3 more hours
Voice-in triage — same pipeline behind speech-to-text/text-to-speech, so a phone call gets triaged live and P1 calls bridge straight to a human.
