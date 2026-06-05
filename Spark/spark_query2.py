"""
Part 1.4 — Spark-based implementation of Query 2 on the MongoDB document model.

Query 2: Return all users with number of trips performed and average trip duration.

Approach:
  1. Pull trips and users from MongoDB into Spark DataFrames.
  2. Compute per-user trip count and average duration with Spark aggregations.
  3. Join the result with the users DataFrame.

Comparison with in-database MongoDB:
  - MongoDB pipeline runs entirely inside the server; minimal data transfer.
  - Spark pulls all data across the wire, then processes in parallel across
    local executor threads (local[*] mode).
  - For small datasets (<50k trips) MongoDB is faster due to lower I/O overhead.
  - For very large datasets Spark scales horizontally (add more executors);
    MongoDB's aggregation pipeline runs single-node.
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
from pyspark.sql.functions import col, count, avg, to_timestamp
from app.mongo.db import get_mongo_db


def get_spark():
    return (
        SparkSession.builder
        .appName("ADM_SparkQuery2_Mongo")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.ui.enabled", "false")
        .config("spark.hadoop.hadoop.security.authentication", "simple")
        .config("spark.hadoop.hadoop.security.authorization",  "false")
        .getOrCreate()
    )


def load_from_mongo(spark, db):
    trip_docs = list(db.trips.find(
        {}, {"_id": 0, "trip_id": 1, "user_id": 1, "start_time": 1, "end_time": 1}
    ))
    user_docs = list(db.users.find(
        {}, {"_id": 0, "user_id": 1, "name": 1, "surname": 1}
    ))
    trips_df = spark.createDataFrame(trip_docs)
    users_df = spark.createDataFrame(user_docs)
    return trips_df, users_df


def spark_query2(trips_df, users_df):
    """Compute trip count and average duration per user using Spark."""
    trips_df = (
        trips_df
        .withColumn("start_ts", to_timestamp("start_time", "yyyy-MM-dd HH:mm:ss"))
        .withColumn("end_ts",   to_timestamp("end_time",   "yyyy-MM-dd HH:mm:ss"))
        .withColumn("duration_min",
                    (col("end_ts").cast("long") - col("start_ts").cast("long")) / 60.0)
    )
    stats = (
        trips_df.groupBy("user_id")
        .agg(
            count("trip_id").alias("total_trips"),
            avg("duration_min").alias("avg_duration_minutes")
        )
    )
    result = (
        users_df.join(stats, on="user_id", how="left")
        .select("user_id", "name", "surname", "total_trips", "avg_duration_minutes")
        .orderBy(col("total_trips").desc())
    )
    return result


if __name__ == "__main__":
    spark = get_spark()
    db    = get_mongo_db()

    print("Loading data from MongoDB into Spark...")
    trips_df, users_df = load_from_mongo(spark, db)
    print(f"  Trips: {trips_df.count()}, Users: {users_df.count()}")

    t0     = time.time()
    result = spark_query2(trips_df, users_df)
    result.show(20, truncate=False)
    print(f"Spark Query 2 completed in {time.time()-t0:.4f}s")

    spark.stop()
