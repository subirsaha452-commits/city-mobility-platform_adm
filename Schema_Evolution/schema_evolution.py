"""
Part 2.1.3 — Schema Evolution.

New requirement: add a 'battery_level' field (integer, 0-100) to all
BATTERY events.

RELATIONAL (PostgreSQL):
  ALTER TABLE events ADD COLUMN battery_level INT;
  - The column is nullable so existing non-BATTERY rows are unaffected.
  - A CHECK constraint enforces 0-100 for BATTERY rows.
  - Existing BATTERY rows get NULL (unknown historic value) or can be
    back-filled with a default.

DOCUMENT (MongoDB):
  db.trips.updateMany(
      {"events.type": "BATTERY"},
      {"$set": {"events.$[e].battery_level": <value>}},
      arrayFilters=[{"e.type": "BATTERY"}]
  )
  - MongoDB's flexible schema means NO migration is required for other
    documents — only BATTERY events gain the new field.
  - Existing documents without BATTERY events are completely untouched.

Key difference:
  PostgreSQL requires a DDL statement (ALTER TABLE) that locks the table
  briefly and adds a nullable column to EVERY row — even non-BATTERY ones.
  MongoDB needs no DDL; each document is updated individually and only
  affected documents change, making the evolution truly schema-less.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import time

from app.postgres.db import get_postgres_conn
from app.mongo.db    import get_mongo_db


# ── PostgreSQL ──────────────────────────────────────────────────────────────

def pg_add_battery_level(conn):
    """
    Step 1 – add nullable column (safe, no data loss).
    Step 2 – add CHECK so future inserts are validated.
    Step 3 – back-fill existing BATTERY rows with a synthetic value.
    """
    cur = conn.cursor()

    # Step 1: add the column if it does not exist yet
    cur.execute("""
        ALTER TABLE events
        ADD COLUMN IF NOT EXISTS battery_level INT;
    """)

    # Step 2: enforce 0-100 range for non-null values
    cur.execute("""
        ALTER TABLE events
        DROP CONSTRAINT IF EXISTS chk_battery_level;
    """)
    cur.execute("""
        ALTER TABLE events
        ADD CONSTRAINT chk_battery_level
            CHECK (battery_level IS NULL OR (battery_level >= 0 AND battery_level <= 100));
    """)

    # Step 3: back-fill existing BATTERY rows (unknown historic value → 50)
    cur.execute("""
        UPDATE events
        SET    battery_level = 50
        WHERE  type = 'BATTERY'
          AND  battery_level IS NULL;
    """)

    conn.commit()
    cur.execute("SELECT COUNT(*) FROM events WHERE type = 'BATTERY'")
    n = cur.fetchone()[0]
    cur.close()
    print(f"[PostgreSQL] battery_level column added. {n} BATTERY rows back-filled.")


def pg_verify(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT event_id, trip_id, type, value, battery_level
        FROM   events
        WHERE  type = 'BATTERY'
        LIMIT  5
    """)
    rows = cur.fetchall()
    cur.close()
    print("[PostgreSQL] Sample BATTERY events after evolution:")
    for r in rows:
        print(f"  event_id={r[0]} trip_id={r[1]} type={r[2]} "
              f"value={r[3]} battery_level={r[4]}")


# ── MongoDB ──────────────────────────────────────────────────────────────────

def mongo_add_battery_level(db):
    """
    Use positional arrayFilters to update only the BATTERY sub-documents
    inside the embedded events array.  Non-BATTERY events and unrelated
    trips are completely untouched.
    """
    # Count trips that have at least one BATTERY event
    n_before = db.trips.count_documents({"events.type": "BATTERY"})

    result = db.trips.update_many(
        {"events.type": "BATTERY"},
        {"$set": {"events.$[e].battery_level": 50}},
        array_filters=[{"e.type": "BATTERY"}]
    )

    print(f"[MongoDB] battery_level field added.")
    print(f"  Trips containing BATTERY events : {n_before}")
    print(f"  Trips matched / modified        : "
          f"{result.matched_count} / {result.modified_count}")


def mongo_verify(db):
    trips = list(db.trips.find(
        {"events.type": "BATTERY"},
        {"_id": 0, "trip_id": 1, "events": 1}
    ).limit(3))
    print("[MongoDB] Sample embedded BATTERY events after evolution:")
    for trip in trips:
        for ev in trip["events"]:
            if ev["type"] == "BATTERY":
                print(f"  trip_id={trip['trip_id']} "
                      f"type={ev['type']} "
                      f"battery_level={ev.get('battery_level', 'MISSING')}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("Schema Evolution: adding battery_level to BATTERY events")
    print("=" * 55)

    # PostgreSQL
    t0   = time.time()
    conn = get_postgres_conn()
    pg_add_battery_level(conn)
    pg_verify(conn)
    conn.close()
    print(f"  PostgreSQL evolution completed in {time.time()-t0:.4f}s\n")

    # MongoDB
    t0 = time.time()
    db = get_mongo_db()
    mongo_add_battery_level(db)
    mongo_verify(db)
    print(f"  MongoDB evolution completed in {time.time()-t0:.4f}s")
