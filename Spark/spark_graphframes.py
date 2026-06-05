"""
Part 2.2 — Spark + GraphFrames implementations.

Q1: Top-3 most important stations by PageRank.
Q2: Connected components of the stations sub-graph.

Station sub-graph construction:
  Vertices = all Station documents  (id = station_id)
  Edges    = one directed edge per trip:  start_station_id --> end_station_id

This projection represents mobility flow between stations.
PageRank identifies stations that receive high traffic from other busy stations.
Connected components show which stations are mutually reachable by any trip path.

How to run:
  spark-submit --packages graphframes:graphframes:0.8.2-spark3.2-s_2.12 spark_graphframes.py
  OR set PYSPARK_SUBMIT_ARGS  .
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
import time

# Force PySpark to use Java 11 (Java 17.0.9+ breaks Spark's Hadoop security layer)
os.environ["JAVA_HOME"] = r"C:\Program Files\Eclipse Adoptium\jdk-11.0.31.11-hotspot"
os.environ["PATH"]      = os.environ["JAVA_HOME"] + r"\bin;" + os.environ["PATH"]

os.environ["PYSPARK_PYTHON"]        = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] = os.environ["HADOOP_HOME"] + r"\bin;" + os.environ["PATH"]

_GF_JAR     = r"C:\spark_jars\graphframes.jar"
_GF_JAR_URI = "file:///C:/spark_jars/graphframes.jar"
os.environ["PYSPARK_SUBMIT_ARGS"] = f"--jars {_GF_JAR_URI} pyspark-shell"

# Must be set BEFORE pyspark is imported so the JVM picks it up (Java 17)
os.environ["JAVA_TOOL_OPTIONS"] = " ".join([
    "--add-opens=java.base/java.lang=ALL-UNNAMED",
    "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED",
    "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",
    "--add-opens=java.base/java.io=ALL-UNNAMED",
    "--add-opens=java.base/java.net=ALL-UNNAMED",
    "--add-opens=java.base/java.nio=ALL-UNNAMED",
    "--add-opens=java.base/java.util=ALL-UNNAMED",
    "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED",
    "--add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED",
    "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED",
    "--add-opens=java.base/sun.nio.cs=ALL-UNNAMED",
    "--add-opens=java.base/sun.security.action=ALL-UNNAMED",
    "--add-opens=java.base/sun.util.calendar=ALL-UNNAMED",
    "--add-opens=java.security.jgss/sun.security.krb5=ALL-UNNAMED",
])

_JAVA17_OPTS = os.environ["JAVA_TOOL_OPTIONS"]

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from app.mongo.db import get_mongo_db


def get_spark():
    return (
        SparkSession.builder
        .appName("ADM_GraphFrames")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.ui.enabled", "false")
        .config("spark.hadoop.hadoop.security.authentication", "simple")
        .config("spark.hadoop.hadoop.security.authorization",  "false")
        .config("spark.jars", "file:///C:/spark_jars/graphframes.jar")
        .getOrCreate()
    )


def build_graph(spark, db):
    """Build a GraphFrame of the stations sub-graph from MongoDB data."""
    from graphframes import GraphFrame  # imported after Spark+JAR are loaded

    stations = list(db.stations.find({}, {"_id": 0, "station_id": 1, "name": 1, "city": 1}))
    trips    = list(db.trips.find({}, {"_id": 0, "start_station_id": 1, "end_station_id": 1}))

    vertices = (
        spark.createDataFrame(stations)
        .withColumnRenamed("station_id", "id")
    )
    edges = spark.createDataFrame([
        {"src": t["start_station_id"], "dst": t["end_station_id"]} for t in trips
    ])
    return GraphFrame(vertices, edges)


def q1_pagerank(g, reset_prob=0.15, max_iter=10):
    """Top-3 stations by PageRank score."""
    t0 = time.time()
    pr = g.pageRank(resetProbability=reset_prob, maxIter=max_iter)
    top3 = (
        pr.vertices
        .select("id", "name", "city", "pagerank")
        .orderBy(col("pagerank").desc())
        .limit(3)
    )
    rows = top3.collect()
    elapsed = time.time() - t0
    return rows, elapsed


def q2_connected_components(g):
    """Connected components of the stations sub-graph.

    GraphFrames connectedComponents() requires Hadoop winutils on Windows
    (for checkpoint directory chmod), which often fails.  We replicate the
    same result with a union-find over the collected edge list — identical
    semantics, no Hadoop shell dependency.
    """
    t0 = time.time()

    edges    = [(r["src"], r["dst"]) for r in g.edges.collect()]
    vertices = {r["id"]: r for r in g.vertices.collect()}

    # Union-Find
    parent = {v: v for v in vertices}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for src, dst in edges:
        if src in parent and dst in parent:
            union(src, dst)

    node_component = {v: find(v) for v in vertices}
    unique_roots   = sorted(set(node_component.values()))
    root_label     = {r: i for i, r in enumerate(unique_roots)}
    n_components   = len(unique_roots)

    rows = sorted(
        [
            {"id": v, "name": vertices[v]["name"], "city": vertices[v]["city"],
             "component": root_label[find(v)]}
            for v in vertices
        ],
        key=lambda r: (r["component"], r["id"])
    )
    elapsed = time.time() - t0
    return rows, n_components, elapsed


def run_all():
    spark = get_spark()
    db    = get_mongo_db()

    print("Building station graph from MongoDB...")
    g = build_graph(spark, db)
    print(f"  Vertices: {g.vertices.count()}, Edges: {g.edges.count()}")

    print("\n--- Q1: PageRank (top-3 stations) ---")
    rows, t = q1_pagerank(g)
    print(f"  Completed in {t:.4f}s")
    for r in rows:
        print(f"  Station {r['id']} | {r['name']} ({r['city']}) | PageRank = {r['pagerank']:.6f}")

    print("\n--- Q2: Connected Components ---")
    rows, n_cc, t = q2_connected_components(g)
    print(f"  {len(rows)} stations in {n_cc} component(s), computed in {t:.4f}s")
    for r in rows[:10]:
        print(f"  Station {r['id']} ({r['name']}) -> component {r['component']}")

    spark.stop()


if __name__ == "__main__":
    run_all()
