"""
ADM Project — Main entry point.

Project folder structure:
  PostgreSQL/        → setup_postgres.py, queries_postgres.py
  MongoDB/           → setup_mongo.py, queries_mongo.py
  Neo4j/             → setup_neo4j.py, queries_neo4j.py
  Spark/             → spark_query2.py, spark_graphframes.py, graphframes.jar
  Schema_Evolution/  → schema_evolution.py
  Benchmark/         → benchmark.py, benchmark_results.csv
  Reports/           → ADM_Project_Report_Subir_Saha_946898.pdf, generate_report_v2.py
  app/               → DB connection helpers (postgres/db.py, mongo/db.py, neo4j/db.py)

Commands:
  python main.py setup               Setup schemas + load 1k/10k/2 default dataset
  python main.py queries             Run all queries (PostgreSQL + MongoDB + Neo4j)
  python main.py spark               Spark Query 2 on MongoDB data
  python main.py graphframes         GraphFrames PageRank + Connected Components
  python main.py evolve              Schema evolution: add battery_level to BATTERY events
  python main.py benchmark           Full scalability benchmark (36 configs)
  python main.py benchmark --quick   Quick 3-config benchmark
"""
import sys


def cmd_setup():
    from app.utils.data_generator import generate_dataset
    data = generate_dataset(n_users=1000, n_trips=10000, events_per_trip=2)

    print("=== PostgreSQL ===")
    from app.postgres.db import get_postgres_conn
    from PostgreSQL.setup_postgres import create_schema, populate as pg_pop
    conn = get_postgres_conn()
    create_schema(conn)
    pg_pop(conn, data)
    conn.close()

    print("\n=== MongoDB ===")
    from app.mongo.db import get_mongo_db
    from MongoDB.setup_mongo import setup_indexes, populate as mongo_pop
    db = get_mongo_db()
    setup_indexes(db)
    mongo_pop(db, data)

    print("\n=== Neo4j ===")
    from app.neo4j.db import get_neo4j_driver
    from Neo4j.setup_neo4j import populate as neo4j_pop
    driver = get_neo4j_driver()
    neo4j_pop(driver, data)
    driver.close()

    print("\nAll databases ready.")


def cmd_queries():
    from PostgreSQL.queries_postgres import run_all as pg_all
    from MongoDB.queries_mongo       import run_all as mongo_all
    from Neo4j.queries_neo4j         import run_all as neo4j_all
    pg_all()
    mongo_all()
    neo4j_all(user_id=1)


def cmd_spark():
    from Spark import spark_query2 as sq
    spark = sq.get_spark()
    db    = sq.get_mongo_db()
    trips_df, users_df = sq.load_from_mongo(spark, db)
    result = sq.spark_query2(trips_df, users_df)
    result.show(20, truncate=False)
    spark.stop()


def cmd_graphframes():
    from Spark import spark_graphframes as gf
    gf.run_all()


def cmd_evolve():
    from Schema_Evolution import schema_evolution as se
    conn = se.get_postgres_conn()
    se.pg_add_battery_level(conn)
    se.pg_verify(conn)
    conn.close()
    db = se.get_mongo_db()
    se.mongo_add_battery_level(db)
    se.mongo_verify(db)


def cmd_benchmark():
    from Benchmark import benchmark as bm
    import itertools
    if "--quick" in sys.argv:
        configs = [(1_000, 10_000, 2), (10_000, 50_000, 5), (50_000, 100_000, 10)]
    else:
        configs = list(itertools.product(bm.USERS_LIST, bm.TRIPS_LIST, bm.EVENTS_LIST))
    bm.run_full(configs)


COMMANDS = {
    "setup":       cmd_setup,
    "queries":     cmd_queries,
    "spark":       cmd_spark,
    "graphframes": cmd_graphframes,
    "evolve":      cmd_evolve,
    "benchmark":   cmd_benchmark,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd not in COMMANDS:
        print(__doc__)
        sys.exit(1)
    COMMANDS[cmd]()
