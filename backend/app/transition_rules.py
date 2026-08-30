from app.state_engine import PaymentState


VALID_TRANSITIONS = {
    PaymentState.UNKNOWN: {
        PaymentState.AUTHORIZED,
        PaymentState.FAILED,
    },

    PaymentState.AUTHORIZED: {
        PaymentState.CAPTURED,
        PaymentState.FAILED,
    },

    PaymentState.FAILED: {
        PaymentState.AUTHORIZED,
        PaymentState.FAILED,
    },

    PaymentState.CAPTURED: {
        PaymentState.PAID,
        PaymentState.REFUNDED,
    },

    PaymentState.PAID: {
        PaymentState.REFUNDED,
    },

    PaymentState.REFUNDED: set(),
}