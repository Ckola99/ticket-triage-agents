# Ticket Triage Agents

A multi-agent system that takes a raw, unstructured IT support ticket — no
assumed format, could be an email dump, WhatsApp message, or a scribbled
note — and:

1. **Triages** it (Agent 1) — decides if it's even a valid ticket, then
   classifies category, assigns an ITIL-style priority (P1-P4) using
   impact x urgency, sets SLA response/resolve targets, and drafts a
   first-response reply.
2. **Audits** that triage (Agent 2) before it's accepted — checks whether
   the priority and category genuinely match the described severity,
   checks the SLA targets are realistic, and scans the drafted reply for
   anything that looks like personal information that shouldn't be
   echoed back (a lightweight POPIA compliance check). If rejected, the
   ticket goes back to Agent 1 once with the auditor's specific feedback
   before being flagged for a human.
3. **Routes** approved tickets to the right team, and fires a live Slack
   alert for urgent ones.

Built for the BroadVision FDE build challenge in ~3 focused hours.

## Why this shape

BroadVision runs SLA-backed managed IT services — service desk,
monitoring, POPIA obligations — across many clients. This mirrors the
first few minutes of what actually happens to a real ticket, with a
second agent as a genuine check before anything is acted on, per the
challenge's rule that one agent must check another's output before it's
accepted.

## Running it

pip install -r requirements.txt, then set up `.env` with
`OPENAI_API_KEY` and `SLACK_WEBHOOK_URL`, then `uvicorn app.main:app --reload`.

## A real bug I hit and fixed

Early on, the Auditor's own JSON output claimed `approved: false` even
when every individual check (`priority_ok`, `category_ok`, `sla_ok`,
`popia_flag`) was correct and should have combined to `true`. The model
was reliably right on each individual judgment but unreliable at
computing the AND across them itself. Fix: stop trusting the model's own
`approved` field, and compute it deterministically in Python instead
from the four fields it does judge well. Worth noting as a general
lesson — don't ask an LLM to do exact boolean logic in its head if you
can compute it yourself from its outputs.

## A genuine disagreement, not just an error

Fed the ticket "urgent!!! my mouse battery is a bit low, please send
someone today or I cannot work at all" — Agent 1 reasonably assigned
P3 (a workaround exists: wired mouse, battery swap). The Auditor
disagreed, arguing the user's stated inability to work justified at
least P2. After one retry, they still disagreed and the ticket
correctly fell through to human review. This is less a "bug" and more
a real judgment call — should priority follow objective technical
severity, or self-reported user impact — that a human triager would
also have to make.

## What works

- Full pipeline end to end: raw text in -> triage -> audit -> retry
  once if rejected -> routing decision -> live Slack alert for P1s
- POPIA-style scan on the drafted reply (tested against a fake ID
  number, correctly flagged)
- A minimal frontend showing the triage, audit verdict, and routing
  outcome as readable cards, not raw JSON

## What I did not get to

- **The loop isn't closed with the customer.** The drafted reply is
  generated but never actually sent anywhere — right now this is an
  internal triage tool, not a system that talks back to whoever raised
  the ticket.
- Only Slack is wired as a notification adapter. In a real multi-client
  system, routing/notification would be per-client config (Slack for
  one client, Teams or PagerDuty for another) — `notify.py` and
  `routing.py` are written with that extension point in mind but only
  one adapter exists.
- No persistence — nothing is stored between requests, so no ticket
  history, no duplicate-ticket detection, and rejected/corrected triage
  pairs aren't fed back in to improve future accuracy.
- No auth on the API, and it isn't deployed/dockerized.

## What I'd build next with 3 more hours

Two directions, in priority order:

1. **Close the loop with the customer.** Once a ticket is approved,
   actually send the drafted reply back (email/WhatsApp), and follow up
   with a real status update tied to the routing decision ("your ticket
   has been triaged as P1 and escalated to our on-call engineer") -
   right now that information stays internal.
2. **Voice-in triage.** Same pipeline, but the entry point is a phone
   call: speech-to-text feeds the same triage/audit pipeline,
   text-to-speech reads back the estimated priority and wait time, and
   a live P1 call gets bridged straight to a human instead of queued.
