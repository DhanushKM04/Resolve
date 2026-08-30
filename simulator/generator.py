from datetime import datetime, timedelta
from uuid import uuid4

from app.models import EventType, PaymentEvent


def create_event(
    payment_id: str,
    order_id: str,
    event_type: EventType,
    amount: int,
    event_time: datetime,
    received_time: datetime | None = None,
):
    if received_time is None:
        received_time = event_time

    return PaymentEvent(
        event_id=f"evt_{uuid4().hex[:8]}",
        payment_id=payment_id,
        order_id=order_id,
        event_type=event_type,
        amount=amount,
        currency="INR",
        event_timestamp=event_time,
        received_timestamp=received_time,
        source="simulator",
    )


# ======================================================
# SCENARIO 1 — NORMAL PAYMENT
# ======================================================

def normal_payment():

    payment_id = f"pay_{uuid4().hex[:8]}"
    order_id = f"order_{uuid4().hex[:8]}"

    start = datetime.now()

    return [

        create_event(
            payment_id,
            order_id,
            EventType.PAYMENT_AUTHORIZED,
            4999,
            start,
        ),

        create_event(
            payment_id,
            order_id,
            EventType.PAYMENT_CAPTURED,
            4999,
            start + timedelta(seconds=2),
        ),

        create_event(
            payment_id,
            order_id,
            EventType.ORDER_PAID,
            4999,
            start + timedelta(seconds=3),
        ),
    ]


# ======================================================
# SCENARIO 2 — FAILED PAYMENT
# ======================================================

def failed_payment():

    payment_id = f"pay_{uuid4().hex[:8]}"
    order_id = f"order_{uuid4().hex[:8]}"

    start = datetime.now()

    return [

        create_event(
            payment_id,
            order_id,
            EventType.PAYMENT_AUTHORIZED,
            4999,
            start,
        ),

        create_event(
            payment_id,
            order_id,
            EventType.PAYMENT_FAILED,
            4999,
            start + timedelta(seconds=2),
        ),
    ]


# ======================================================
# SCENARIO 3 — INVALID CAPTURE → FAILURE
# ======================================================

def invalid_capture_failure():

    payment_id = f"pay_{uuid4().hex[:8]}"
    order_id = f"order_{uuid4().hex[:8]}"

    start = datetime.now()

    return [

        create_event(
            payment_id,
            order_id,
            EventType.PAYMENT_AUTHORIZED,
            4999,
            start,
        ),

        create_event(
            payment_id,
            order_id,
            EventType.PAYMENT_CAPTURED,
            4999,
            start + timedelta(seconds=2),
        ),

        create_event(
            payment_id,
            order_id,
            EventType.PAYMENT_FAILED,
            4999,
            start + timedelta(seconds=4),
        ),
    ]


# ======================================================
# SCENARIO 4 — ORDER PAID WITHOUT CAPTURE
# ======================================================

def order_paid_without_capture():

    payment_id = f"pay_{uuid4().hex[:8]}"
    order_id = f"order_{uuid4().hex[:8]}"

    start = datetime.now()

    return [

        create_event(
            payment_id,
            order_id,
            EventType.PAYMENT_AUTHORIZED,
            4999,
            start,
        ),

        create_event(
            payment_id,
            order_id,
            EventType.ORDER_PAID,
            4999,
            start + timedelta(seconds=2),
        ),
    ]

# ======================================================
# SCENARIO 5 — Out-of-order delivery
# ======================================================


def out_of_order_payment():

    payment_id = f"pay_{uuid4().hex[:8]}"
    order_id = f"order_{uuid4().hex[:8]}"

    start = datetime.now()

    authorized = create_event(
        payment_id,
        order_id,
        EventType.PAYMENT_AUTHORIZED,
        4999,
        start,
        start + timedelta(seconds=5),
    )

    captured = create_event(
        payment_id,
        order_id,
        EventType.PAYMENT_CAPTURED,
        4999,
        start + timedelta(seconds=2),
        start + timedelta(seconds=3),
    )

    # IMPORTANT:
    # Return them in RECEIVED order,
    # not event order.

    return [
        captured,
        authorized,
    ]