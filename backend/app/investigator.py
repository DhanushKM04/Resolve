import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

ai_call_count = 0


class PaymentInvestigator:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=self.api_key
        )

    def investigate(self, events, conflicts):

        evidence = []

        for event in events:
            evidence.append(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "event_timestamp": (
                        event.event_timestamp.isoformat()
                    )
                }
            )

        if not conflicts:
            return {
                "summary": "No payment inconsistencies detected.",
                "root_cause": "",
                "evidence": evidence,
                "recommendation": ""
            }

        conflict_data = [
            {
                "conflict_type": conflict.conflict_type,
                "severity": conflict.severity,
                "message": conflict.message
            }
            for conflict in conflicts
        ]

        prompt = f"""
You are a payment systems investigator.

Analyze this synthetic payment transaction.

CONFLICTS:
{conflict_data}

EVENT EVIDENCE:
{evidence}

Return a concise investigation with exactly these sections:

SUMMARY:
ROOT CAUSE:
RECOMMENDATION:

Do not invent facts.
Use only the supplied evidence.

The recommendation must be advisory only.
Do not recommend executing, modifying, injecting, retrying,
capturing, refunding, voiding, or otherwise mutating a payment.

Recommend only actions such as:
- verifying payment status with the payment provider
- reconciling event history
- inspecting logs
- reviewing payment/order state transitions
- identifying the system responsible for the inconsistency

Never instruct an engineer to perform a financial action directly.

Keep the response under 150 words.
"""
        global ai_call_count
        ai_call_count += 1

        try:
            response = self.client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            ai_text = response.text.strip()
            recommendation = ""
            if "RECOMMENDATION:" in ai_text:
                recommendation = ai_text.split(
                    "RECOMMENDATION:", 1
                    )[1].strip()

            return {
                "summary": ai_text,
                "root_cause": conflicts[0].message,
                "evidence": evidence,
                "recommendation": recommendation
            }

        except Exception:
            # Safe fallback if Gemini is unavailable
            return {
                "summary": (
                    f"Detected {len(conflicts)} payment conflict(s)."
                ),
                "root_cause": conflicts[0].message,
                "evidence": evidence,
                "recommendation": (
                    "Review the conflicting event source and "
                    "downstream payment state synchronization."
                )
            }