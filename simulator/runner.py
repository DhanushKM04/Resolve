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


def send_events(events, include_ai=True):
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
        f"{API_URL}/payments/{payment_id}/analysis",
        params={"include_ai": include_ai}
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

total_tests = 0
passed_tests = 0

benchmark_total = 0
true_positives = 0
true_negatives = 0
false_positives = 0
false_negatives = 0

def run_scenario(name, generator, expected_conflict):

    global total_tests, passed_tests
    total_tests += 1

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

        passed_tests += 1
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

def run_benchmark(iterations=100):
    global benchmark_total
    global true_positives
    global true_negatives
    global false_positives
    global false_negatives

    benchmark_scenarios = [
        (normal_payment, False),
        (failed_payment, False),
        (invalid_capture_failure, True),
        (order_paid_without_capture, True),
        (out_of_order_payment, False),
    ]

    print("\n")
    print("=" * 65)
    print("LARGE-SCALE BENCHMARK")
    print("=" * 65)

    for _ in range(iterations):
        for generator, expected_conflict in benchmark_scenarios:

            events = generator()

            # AI deliberately disabled during benchmark
            result = send_events(events, include_ai=False)

            benchmark_total += 1

            detected_conflict = result.get("conflict_count", 0) > 0

            if expected_conflict and detected_conflict:
                true_positives += 1

            elif not expected_conflict and not detected_conflict:
                true_negatives += 1

            elif not expected_conflict and detected_conflict:
                false_positives += 1

            elif expected_conflict and not detected_conflict:
                false_negatives += 1

    # ===============================
    # METRICS
    # ===============================

    total_predictions = (
        true_positives
        + true_negatives
        + false_positives
        + false_negatives
    )

    accuracy = (
        (true_positives + true_negatives)
        / total_predictions
        * 100
        if total_predictions > 0
        else 0
    )

    precision = (
        true_positives
        / (true_positives + false_positives)
        * 100
        if (true_positives + false_positives) > 0
        else 0
    )

    recall = (
        true_positives
        / (true_positives + false_negatives)
        * 100
        if (true_positives + false_negatives) > 0
        else 0
    )

    f1_score = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    print(f"Benchmark tests:    {benchmark_total}")
    print()
    print(f"True Positives:     {true_positives}")
    print(f"True Negatives:     {true_negatives}")
    print(f"False Positives:    {false_positives}")
    print(f"False Negatives:    {false_negatives}")
    print()
    print(f"Accuracy:           {accuracy:.2f}%")
    print(f"Precision:          {precision:.2f}%")
    print(f"Recall:             {recall:.2f}%")
    print(f"F1 Score:           {f1_score:.2f}%")

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

    # Run the five core scenarios first
    for name, generator, expected_conflict in scenarios:

        run_scenario(
            name,
            generator,
            expected_conflict
        )

    # Print core evaluation
    print("\n")
    print("=" * 65)
    print("EVALUATION SUMMARY")
    print("=" * 65)

    print(f"Total tests:        {total_tests}")
    print(f"Passed tests:       {passed_tests}")

    if total_tests > 0:
        accuracy = (passed_tests / total_tests) * 100
        print(f"Accuracy:           {accuracy:.2f}%")

    # Run large-scale benchmark
    run_benchmark(iterations=20)


if __name__ == "__main__":
    main()