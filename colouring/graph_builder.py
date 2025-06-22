from collections import defaultdict
from db import run_query

def build_conflict_graph():
    # Ambil semua course dan tetangganya (conflict graph)
    nodes = run_query("MATCH (c:Course) RETURN c.id AS id, c.name AS name")
    edges = run_query("""
        MATCH (c1:Course)<-[:ENROLLED_IN]-(s:Student)-[:ENROLLED_IN]->(c2:Course)
        WHERE c1.id <> c2.id
        RETURN DISTINCT c1.id AS source, c2.id AS target
    """)
    graph = defaultdict(set)
    for edge in edges:
        graph[edge['source']].add(edge['target'])
        graph[edge['target']].add(edge['source'])
    return {n['id']: graph[n['id']] for n in nodes}, {n['id']: n['name'] for n in nodes} 