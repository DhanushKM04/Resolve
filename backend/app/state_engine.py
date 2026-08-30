from enum import Enum

from app.models import EventType, PaymentEvent


class PaymentState(str, Enum):
    UNKNOWN = "unknown"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    PAID = "paid"
    REFUNDED = "refunded"


class StateEngine:

    def __init__(self):
        self.events = {}
        self.processed_event_ids = set()

    def add_event(self, event: PaymentEvent):

        # ---------------------------------------------
        # IDEMPOTENCY CHECK
        # ---------------------------------------------

        if event.event_id in self.processed_event_ids:
            return {
                "state": self.get_state(event.payment_id),
                "duplicate": True
            }

        self.processed_event_ids.add(event.event_id)

        # ---------------------------------------------
        # STORE EVENT
        # ---------------------------------------------

        payment_id = event.payment_id

        if payment_id not in self.events:
            self.events[payment_id] = []

        self.events[payment_id].append(event)

        # Calculate current state
        state = self.get_state(payment_id)

        return {
            "state": state,
            "duplicate": False
        }

    def get_state(self, payment_id: str) -> PaymentState:

        events = self.events.get(payment_id, [])

        if not events:
            return PaymentState.UNKNOWN

        # ---------------------------------------------
        # IMPORTANT:
        # Sort by when the event actually happened,
        # NOT when our system received it.
        # ---------------------------------------------

        events = sorted(
            events,
            key=lambda event: event.event_timestamp
        )

        state = PaymentState.UNKNOWN

        for event in events:

            if event.event_type == EventType.PAYMENT_AUTHORIZED:
                state = PaymentState.AUTHORIZED

            elif event.event_type == EventType.PAYMENT_CAPTURED:
                state = PaymentState.CAPTURED

            elif event.event_type == EventType.PAYMENT_FAILED:
                state = PaymentState.FAILED

            elif event.event_type == EventType.ORDER_PAID:
                state = PaymentState.PAID

            elif event.event_type == EventType.REFUND_PROCESSED:
                state = PaymentState.REFUNDED

        return state