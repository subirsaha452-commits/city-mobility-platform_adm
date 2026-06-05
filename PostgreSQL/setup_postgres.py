"""
Part 1 — Relational Model: PostgreSQL schema creation and data population.

Schema design (referencing model):
  users(user_id PK, name, surname, birthdate, country)
  stations(station_id PK, name, city, capacity)
  trips(trip_id PK, user_id FK, start_station_id FK, end_station_id FK,
        start_time, end_time, total_cost)
  events(event_id PK, trip_id FK, timestamp, type, value)

Design rationale:
  - All four entities are separate tables (fully normalised).
  - Events reference trips via FK — NOT embedded — because SQL does not
    natively support nested records; JOINs are the relational idiom.
  - Indexes on FK columns and events.type speed up all four queries.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from app.postgres.db import get_postgres_conn
from app.utils.data_generator import generate_dataset

SCHEMA = """
DROP TABLE IF EXISTS events   CASCADE;
DROP TABLE IF EXISTS trips    CASCADE;
DROP TABLE IF EXISTS stations CASCADE;
DROP TABLE IF EXISTS users    CASCADE;

CREATE TABLE users (
    user_id   SERIAL PRIMARY KEY,
    name      VARCHAR(50)  NOT NULL,
    surname   VARCHAR(50)  NOT NULL,
    birthdate DATE         NOT NULL,
    country   VARCHAR(50)  NOT NULL
);

CREATE TABLE stations (
    station_id SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    city       VARCHAR(50)  NOT NULL,
    capacity   INT          NOT NULL
);

CREATE TABLE trips (
    trip_id          SERIAL    PRIMARY KEY,
    user_id          INT       REFERENCES users(user_id),
    start_station_id INT       REFERENCES stations(station_id),
    end_station_id   INT       REFERENCES stations(station_id),
    start_time       TIMESTAMP NOT NULL,
    end_time         TIMESTAMP NOT NULL,
    total_cost       FLOAT     NOT NULL
);

CREATE TABLE events (
    event_id  SERIAL    PRIMARY KEY,
    trip_id   INT       REFERENCES trips(trip_id),
    timestamp TIMESTAMP NOT NULL,
    type      VARCHAR(20) NOT NULL,
    value     TEXT        NOT NULL
);

CREATE INDEX idx_trips_user     ON trips(user_id);
CREATE INDEX idx_trips_start_st ON trips(start_station_id);
CREATE INDEX idx_trips_end_st   ON trips(end_station_id);
CREATE INDEX idx_events_trip    ON events(trip_id);
CREATE INDEX idx_events_type    ON events(type);
"""


def create_schema(conn):
    cur = conn.cursor()
    cur.execute(SCHEMA)
    conn.commit()
    cur.close()
    print("[PostgreSQL] Schema created.")


def populate(conn, dataset):
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO users (user_id, name, surname, birthdate, country) VALUES (%s,%s,%s,%s,%s)",
        [(u["user_id"], u["name"], u["surname"], u["birthdate"], u["country"])
         for u in dataset["users"]]
    )
    cur.executemany(
        "INSERT INTO stations (station_id, name, city, capacity) VALUES (%s,%s,%s,%s)",
        [(s["station_id"], s["name"], s["city"], s["capacity"])
         for s in dataset["stations"]]
    )
    cur.executemany(
        "INSERT INTO trips (trip_id, user_id, start_station_id, end_station_id,"
        " start_time, end_time, total_cost) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        [(t["trip_id"], t["user_id"], t["start_station_id"], t["end_station_id"],
          t["start_time"], t["end_time"], t["total_cost"]) for t in dataset["trips"]]
    )
    if dataset["events"]:
        cur.executemany(
            "INSERT INTO events (event_id, trip_id, timestamp, type, value)"
            " VALUES (%s,%s,%s,%s,%s)",
            [(e["event_id"], e["trip_id"], e["timestamp"], e["type"], e["value"])
             for e in dataset["events"]]
        )
    conn.commit()
    # sync sequences
    for tbl, col in [("users","user_id"),("stations","station_id"),
                     ("trips","trip_id"),("events","event_id")]:
        cur.execute(f"SELECT setval(pg_get_serial_sequence('{tbl}','{col}'),"
                    f"COALESCE((SELECT MAX({col}) FROM {tbl}),1))")
    conn.commit()
    cur.close()
    print(f"  Inserted {len(dataset['users'])} users, {len(dataset['stations'])} stations,"
          f" {len(dataset['trips'])} trips, {len(dataset['events'])} events.")


if __name__ == "__main__":
    conn = get_postgres_conn()
    create_schema(conn)
    t0   = time.time()
    data = generate_dataset(n_users=1000, n_trips=10000, events_per_trip=2)
    populate(conn, data)
    conn.close()
    print(f"Done in {time.time()-t0:.2f}s")
