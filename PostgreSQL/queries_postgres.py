"""
Part 1 — PostgreSQL implementations of all 4 required queries.
Each function returns (rows, elapsed_seconds).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from app.postgres.db import get_postgres_conn

# ------------------------------------------------------------------
# Q1: All trips with user info and start/end station names
# ------------------------------------------------------------------
Q1 = """
SELECT
    t.trip_id,
    u.name,
    u.surname,
    u.country,
    s1.name  AS start_station,
    s2.name  AS end_station,
    t.start_time,
    t.end_time,
    t.total_cost
FROM trips t
JOIN users    u  ON t.user_id          = u.user_id
JOIN stations s1 ON t.start_station_id = s1.station_id
JOIN stations s2 ON t.end_station_id   = s2.station_id;
"""

# ------------------------------------------------------------------
# Q2: All users with number of trips and average trip duration
# ------------------------------------------------------------------
Q2 = """
SELECT
    u.user_id,
    u.name,
    u.surname,
    COUNT(t.trip_id)  AS total_trips,
    AVG(EXTRACT(EPOCH FROM (t.end_time - t.start_time)) / 60.0)
                      AS avg_duration_minutes
FROM users u
LEFT JOIN trips t ON u.user_id = t.user_id
GROUP BY u.user_id, u.name, u.surname
ORDER BY total_trips DESC;
"""

# ------------------------------------------------------------------
# Q3: All stations with trips starting / ending there
# ------------------------------------------------------------------
Q3 = """
SELECT
    s.station_id,
    s.name,
    s.city,
    COUNT(DISTINCT t1.trip_id) AS trips_starting,
    COUNT(DISTINCT t2.trip_id) AS trips_ending
FROM stations s
LEFT JOIN trips t1 ON s.station_id = t1.start_station_id
LEFT JOIN trips t2 ON s.station_id = t2.end_station_id
GROUP BY s.station_id, s.name, s.city
ORDER BY (COUNT(DISTINCT t1.trip_id) + COUNT(DISTINCT t2.trip_id)) DESC;
"""

# ------------------------------------------------------------------
# Q4: Trips that contain at least one ERROR event
# ------------------------------------------------------------------
Q4 = """
SELECT DISTINCT
    t.trip_id,
    u.name,
    u.surname,
    t.start_time,
    t.end_time,
    t.total_cost
FROM trips t
JOIN users u ON t.user_id = u.user_id
WHERE EXISTS (
    SELECT 1 FROM events e
    WHERE e.trip_id = t.trip_id AND e.type = 'ERROR'
);
"""

QUERIES = {"Q1": Q1, "Q2": Q2, "Q3": Q3, "Q4": Q4}


def run_query(conn, name, sql, show=3):
    cur = conn.cursor()
    t0  = time.time()
    cur.execute(sql)
    rows = cur.fetchall()
    elapsed = time.time() - t0
    cur.close()
    print(f"  [PG] {name}: {len(rows)} rows in {elapsed:.4f}s")
    if show and rows:
        print(f"       sample -> {rows[:show]}")
    return rows, elapsed


def run_all(show=2):
    conn = get_postgres_conn()
    print("\n=== PostgreSQL Queries ===")
    results = {}
    for name, sql in QUERIES.items():
        rows, t = run_query(conn, name, sql, show)
        results[name] = {"rows": len(rows), "time": t}
    conn.close()
    return results


if __name__ == "__main__":
    run_all()
