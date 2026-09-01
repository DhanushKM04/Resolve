from fastapi import FastAPI
from app.models import EventType, PaymentEvent
from app.state_engine import StateEngine
from app.conflict_detector import ConflictDetector
from app.database import initialize_database, save_event, get_events, mark_duplicate
from app.investigator import PaymentInvestigator

app = FastAPI(
    title="Resolve",
    description="AI-powered payment state intelligence",
    version="0.1.0"
)

state_engine = StateEngine()
initialize_database()
conflict_detector = ConflictDetector()
investigator = PaymentInvestigator()


@app.get("/")
def root():
    return {
        "service": "Resolve",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/events/test")
def test_event(event: PaymentEvent):
    return {
        "message": "Event accepted",
        "event": event
    }


@app.post("/events/process")

def process_event(event: PaymentEvent):

    result = state_engine.add_event(event)

    if result["duplicate"]:
        mark_duplicate(event.event_id)
    else:
        save_event(event)
        result["state"] = state_engine.get_state(event.payment_id)

    return {
        "payment_id": event.payment_id,
        "current_state": result["state"],
        "duplicate": result["duplicate"]
    }


@app.get("/payments/{payment_id}/analysis")
def analyze_payment(payment_id: str):

    rows = get_events(payment_id)

    events = [
        PaymentEvent(
            event_id=row["event_id"],
            payment_id=row["payment_id"],
            order_id=row["order_id"],
            event_type=EventType(row["event_type"]),
            amount=row["amount"],
            currency=row["currency"],
            event_timestamp=row["event_timestamp"],
            received_timestamp=row["received_timestamp"],
            source=row["source"],
        )
        for row in rows
    ]

    state = state_engine.get_state(payment_id)

    conflicts = conflict_detector.analyze(
        events,
        state
    )

    investigation = investigator.investigate(
    events,
    conflicts
    )

    duplicates = state_engine.duplicate_events.get(
    payment_id,
    []
    )

    return {
        "payment_id": payment_id,
        "event_count": len(events),
        "event_ids": [
            event.event_id
            for event in events
        ],
        "current_state": state,
        "conflict_count": len(conflicts) + len(duplicates),
        "conflicts": conflicts + [
            {
                "conflict_type": "DUPLICATE_EVENT",
                "severity": "MEDIUM",
                "message": f"Duplicate event detected: {event_id}",
                "payment_id": payment_id
            }
            for event_id in duplicates
        ],
        "investigation": investigation
    }


@app.get("/stats/ai")
def get_ai_stats():
    from app import investigator
    return {
        "gemini_calls": investigator.ai_call_count
        }