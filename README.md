# City Mobility Platform — Advanced Data Management Project
**University of Milano-Bicocca · a.y. 2025/2026**  
**Student:** Subir Saha · **MID:** 946898  
**Instructors:** Andrea Campagner · Gloria Lopiano

A bike-sharing mobility system implemented across three database paradigms with Spark-based analytics.

---

## Project Structure

```
ADM_New_Project/
├── HOW_TO_ACCESS.pdf            # Teacher access guide (start here)
├── main.py                      # Single entry point for all commands
├── requirements.txt             # Python dependencies
├── README.md                    # This file
│
├── PostgreSQL/                  # Relational model
│   ├── setup_postgres.py        # Creates 4 tables + indexes, loads data
│   └── queries_postgres.py      # Q1 Q2 Q3 Q4 in SQL
│
├── MongoDB/                     # Document model
│   ├── setup_mongo.py           # Creates collections + indexes, loads data
│   └── queries_mongo.py         # Q1 Q2 Q3 Q4 in aggregation pipeline
│
├── Neo4j/                       # Graph model
│   ├── setup_neo4j.py           # Creates User / Station / Trip nodes + edges
│   └── queries_neo4j.py         # Cypher: reachable stations + top-3 stations
│
├── Spark/                       # Spark analytics
│   ├── spark_query2.py          # Spark implementation of Query 2
│   └── spark_graphframes.py     # PageRank + Connected Components
│
├── Schema_Evolution/            # Schema evolution
│   └── schema_evolution.py      # Adds battery_level to BATTERY events
│
├── Benchmark/                   # Scalability benchmark
│   ├── benchmark.py             # Runs all queries across dataset sizes
│   └── benchmark_results.csv    # Actual measured timings
│
├── Reports/                     # Deliverable documents
│   ├── ADM_Project_Report_Subir_Saha_Final.pdf    # Main report (51 pages)
│   ├── ADM_Project_Report_Subir_Saha_Final.docx   # Word source
│   └── generate_report_v2.py    # Report generator script
│
└── app/                         # Database connection helpers
    ├── postgres/db.py           # PostgreSQL connection (pg8000)
    ├── mongo/db.py              # MongoDB connection (PyMongo)
    ├── neo4j/db.py              # Neo4j connection (bolt://)
    └── utils/data_generator.py  # Synthetic data generator
```

---

## Setup

### Requirements
- Python 3.11
- PostgreSQL 15+
- MongoDB 6+ (local, port 27017)
- Neo4j Desktop 5+ (port 7687, password: `123456789`)
- Java 11 (for Spark and GraphFrames only)

### Install dependencies
```bash
pip install -r requirements.txt
```

### Database connections
Edit these files with your credentials if needed:
- `app/postgres/db.py` — PostgreSQL (default: `ADM_New_Project`, user: `postgres`)
- `app/mongo/db.py` — MongoDB (default: `adm_new_project`)
- `app/neo4j/db.py` — Neo4j (default password: `123456789`)

---

## Running the Project

```bash
# 1. Setup all databases (1k users, 10k trips, 2 events/trip)
python main.py setup

# 2. Run all queries (PostgreSQL + MongoDB + Neo4j)
python main.py queries

# 3. Spark Query 2 on MongoDB
python main.py spark

# 4. GraphFrames: PageRank + Connected Components
python main.py graphframes

# 5. Schema Evolution (add battery_level to BATTERY events)
python main.py evolve

# 6. Scalability benchmark (quick: 3 configs)
python main.py benchmark --quick
```

---

## Data Model

### Relational (PostgreSQL)
4 normalized tables: `users`, `stations`, `trips`, `events` — fully referencing model.

### Document (MongoDB)
Hybrid design: events **embedded** in trips; users and stations **referenced**.

### Graph (Neo4j)
Nodes: `(:User)`, `(:Station)`, `(:Trip)`  
Edges: `[:PERFORMED]`, `[:STARTS_AT]`, `[:ENDS_AT]`

---

## Key Results

| Query | PostgreSQL | MongoDB | Winner |
|-------|-----------|---------|--------|
| Q1 — Trips + user + station | 0.24s → 6.87s | 4.29s → 37.94s | PostgreSQL |
| Q2 — User trip stats | 0.02s → 1.19s | 0.38s → 7.79s | PostgreSQL |
| Q3 — Station counts | 2.0s → **373s** | 0.03s → **0.09s** | **MongoDB** |
| Q4 — ERROR events | 0.13s → 1.43s | 0.03s → 0.61s | **MongoDB** |

**GraphFrames PageRank Top-3:**
1. Milan Parco — 1.13
2. Palermo doumo — 1.12
3. Florence ovest — 1.10

**Connected Components:** 50 stations → 1 component (fully connected network)
