from neo4j import GraphDatabase

def get_neo4j_driver():
    return GraphDatabase.driver(
        "bolt://127.0.0.1:7687",
        auth=("neo4j", "123456789")
    )
