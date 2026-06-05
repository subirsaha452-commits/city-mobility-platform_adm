"""
Part 2.1 — Neo4j Cypher query implementations.

Q1: Given a user, find all stations reachable through their trips.
Q2: Find the 3 most important stations by incoming + outgoing trips.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from app.neo4j.db import get_neo4j_driver


# ------------------------------------------------------------------
# Q1 — Stations reachable by a specific user
# Path: (u:User)-[:PERFORMED]->(t:Trip)-[:STARTS_AT|ENDS_AT]->(s:Station)
# Returns all DISTINCT stations the user has visited.
# ------------------------------------------------------------------
CYPHER_Q1 = """
MATCH (u:User {user_id: $user_id})-[:PERFORMED]->(t:Trip)
      -[:STARTS_AT|ENDS_AT]->(s:Station)
RETURN DISTINCT s.station_id AS station_id,
                s.name       AS station_name,
                s.city       AS city
ORDER BY s.name
"""

# ------------------------------------------------------------------
# Q2 — Top-3 stations by total degree (incoming + outgoing trips)
# Counts trips that START or END at each station.
# ------------------------------------------------------------------
CYPHER_Q2 = """
MATCH (s:Station)
OPTIONAL MATCH (s)<-[:ENDS_AT]-(t_in:Trip)
OPTIONAL MATCH (s)<-[:STARTS_AT]-(t_out:Trip)
WITH s,
     COUNT(DISTINCT t_in)  AS incoming,
     COUNT(DISTINCT t_out) AS outgoing
RETURN s.station_id       AS station_id,
       s.name             AS station_name,
       s.city             AS city,
       incoming,
       outgoing,
       incoming + outgoing AS total_trips
ORDER BY total_trips DESC
LIMIT 3
"""


def q1_reachable_stations(driver, user_id):
    with driver.session() as s:
        t0    = time.time()
        result = s.run(CYPHER_Q1, user_id=user_id)
        rows   = [dict(r) for r in result]
        elapsed = time.time() - t0
    return rows, elapsed


def q2_top3_stations(driver):
    with driver.session() as s:
        t0    = time.time()
        result = s.run(CYPHER_Q2)
        rows   = [dict(r) for r in result]
        elapsed = time.time() - t0
    return rows, elapsed


def run_all(user_id=1, show=5):
    driver = get_neo4j_driver()
    print("\n=== Neo4j Queries ===")

    rows, t = q1_reachable_stations(driver, user_id)
    print(f"  [Neo4j] Q1 (user {user_id} reachable stations):"
          f" {len(rows)} stations in {t:.4f}s")
    for r in rows[:show]:
        print(f"    {r}")

    rows, t = q2_top3_stations(driver)
    print(f"  [Neo4j] Q2 (top-3 important stations): {len(rows)} in {t:.4f}s")
    for r in rows:
        print(f"    {r}")

    driver.close()


if __name__ == "__main__":
    run_all(user_id=1)
