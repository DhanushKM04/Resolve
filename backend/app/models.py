from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    PAYMENT_AUTHORIZED = "payment.authorized"
    PAYMENT_CAPTURED = "payment.captured"
    PAYMENT_FAILED = "payment.failed"
    ORDER_PAID = "order.paid"
    REFUND_CREATED = "refund.created"
    REFUND_PROCESSED = "refund.processed"
    WEBHOOK_DELIVERED = "webhook.delivered"
    WEBHOOK_FAILED = "webhook.failed"


class PaymentEvent(BaseModel):
    event_id: str = Field(..., min_length=1)
    payment_id: str = Field(..., min_length=1)
    order_id: str = Field(..., min_length=1)

    event_type: EventType

    amount: int = Field(..., ge=0)
    currency: str = Field(default="INR", min_length=3, max_length=3)

    event_timestamp: datetime
    received_timestamp: datetime

    source: str = Field(default="simulator", min_length=1)