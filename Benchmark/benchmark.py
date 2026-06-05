"""
Scalability benchmark — runs all queries across all dataset configurations.

Configurations (as specified in the project):
  Users:           1 000 | 10 000 | 50 000
  Trips:          10 000 | 50 000 | 100 000
  Events per trip:     0 |      2 |       5 | 10

Results are written to benchmark_results.csv for use in the project report.

Usage:
  python benchmark.py          # full benchmark (36 configs)
  python benchmark.py --quick  # 3-config smoke test
"""
import csv
import time
import itertools
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.postgres.db import get_postgres_conn
from app.mongo.db    import get_mongo_db
from app.utils.data_generator import generate_dataset

from PostgreSQL.setup_postgres  import create_schema, populate as pg_populate
from MongoDB.setup_mongo        import setup_indexes, populate as mongo_populate
from PostgreSQL.queries_postgres import QUERIES as PG_QUERIES, run_query as pg_run
from MongoDB.queries_mongo       import QUERIES as MONGO_QUERIES, run_query as mongo_run

USERS_LIST  = [1_000, 10_000, 50_000]
TRIPS_LIST  = [10_000, 50_000, 100_000]
EVENTS_LIST = [0, 2, 5, 10]
CSV_FILE    = "Benchmark/benchmark_results.csv"


def bench_postgres(data):
    conn = get_postgres_conn()
    create_schema(conn)
    pg_populate(conn, data)
    times = {}
    for name, sql in PG_QUERIES.items():
        _, t = pg_run(conn, name, sql, show=0)
        times[f"pg_{name}"] = round(t, 4)
    conn.close()
    return times


def bench_mongo(data):
    db = get_mongo_db()
    setup_indexes(db)
    mongo_populate(db, data)
    times = {}
    for name, fn in MONGO_QUERIES.items():
        _, t = mongo_run(db, name, fn, show=0)
        times[f"mongo_{name}"] = round(t, 4)
    return times


def run_config(n_users, n_trips, events_per_trip):
    label = f"u={n_users//1000}k  t={n_trips//1000}k  e={events_per_trip}"
    print(f"\n{'-'*55}")
    print(f"Config: {label}")

    t0   = time.time()
    data = generate_dataset(n_users, n_trips, events_per_trip)
    print(f"  Generated in {time.time()-t0:.1f}s "
          f"({len(data['events'])} events total)")

    row = {"n_users": n_users, "n_trips": n_trips, "events_per_trip": events_per_trip}

    print("  [PostgreSQL]")
    row.update(bench_postgres(data))

    print("  [MongoDB]")
    row.update(bench_mongo(data))

    for k, v in sorted(row.items()):
        if isinstance(v, float):
            print(f"    {k}: {v}s")
    return row


def run_full(configs):
    rows = [run_config(*cfg) for cfg in configs]
    if rows:
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nResults saved to {CSV_FILE}")
    return rows


if __name__ == "__main__":
    if "--quick" in sys.argv:
        configs = [(1_000, 10_000, 2), (10_000, 50_000, 5), (50_000, 100_000, 10)]
        print("Quick benchmark (3 configs)...")
    else:
        configs = list(itertools.product(USERS_LIST, TRIPS_LIST, EVENTS_LIST))
        print(f"Full benchmark ({len(configs)} configs)...")
    run_full(configs)
