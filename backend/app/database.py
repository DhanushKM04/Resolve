import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent.parent / "resolve.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS payment_events (
            event_id TEXT PRIMARY KEY,
            payment_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            currency TEXT NOT NULL,
            event_timestamp TEXT NOT NULL,
            received_timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            is_duplicate INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    connection.commit()
    try:
        connection.execute(
            """
            ALTER TABLE payment_events
            ADD COLUMN is_duplicate INTEGER NOT NULL DEFAULT 0
            """
        )
        connection.commit()
    except sqlite3.OperationalError:
        pass
    connection.close()


def save_event(event):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO payment_events (
            event_id,
            payment_id,
            order_id,
            event_type,
            amount,
            currency,
            event_timestamp,
            received_timestamp,
            source,
            is_duplicate
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.event_id,
            event.payment_id,
            event.order_id,
            event.event_type.value,
            event.amount,
            event.currency,
            event.event_timestamp.isoformat(),
            event.received_timestamp.isoformat(),
            event.source,
            0
        )
    )

    connection.commit()
    connection.close()


def get_events(payment_id):
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT *
        FROM payment_events
        WHERE payment_id = ?
        ORDER BY event_timestamp ASC
        """,
        (payment_id,)
        ).fetchall()
    connection.close()
    return rows

def mark_duplicate(event_id):

    connection = get_connection()

    connection.execute(
        """
        UPDATE payment_events
        SET is_duplicate = 1
        WHERE event_id = ?
        """,
        (event_id,)
    )

    connection.commit()
    connection.close()

def event_exists(event_id):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT 1
        FROM payment_events
        WHERE event_id = ?
        """,
        (event_id,)
    ).fetchone()

    connection.close()

    return row is not None