"""
Part 1 — Document Model: MongoDB schema design and data population.

Design decision — HYBRID approach:
  Collection 'users':    flat document  {user_id, name, surname, birthdate, country}
  Collection 'stations': flat document  {station_id, name, city, capacity}
  Collection 'trips':    trip document  {trip_id, user_id, start_station_id,
                                         end_station_id, start_time, end_time,
                                         total_cost, events: [...]}
                         events are EMBEDDED inside trips.

Why embed events in trips?
  + Events are never queried independently — they always appear in the context
    of a trip. Embedding avoids $lookup and speeds up Query 4 (ERROR filter).
  + Events per trip are bounded (<=10), so documents stay within MongoDB's
    16 MB limit.

Why reference users and stations?
  + One user appears in many trips (high fan-out). Embedding would duplicate
    user data across thousands of trip documents.
  + Stations are also shared across many trips — referencing avoids stale
    copies if station data changes.

vs Relational model:
  SQL requires events in a separate table (no native nested records) and uses
  JOINs. MongoDB can embed events — this is its key advantage for Q4, but
  makes cross-document aggregations (Q1) slightly more complex (needs $lookup).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import copy
import time
from app.mongo.db import get_mongo_db
from app.utils.data_generator import generate_dataset


def setup_indexes(db):
    db.users.drop()
    db.stations.drop()
    db.trips.drop()

    db.users.create_index("user_id", unique=True)
    db.stations.create_index("station_id", unique=True)
    db.trips.create_index("trip_id",         unique=True)
    db.trips.create_index("user_id")
    db.trips.create_index("start_station_id")
    db.trips.create_index("end_station_id")
    db.trips.create_index("events.type")      # enables fast Q4 filter
    print("[MongoDB] Collections and indexes created.")


def populate(db, dataset):
    # Deep-copy before inserting so PyMongo's _id injection does not
    # mutate the original dicts (which are reused by the Neo4j setup).
    if dataset["users"]:
        db.users.insert_many(copy.deepcopy(dataset["users"]))
    if dataset["stations"]:
        db.stations.insert_many(copy.deepcopy(dataset["stations"]))

    # Group events by trip_id, then embed them
    by_trip = {}
    for e in dataset["events"]:
        by_trip.setdefault(e["trip_id"], []).append({
            "timestamp": e["timestamp"],
            "type":      e["type"],
            "value":     e["value"]
        })

    trip_docs = []
    for t in dataset["trips"]:
        doc = dict(t)
        doc["events"] = by_trip.get(t["trip_id"], [])
        trip_docs.append(doc)

    if trip_docs:
        db.trips.insert_many(copy.deepcopy(trip_docs))

    print(f"  Inserted {len(dataset['users'])} users, {len(dataset['stations'])} stations,"
          f" {len(dataset['trips'])} trips (events embedded).")


if __name__ == "__main__":
    db = get_mongo_db()
    setup_indexes(db)
    t0   = time.time()
    data = generate_dataset(n_users=1000, n_trips=10000, events_per_trip=2)
    populate(db, data)
    print(f"Done in {time.time()-t0:.2f}s")
