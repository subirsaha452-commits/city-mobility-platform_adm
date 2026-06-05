"""
Part 2 — Graph Model: Neo4j schema design and data population.

Graph structure (as specified in project):
  Nodes:  (:User    {user_id, name, surname, country})
          (:Trip    {trip_id, start_time, end_time, total_cost})
          (:Station {station_id, name, city})
  Edges:  (:User)-[:PERFORMED]->(:Trip)
          (:Trip)-[:STARTS_AT]->(:Station)
          (:Trip)-[:ENDS_AT]->(:Station)

Data is loaded in batches via UNWIND to avoid memory issues on large datasets.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from app.neo4j.db import get_neo4j_driver
from app.utils.data_generator import generate_dataset

BATCH = 500


def _chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def clear_and_constrain(session):
    session.run("MATCH (n) DETACH DELETE n")
    for label, prop in [("User","user_id"), ("Station","station_id"), ("Trip","trip_id")]:
        session.run(
            f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
        )
    print("[Neo4j] Cleared graph and ensured constraints.")


def load_users(session, users):
    for batch in _chunks(users, BATCH):
        session.run(
            "UNWIND $b AS u "
            "MERGE (:User {user_id:u.user_id, name:u.name, "
            "surname:u.surname, country:u.country})",
            b=batch
        )


def load_stations(session, stations):
    for batch in _chunks(stations, BATCH):
        session.run(
            "UNWIND $b AS s "
            "MERGE (:Station {station_id:s.station_id, name:s.name, city:s.city})",
            b=batch
        )


def load_trips(session, trips):
    for batch in _chunks(trips, BATCH):
        session.run(
            "UNWIND $b AS t "
            "MERGE (tr:Trip {trip_id:t.trip_id, start_time:t.start_time,"
            " end_time:t.end_time, total_cost:t.total_cost}) "
            "WITH tr, t "
            "MATCH (u:User    {user_id:t.user_id}) "
            "MATCH (ss:Station {station_id:t.start_station_id}) "
            "MATCH (es:Station {station_id:t.end_station_id}) "
            "MERGE (u)-[:PERFORMED]->(tr) "
            "MERGE (tr)-[:STARTS_AT]->(ss) "
            "MERGE (tr)-[:ENDS_AT]->(es)",
            b=batch
        )


def populate(driver, dataset):
    with driver.session() as s:
        clear_and_constrain(s)
        load_users(s, dataset["users"])
        load_stations(s, dataset["stations"])
        load_trips(s, dataset["trips"])
    print(f"  Loaded {len(dataset['users'])} users, {len(dataset['stations'])} stations,"
          f" {len(dataset['trips'])} trips into Neo4j.")


if __name__ == "__main__":
    driver = get_neo4j_driver()
    t0   = time.time()
    data = generate_dataset(n_users=1000, n_trips=10000, events_per_trip=2)
    populate(driver, data)
    driver.close()
    print(f"Done in {time.time()-t0:.2f}s")
