from dataclasses import dataclass
from typing import List

from app.models import EventType, PaymentEvent
from app.state_engine import PaymentState
from app.transition_rules import VALID_TRANSITIONS


@dataclass
class Conflict:
    conflict_type: str
    severity: str
    message: str
    payment_id: str


class ConflictDetector:

    def analyze(
        self,
        events: List[PaymentEvent],
        current_state: PaymentState
    ) -> List[Conflict]:

        conflicts = []

        if not events:
            return conflicts

        # --------------------------------------------------
        # SORT EVENTS BY ACTUAL EVENT TIME
        # --------------------------------------------------

        events = sorted(
            events,
            key=lambda event: event.event_timestamp
        )

        payment_id = events[0].payment_id

        # --------------------------------------------------
        # BUILD STATE TRANSITIONS
        # --------------------------------------------------

        previous_state = PaymentState.UNKNOWN

        for event in events:

            # ORDER.PAID is a business event.
            # We handle it separately below.
            if event.event_type == EventType.ORDER_PAID:
                continue

            # Convert event → resulting payment state
            new_state = self._event_to_state(
                event,
                previous_state
            )

            # Ignore events that don't change state
            if new_state == previous_state:
                continue

            # --------------------------------------------------
            # CHECK WHETHER TRANSITION IS VALID
            # --------------------------------------------------

            allowed_states = VALID_TRANSITIONS.get(
                previous_state,
                set()
            )

            if new_state not in allowed_states:

                conflicts.append(
                    Conflict(
                        conflict_type="INVALID_STATE_TRANSITION",
                        severity="HIGH",
                        message=(
                            f"Invalid payment transition: "
                            f"{previous_state.value} → "
                            f"{new_state.value}"
                        ),
                        payment_id=payment_id
                    )
                )

            previous_state = new_state

        # --------------------------------------------------
        # ORDER PAID WITHOUT CAPTURE
        # --------------------------------------------------

        event_types = [
            event.event_type
            for event in events
        ]

        if (
            EventType.ORDER_PAID in event_types
            and EventType.PAYMENT_CAPTURED not in event_types
        ):

            conflicts.append(
                Conflict(
                    conflict_type="ORDER_PAID_WITHOUT_CAPTURE",
                    severity="HIGH",
                    message=(
                        "Order is marked paid but no "
                        "payment capture event exists."
                    ),
                    payment_id=payment_id
                )
            )

        return conflicts

    # ------------------------------------------------------
    # EVENT → PAYMENT STATE
    # ------------------------------------------------------

    def _event_to_state(
        self,
        event: PaymentEvent,
        previous_state: PaymentState
    ) -> PaymentState:

        if event.event_type == EventType.PAYMENT_AUTHORIZED:
            return PaymentState.AUTHORIZED

        if event.event_type == EventType.PAYMENT_CAPTURED:
            return PaymentState.CAPTURED

        if event.event_type == EventType.PAYMENT_FAILED:
            return PaymentState.FAILED

        if event.event_type == EventType.REFUND_PROCESSED:
            return PaymentState.REFUNDED

        return previous_state