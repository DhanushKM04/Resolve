from fastapi import FastAPI

from app.models import PaymentEvent
from app.state_engine import StateEngine
from app.conflict_detector import ConflictDetector
from app.database import initialize_database, save_event


app = FastAPI(
    title="Resolve",
    description="AI-powered payment state intelligence",
    version="0.1.0"
)

state_engine = StateEngine()
initialize_database()
conflict_detector = ConflictDetector()


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
    save_event(event)

    return {
       "payment_id": event.payment_id,
        "current_state": result["state"],
        "duplicate": result["duplicate"]
    }


@app.get("/payments/{payment_id}/analysis")
def analyze_payment(payment_id: str):

    events = state_engine.events.get(payment_id, [])

    state = state_engine.get_state(payment_id)

    conflicts = conflict_detector.analyze(
        events,
        state
    )

    return {
        "payment_id": payment_id,
        "event_count": len(events),
        "event_ids": [event.event_id for event in events],
        "current_state": state,
        "conflict_count": len(conflicts),
        "conflicts": conflicts
    }