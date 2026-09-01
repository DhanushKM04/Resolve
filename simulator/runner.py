import sys
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_PATH))

from generator import (
    normal_payment,
    failed_payment,
    invalid_capture_failure,
    order_paid_without_capture,
    out_of_order_payment,
)

(
    "OUT-OF-ORDER DELIVERY",
    out_of_order_payment,
    False,
),


API_URL = "http://127.0.0.1:8000"


def send_events(events):
    api_failed = False

    for event in events:
        response = requests.post(
            f"{API_URL}/events/process",
            json=event.model_dump(mode="json")
        )

        if response.status_code != 200:
            print(
                f"❌ Event failed: "
                f"{response.status_code}"
            )
            api_failed = True

    payment_id = events[0].payment_id

    analysis_response = requests.get(
        f"{API_URL}/payments/{payment_id}/analysis"
    )

    if analysis_response.status_code != 200:
        print(
            f"❌ Analysis failed: "
            f"{analysis_response.status_code}"
        )
        return {
            "api_failed": True
        }

    result = analysis_response.json()

    if api_failed:
        result["api_failed"] = True

    return result


def run_scenario(name, generator, expected_conflict):

    print("\n")
    print("=" * 65)
    print(name)
    print("=" * 65)

    events = generator()

    result = send_events(events)

    actual_conflict = result["conflict_count"] > 0

    print(
        f"Payment ID:       {result['payment_id']}"
    )

    print(
        f"Current state:     {result['current_state']}"
    )

    print(
        f"Conflicts found:   {result['conflict_count']}"
    )

    if not result.get("api_failed", False) and actual_conflict == expected_conflict:

        print("RESULT:            ✅ PASS")

    else:

        print("RESULT:            ❌ FAIL")

    if result["conflicts"]:

        print("\nDetected conflicts:")

        for conflict in result["conflicts"]:

            print(
                f"  🚨 {conflict['conflict_type']}"
                f" [{conflict['severity']}]"
            )

            print(
                f"     {conflict['message']}"
            )


def main():

    scenarios = [

        (
            "NORMAL PAYMENT",
            normal_payment,
            False,
        ),

        (
            "FAILED PAYMENT",
            failed_payment,
            False,
        ),

        (
            "INVALID CAPTURE → FAILURE",
            invalid_capture_failure,
            True,
        ),

        (
            "ORDER PAID WITHOUT CAPTURE",
            order_paid_without_capture,
            True,
        ),

        (
            "OUT-OF-ORDER DELIVERY",
            out_of_order_payment,
            False,
        ),
    ]

    for name, generator, expected_conflict in scenarios:

        run_scenario(
            name,
            generator,
            expected_conflict
        )

if __name__ == "__main__":
    main()