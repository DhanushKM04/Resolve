class PaymentInvestigator:

    def investigate(self, events, conflicts):

        investigation = {
            "summary": "",
            "root_cause": "",
            "evidence": [],
            "recommendation": ""
        }

        if not conflicts:
            investigation["summary"] = (
                "No payment inconsistencies detected."
            )
            return investigation

        first_conflict = conflicts[0]

        investigation["summary"] = (
            f"Detected {len(conflicts)} payment conflict(s)."
        )

        investigation["root_cause"] = (
            first_conflict.message
        )

        for event in events:
            investigation["evidence"].append(
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "event_timestamp": event.event_timestamp.isoformat()
                }
            )

        investigation["recommendation"] = (
            "Review the conflicting event source and "
            "downstream payment state synchronization."
        )

        return investigation