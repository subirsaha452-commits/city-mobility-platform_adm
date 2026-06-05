"""
Part 1 — MongoDB aggregation pipeline implementations of all 4 queries.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from app.mongo.db import get_mongo_db


# ------------------------------------------------------------------
# Q1: All trips with user info and start/end station names
# Uses two $lookup stages to join users and stations collections.
# In the embedded model events are ignored for this query.
# ------------------------------------------------------------------
def q1_trips_with_info(db):
    pipeline = [
        {"$lookup": {"from": "users",    "localField": "user_id",
                     "foreignField": "user_id", "as": "user"}},
        {"$unwind": "$user"},
        {"$lookup": {"from": "stations", "localField": "start_station_id",
                     "foreignField": "station_id", "as": "start_st"}},
        {"$unwind": "$start_st"},
        {"$lookup": {"from": "stations", "localField": "end_station_id",
                     "foreignField": "station_id", "as": "end_st"}},
        {"$unwind": "$end_st"},
        {"$project": {
            "_id": 0,
            "trip_id":      1,
            "user_name":    "$user.name",
            "user_surname": "$user.surname",
            "user_country": "$user.country",
            "start_station": "$start_st.name",
            "end_station":   "$end_st.name",
            "start_time":   1,
            "end_time":     1,
            "total_cost":   1
        }}
    ]
    return list(db.trips.aggregate(pipeline))


# ------------------------------------------------------------------
# Q2: All users with number of trips and average trip duration
# Groups trips by user_id, computes stats, then joins with users.
# ------------------------------------------------------------------
def q2_user_stats(db):
    pipeline = [
        {"$group": {
            "_id": "$user_id",
            "total_trips": {"$sum": 1},
            "avg_dur_sec": {"$avg": {
                "$dateDiff": {
                    "startDate": {"$dateFromString": {"dateString": "$start_time"}},
                    "endDate":   {"$dateFromString": {"dateString": "$end_time"}},
                    "unit": "second"
                }
            }}
        }},
        {"$lookup": {"from": "users", "localField": "_id",
                     "foreignField": "user_id", "as": "user"}},
        {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "user_id":              "$_id",
            "name":                 "$user.name",
            "surname":              "$user.surname",
            "total_trips":          1,
            "avg_duration_minutes": {"$divide": ["$avg_dur_sec", 60]}
        }},
        {"$sort": {"total_trips": -1}}
    ]
    return list(db.trips.aggregate(pipeline))


# ------------------------------------------------------------------
# Q3: All stations with number of trips starting / ending there
# Two aggregations merged in Python (MongoDB has no FULL OUTER JOIN).
# ------------------------------------------------------------------
def q3_station_counts(db):
    starts = {r["_id"]: r["n"]
              for r in db.trips.aggregate([
                  {"$group": {"_id": "$start_station_id", "n": {"$sum": 1}}}
              ])}
    ends   = {r["_id"]: r["n"]
              for r in db.trips.aggregate([
                  {"$group": {"_id": "$end_station_id", "n": {"$sum": 1}}}
              ])}

    st_map = {s["station_id"]: s
              for s in db.stations.find({}, {"_id": 0})}

    rows = []
    for sid in set(starts) | set(ends):
        info = st_map.get(sid, {})
        rows.append({
            "station_id":    sid,
            "name":          info.get("name", "unknown"),
            "city":          info.get("city", "unknown"),
            "trips_starting": starts.get(sid, 0),
            "trips_ending":   ends.get(sid, 0)
        })
    return sorted(rows, key=lambda r: r["trips_starting"] + r["trips_ending"], reverse=True)


# ------------------------------------------------------------------
# Q4: Trips with at least one ERROR event
# Because events are embedded, this is a direct field filter — no JOIN.
# This is the main performance advantage of the embedded design.
# ------------------------------------------------------------------
def q4_trips_with_error(db):
    return list(db.trips.find(
        {"events.type": "ERROR"},
        {"_id": 0, "trip_id": 1, "user_id": 1,
         "start_time": 1, "end_time": 1, "total_cost": 1}
    ))


QUERIES = {
    "Q1": q1_trips_with_info,
    "Q2": q2_user_stats,
    "Q3": q3_station_counts,
    "Q4": q4_trips_with_error,
}


def run_query(db, name, fn, show=2):
    t0    = time.time()
    rows  = fn(db)
    elapsed = time.time() - t0
    print(f"  [Mongo] {name}: {len(rows)} results in {elapsed:.4f}s")
    if show and rows:
        print(f"          sample -> {rows[:show]}")
    return rows, elapsed


def run_all(show=2):
    db = get_mongo_db()
    print("\n=== MongoDB Queries ===")
    results = {}
    for name, fn in QUERIES.items():
        rows, t = run_query(db, name, fn, show)
        results[name] = {"rows": len(rows), "time": t}
    return results


if __name__ == "__main__":
    run_all()
