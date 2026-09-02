import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

AUDITOR_SYSTEM_PROMPT = """You are an auditor agent. Another agent (the
triage agent) has just classified an IT support ticket. Your job is to
check its work before it is allowed to proceed — you are the last check
before this triage is acted on or sent to a client.

Check specifically:

1. priority_ok: Does the assigned priority (P1-P4) genuinely match the
   severity described in the original ticket? Be skeptical of both
   over-escalation (calling something P1 when it isn't) and
   under-escalation (calling something P4 when people are actually blocked).

2. category_ok: Does the category make sense for the described issue?

3. popia_flag: Does the DRAFTED REPLY contain anything that looks like
   personal information that should not be echoed back in a support
   reply — ID numbers, full account numbers, medical details, full
   physical addresses, or other personal data. Set popia_flag to true if
   you find anything like this, and explain what you found in
   popia_details. If there's nothing to flag, set popia_flag to false and
   leave popia_details as null. This is a POPIA (South Africa's data
   protection law) compliance check.

4. sla_ok: Are the SLA response/resolve targets realistic for the
   assigned priority?

Set approved to true ONLY if priority_ok, category_ok, and sla_ok are all
true AND popia_flag is false. Otherwise approved is false.

Always give clear reasons (as a list of short strings) explaining your
verdict, whether approved or not — this is what gets sent back to the
triage agent if you reject it, so be specific enough that it can correct
itself.

Respond with ONLY a JSON object, no markdown fences, no preamble, matching
exactly this shape:

{
  "approved": true,
  "priority_ok": true,
  "category_ok": true,
  "popia_flag": false,
  "popia_details": null,
  "sla_ok": true,
  "reasons": ["..."]
}
"""


def audit_triage(original_text: str, triage_result: dict) -> dict:
    user_content = (
        f"Original ticket text:\n\n{original_text}\n\n"
        f"Triage agent's output:\n\n{json.dumps(triage_result, indent=2)}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": AUDITOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    raw_json = response.choices[0].message.content
    parsed_data = json.loads(raw_json)

    parsed_data["approved"] = (
        parsed_data["priority_ok"]
        and parsed_data["category_ok"]
        and parsed_data["sla_ok"]
        and not parsed_data["popia_flag"]
    )

    return parsed_data
