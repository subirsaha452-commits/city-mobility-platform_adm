"""
Generates HOW_TO_ACCESS.pdf — teacher access guide for the project.
Run: python Reports/generate_how_to_access.py
Output: HOW_TO_ACCESS.pdf
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable, Preformatted)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "HOW_TO_ACCESS.pdf")

W, H = A4
doc = SimpleDocTemplate(
    OUT,
    pagesize=A4,
    leftMargin=2.5*cm, rightMargin=2.5*cm,
    topMargin=2.5*cm,  bottomMargin=2.5*cm
)

styles = getSampleStyleSheet()

def sty(name, **kw):
    base = styles[name]
    return ParagraphStyle(name + "_c", parent=base, **kw)

h1  = sty("Heading1", fontSize=13, spaceAfter=5, spaceBefore=14, textColor=colors.HexColor("#1a1a2e"))
h2  = sty("Heading2", fontSize=10, spaceAfter=4, spaceBefore=9,  textColor=colors.HexColor("#1a1a2e"))
bod = sty("Normal",   fontSize=9,  spaceAfter=4, leading=14)
bld = sty("Normal",   fontSize=9,  fontName="Helvetica-Bold", spaceAfter=2)
sml = sty("Normal",   fontSize=8,  textColor=colors.HexColor("#555555"))
cen = sty("Normal",   fontSize=8,  textColor=colors.HexColor("#888888"), alignment=TA_CENTER)

DARK   = colors.HexColor("#1a1a2e")
BLUE   = colors.HexColor("#2c3e6b")
GREY   = colors.HexColor("#cccccc")
STRIPE = colors.HexColor("#f2f4f8")

def sp(n=6):
    return Spacer(1, n)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=GREY, spaceAfter=6, spaceBefore=4)

def make_table(data, col_widths, header=True):
    from reportlab.platypus import Paragraph as P
    def wrap(cell):
        if isinstance(cell, str):
            return P(cell, sty("Normal", fontSize=8, leading=11))
        return cell
    wrapped = [[wrap(c) for c in row] for row in data]
    t = Table(wrapped, colWidths=col_widths)
    ts = [
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("GRID",          (0, 0), (-1, -1), 0.4, GREY),
    ]
    if header:
        ts += [
            ("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
        for i in range(1, len(data)):
            bg = STRIPE if i % 2 == 0 else colors.white
            ts.append(("BACKGROUND", (0, i), (-1, i), bg))
    t.setStyle(TableStyle(ts))
    return t

story = []

# ── TITLE BLOCK ───────────────────────────────────────────────────────────────
title_tbl = Table(
    [[Paragraph("City Mobility Platform  —  Teacher Access Guide",
                sty("Normal", fontSize=15, fontName="Helvetica-Bold",
                    textColor=colors.white, leading=20))]],
    colWidths=[16*cm]
)
title_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0, 0), (-1, -1), DARK),
    ("LEFTPADDING",   (0, 0), (-1, -1), 14),
    ("TOPPADDING",    (0, 0), (-1, -1), 14),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
]))
story.append(title_tbl)
story.append(sp(10))

info = [
    ["Student",      "Subir Saha"],
    ["MID",          "946898"],
    ["Course",       "Advanced Data Management and Decision Support Systems"],
    ["University",   "University of Milano-Bicocca   |   A.Y. 2025/2026"],
    ["Instructors",  "Andrea Campagner   |   Gloria Lopiano"],
]
story.append(make_table(info, [3.2*cm, 12.8*cm], header=False))
story.append(sp(10))
story.append(hr())

# ── 1. HOW TO ACCESS ──────────────────────────────────────────────────────────
story.append(Paragraph("1.  How to Access This Submission", h1))
story.append(Paragraph(
    "There are two ways to access the project. Both contain identical files.", bod))

story.append(Paragraph("Option 1 — GitHub Repository (Recommended)", h2))
story.append(Paragraph(
    "Link:  https://github.com/subirsaha452-commits/city-mobility-platform_adm",
    sty("Normal", fontSize=9, fontName="Courier",
        textColor=colors.HexColor("#1a4a8a"), spaceAfter=6)))
steps1 = [
    ["1.", "Open the link in any browser."],
    ["2.", "All source code is visible and readable directly in the browser — no download needed."],
    ["3.", "Click any .py file to read the code with syntax highlighting."],
    ["4.", "Click any folder name to browse its contents."],
]
story.append(make_table(steps1, [0.6*cm, 15.4*cm], header=False))
story.append(sp(8))

story.append(Paragraph("Option 2 — ZIP File", h2))
story.append(Paragraph(
    "The ZIP file ADM_Subir_Saha_946898.zip is included alongside this guide.", bod))
steps2 = [
    ["1.", "Right-click the ZIP and select Extract All (Windows) or double-click (Mac)."],
    ["2.", "Open the extracted folder ADM_New_Project/."],
    ["3.", "Open HOW_TO_ACCESS.pdf (this file) to navigate the project."],
]
story.append(make_table(steps2, [0.6*cm, 15.4*cm], header=False))
story.append(sp(8))
story.append(hr())

# ── 2. FOLDER STRUCTURE ───────────────────────────────────────────────────────
story.append(Paragraph("2.  Project Folder Structure", h1))

structure = (
    "ADM_New_Project/\n"
    "  main.py                          Single entry point for all commands\n"
    "  requirements.txt                 Python dependencies\n"
    "  HOW_TO_ACCESS.pdf                This file\n"
    "  README.md                        Technical overview\n"
    "\n"
    "  PostgreSQL/                      Relational model\n"
    "    setup_postgres.py              Creates 4 tables + indexes, loads data\n"
    "    queries_postgres.py            Q1 Q2 Q3 Q4 in SQL\n"
    "\n"
    "  MongoDB/                         Document model\n"
    "    setup_mongo.py                 Creates collections + indexes, loads data\n"
    "    queries_mongo.py               Q1 Q2 Q3 Q4 in aggregation pipeline\n"
    "\n"
    "  Neo4j/                           Graph model\n"
    "    setup_neo4j.py                 Creates User / Station / Trip nodes + edges\n"
    "    queries_neo4j.py               Cypher: reachable stations + top-3 stations\n"
    "\n"
    "  Spark/                           Spark analytics\n"
    "    spark_query2.py                Spark implementation of Query 2\n"
    "    spark_graphframes.py           PageRank + Connected Components\n"
    "\n"
    "  Schema_Evolution/                Schema evolution\n"
    "    schema_evolution.py            Adds battery_level to BATTERY events\n"
    "\n"
    "  Benchmark/                       Scalability benchmark\n"
    "    benchmark.py                   Runs all queries across dataset sizes\n"
    "    benchmark_results.csv          Actual measured timings\n"
    "\n"
    "  Reports/                         Deliverable documents\n"
    "    ADM_Project_Report_Subir_Saha_Final.pdf    Main project report (51 pages)\n"
    "    ADM_Project_Report_Subir_Saha_Final.docx   Word source of the report\n"
    "    generate_report_v2.py          Report generator script\n"
    "\n"
    "  app/                             Database connection helpers\n"
    "    postgres/db.py                 PostgreSQL connection (pg8000)\n"
    "    mongo/db.py                    MongoDB connection (PyMongo)\n"
    "    neo4j/db.py                    Neo4j connection (bolt://)\n"
    "    utils/data_generator.py        Synthetic data generator\n"
)
story.append(Preformatted(
    structure,
    sty("Code", fontSize=7.8, fontName="Courier", leading=11, leftIndent=5, spaceAfter=4)
))
story.append(hr())

# ── 3. ASSIGNMENT COVERAGE ────────────────────────────────────────────────────
story.append(Paragraph("3.  Assignment Requirements Coverage", h1))
req = [
    ["Assignment Requirement",           "File(s)",                                           "Status"],
    ["Relational schema (PostgreSQL)",   "PostgreSQL/setup_postgres.py",                      "Complete"],
    ["Document schema (MongoDB)",        "MongoDB/setup_mongo.py",                            "Complete"],
    ["Q1-Q4 in relational model",        "PostgreSQL/queries_postgres.py",                    "Complete"],
    ["Q1-Q4 in document model",          "MongoDB/queries_mongo.py",                          "Complete"],
    ["Graph model (Neo4j)",              "Neo4j/setup_neo4j.py",                              "Complete"],
    ["Graph queries (Cypher)",           "Neo4j/queries_neo4j.py",                            "Complete"],
    ["Schema evolution",                 "Schema_Evolution/schema_evolution.py",              "Complete"],
    ["Spark Query 2",                    "Spark/spark_query2.py",                             "Complete"],
    ["GraphFrames PageRank",             "Spark/spark_graphframes.py",                        "Complete"],
    ["GraphFrames Connected Components", "Spark/spark_graphframes.py",                        "Complete"],
    ["Scalability benchmark",            "Benchmark/benchmark.py",                            "Complete"],
    ["Performance discussion",           "Reports/ADM_Project_Report_Subir_Saha_Final.pdf",   "Complete"],
]
story.append(make_table(req, [5.5*cm, 7.5*cm, 3*cm]))
story.append(hr())

# ── 4. READING THE REPORT ─────────────────────────────────────────────────────
story.append(Paragraph("4.  Reading the Report (No Installation Needed)", h1))
story.append(Paragraph(
    "Open Reports/ADM_Project_Report_Subir_Saha_Final.pdf in any PDF viewer. "
    "The report is 51 pages and covers:", bod))
topics = [
    ["", "Data model design and justification (relational vs. document vs. graph)"],
    ["", "All four queries with SQL and aggregation pipeline implementation and results"],
    ["", "Benchmark results with charts showing actual measured timings"],
    ["", "Schema evolution analysis for both PostgreSQL and MongoDB"],
    ["", "Spark and GraphFrames results (PageRank scores, Connected Components)"],
    ["", "Partitioning and replication discussion"],
    ["", "Conclusion and comparative analysis of all three database systems"],
]
story.append(make_table(topics, [0.4*cm, 15.6*cm], header=False))
story.append(hr())

# ── 5. RUNNING THE PROJECT ────────────────────────────────────────────────────
story.append(Paragraph("5.  Running the Project (Optional)", h1))
story.append(Paragraph("Requirements:", bld))
req2 = [
    ["Requirement",    "Version", "Notes"],
    ["Python",         "3.11",    ""],
    ["PostgreSQL",     "15+",     "Default port 5432"],
    ["MongoDB",        "6+",      "Default port 27017"],
    ["Neo4j Desktop",  "5+",      "Default bolt port 7687   password: 123456789"],
    ["Java",           "11",      "Required for Spark and GraphFrames only"],
]
story.append(make_table(req2, [3.8*cm, 2.5*cm, 9.7*cm]))
story.append(sp(6))
story.append(Paragraph("Commands:", bld))
cmds = [
    ["Command",                           "What it does"],
    ["python main.py setup",              "Create all schemas and load default dataset"],
    ["python main.py queries",            "Run all queries: PostgreSQL + MongoDB + Neo4j"],
    ["python main.py spark",              "Run Spark Query 2 on MongoDB data"],
    ["python main.py graphframes",        "Run GraphFrames PageRank and Connected Components"],
    ["python main.py evolve",             "Run schema evolution (add battery_level)"],
    ["python main.py benchmark --quick",  "Run quick 3-configuration scalability benchmark"],
]
story.append(make_table(cmds, [6*cm, 10*cm]))
story.append(hr())

# ── 6. KEY RESULTS ────────────────────────────────────────────────────────────
story.append(Paragraph("6.  Key Results at a Glance", h1))

story.append(Paragraph("Benchmark — Wall-clock seconds", h2))
bench = [
    ["Configuration",                     "PG Q1","PG Q2","PG Q3","PG Q4","Mongo Q1","Mongo Q2","Mongo Q3","Mongo Q4"],
    ["Small  (1k users / 10k trips / 2 ev)","0.24","0.02","2.01","0.13","4.29","0.38","0.03","0.03"],
    ["Medium (10k / 50k / 5 ev)",          "3.36","0.24","91.5","2.59","20.94","2.52","0.06","0.26"],
    ["Large  (50k / 100k / 10 ev)",        "6.87","1.19","373s","1.43","37.94","7.79","0.09","0.61"],
]
story.append(make_table(bench, [4.5*cm,1.4*cm,1.4*cm,1.4*cm,1.4*cm,1.7*cm,1.7*cm,1.7*cm,1.7*cm]))
story.append(Paragraph(
    "PostgreSQL wins Q1 and Q2 (JOIN-heavy). "
    "MongoDB wins Q3 and Q4 — up to 4,100x faster on Q3 at large scale.", sml))
story.append(sp(8))

story.append(Paragraph("GraphFrames PageRank — Top 3 Stations", h2))
pr = [
    ["Rank", "Station",      "City",   "PageRank Score"],
    ["1",    "Padua Porto",  "Padua",  "1.149316"],
    ["2",    "Milan Stadio", "Milan",  "1.122747"],
    ["3",    "Verona Sud",   "Verona", "1.089738"],
]
story.append(make_table(pr, [2*cm, 4.5*cm, 4*cm, 5.5*cm]))
story.append(sp(6))

story.append(Paragraph("Connected Components", h2))
story.append(Paragraph(
    "All 50 stations form 1 connected component — "
    "every station is reachable from every other station.", bod))

story.append(Paragraph("Schema Evolution", h2))
evo = [
    ["Database",    "Operation",                                        "Result"],
    ["PostgreSQL",  "ALTER TABLE events ADD COLUMN battery_level INT",  "250,010 rows back-filled"],
    ["MongoDB",     "update_many with arrayFilters",                    "94,432 documents updated"],
]
story.append(make_table(evo, [3*cm, 7.5*cm, 5.5*cm]))
story.append(sp(20))
story.append(hr())

story.append(Paragraph(
    "Subir Saha   |   MID: 946898   |   University of Milano-Bicocca   |   A.Y. 2025/2026",
    cen))

doc.build(story)
print(f"Created: {OUT}")
