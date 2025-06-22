from neo4j import GraphDatabase
import os

# Konfigurasi Neo4j
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_query(query, parameters=None):
    with driver.session() as session:
        result = session.run(query, parameters)
        return [dict(record) for record in result] 