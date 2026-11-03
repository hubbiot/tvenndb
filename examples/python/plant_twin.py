"""An industrial twin in TvennDB: the walkthrough of the blog post
"Six questions an industrial twin should answer" (hubbiot.com/blog).

Two sites, three lines, six robots and two spare parts in their own graph,
"plant", then the questions a twin is asked on a bad day: what stops when a
robot stops, where a part is used and whether stock covers it, which
machines are due for service, what changed and why, and what a contractor
confined to one site can see.

    TVENNDB_PASSWORD=<admin password> python3 plant_twin.py

Running it again starts the graph over.
"""
import json

from tvenndb_http import TvennDB, TvennDBError

GRAPH = "plant"

ONTOLOGY = {
    "labels": {
        "Site": {"key": "code", "properties": {
            "code": {"type": "string", "required": True}, "name": {"type": "string"}}},
        "Line": {"key": "code", "properties": {
            "code": {"type": "string", "required": True}, "name": {"type": "string"}}},
        "Robot": {"key": "serial", "properties": {
            "serial": {"type": "string", "required": True},
            "model": {"type": "string"},
            "status": {"type": "string", "values": ["running", "idle", "maintenance"]},
            "hours": {"type": "float", "min": 0, "index": True},
            "notes": {"type": "string", "fulltext": True}}},
        "Part": {"key": "number", "properties": {
            "number": {"type": "string", "required": True},
            "name": {"type": "string"},
            "stock": {"type": "int", "min": 0}}},
    },
    "relations": {
        "HAS_LINE": {"from": ["Site"], "to": ["Line"], "containment": True},
        "HAS_ROBOT": {"from": ["Line"], "to": ["Robot"], "containment": True},
        "FEEDS": {"from": ["Robot"], "to": ["Robot"]},
        "USES": {"from": ["Robot"], "to": ["Part"], "properties": {"qty": {"type": "int", "min": 1}}},
    },
}

SEED = """
INSERT (n:Site {code: 'north', name: 'Plant North'}),
       (s:Site {code: 'south', name: 'Plant South'}),
       (n)-[:HAS_LINE]->(body:Line {code: 'north-body', name: 'Body shop'}),
       (n)-[:HAS_LINE]->(paint:Line {code: 'north-paint', name: 'Paint shop'}),
       (s)-[:HAS_LINE]->(pack:Line {code: 'south-pack', name: 'Packaging'}),
       (body)-[:HAS_ROBOT]->(r1:Robot {serial: 'r1', model: 'KR-210', status: 'running', hours: 4620.0,
                                       notes: 'Gearbox vibration above limit at last inspection'}),
       (body)-[:HAS_ROBOT]->(r2:Robot {serial: 'r2', model: 'KR-210', status: 'running', hours: 4310.0,
                                       notes: 'Welding tip replaced'}),
       (paint)-[:HAS_ROBOT]->(r3:Robot {serial: 'r3', model: 'KR-120', status: 'running', hours: 2100.0,
                                        notes: 'Nozzle cleaned'}),
       (paint)-[:HAS_ROBOT]->(r4:Robot {serial: 'r4', model: 'KR-120', status: 'idle', hours: 980.0}),
       (pack)-[:HAS_ROBOT]->(r5:Robot {serial: 'r5', model: 'VG-60', status: 'running', hours: 5150.0,
                                       notes: 'Vacuum gripper loses suction, gearbox noise'}),
       (pack)-[:HAS_ROBOT]->(r6:Robot {serial: 'r6', model: 'VG-60', status: 'running', hours: 4890.0}),
       (r1)-[:FEEDS]->(r2), (r2)-[:FEEDS]->(r3), (r3)-[:FEEDS]->(r4), (r5)-[:FEEDS]->(r6),
       (g:Part {number: 'G-200', name: 'Gearbox G-200', stock: 2}),
       (c:Part {number: 'V-60', name: 'Suction cup V-60', stock: 40}),
       (r1)-[:USES {qty: 1}]->(g), (r2)-[:USES {qty: 1}]->(g), (r5)-[:USES {qty: 1}]->(g),
       (r5)-[:USES {qty: 8}]->(c), (r6)-[:USES {qty: 8}]->(c)
"""

QUESTIONS = {
    "If r1 stops, what stops with it?": """
        MATCH (r:Robot {serial: 'r1'})-[:FEEDS]->+(d:Robot)<-[:HAS_ROBOT]-(l:Line)
        RETURN l.name AS line, collect(d.serial) AS stops ORDER BY line""",
    "How does r1 reach r4?": """
        MATCH p = shortestPath((a:Robot {serial: 'r1'})-[:FEEDS*]->(b:Robot {serial: 'r4'}))
        RETURN [n IN nodes(p) | n.serial] AS route, length(p) AS hops""",
    "Where is gearbox G-200 used?": """
        MATCH (s:Site)-[:HAS_LINE]->(l:Line)-[:HAS_ROBOT]->(r:Robot)-[u:USES]->(p:Part {number: 'G-200'})
        RETURN s.name AS site, l.name AS line, r.serial AS robot, u.qty AS qty ORDER BY site, robot""",
    "Which parts does stock not cover?": """
        MATCH (r:Robot)-[u:USES]->(p:Part)
        WITH p, sum(u.qty) AS installed, count(r) AS robots
        WHERE installed > p.stock
        RETURN p.name AS part, robots, installed, p.stock AS in_stock""",
    "Which robots are due for service, per site?": """
        MATCH (s:Site)-[:HAS_LINE]->(:Line)-[:HAS_ROBOT]->(r:Robot)
        WHERE r.hours > 4000
        RETURN s.name AS site, count(r) AS due, collect(r.serial) AS robots ORDER BY due DESC""",
    "Which lines have two or more robots due?": """
        MATCH (l:Line)
        WHERE COUNT { (l)-[:HAS_ROBOT]->(r:Robot) WHERE r.hours > 4000 } >= 2
        RETURN l.name AS line""",
    "Whose notes mention gearbox vibration?": """
        CALL text_search('Robot', 'notes', 'gearbox vibration', 5) YIELD node, score
        RETURN node.serial AS robot, node.notes AS notes, score""",
}


def show(title: str, result: dict) -> None:
    print(f"\n{title}\n  {result['columns']}")
    for row in result["rows"]:
        print("  ", json.dumps(row, ensure_ascii=False))


db = TvennDB(graph=GRAPH)
db.put(f"/v1/graphs/{GRAPH}", {})  # create the graph (idempotent)
db.put(f"/v1/graphs/{GRAPH}/ontology", {"ontology": ONTOLOGY, "message": "plant ontology"})
for label in ("Site", "Line", "Robot", "Part"):  # start over when run again
    db.query(f"MATCH (n:{label}) DETACH DELETE n", message="reset")
db.query(SEED, message="Initial plant model", tags={"source": "erp-import"})

# The ontology refuses what does not fit, before it reaches the data.
try:
    db.query("MATCH (r:Robot {serial: 'r4'}) SET r.status = 'broken'", message="typo")
except TvennDBError as e:
    print("refused:", e)

for title, gql in QUESTIONS.items():
    show(title, db.query(gql))

# What changed, when and why: a commit with the work order, then the past.
before = db.get("/v1/time")["ts"]
db.query("MATCH (r:Robot {serial: 'r1'}) SET r.status = 'maintenance'", message="Gearbox replacement",
         event_time="2026-10-24T06:30:00Z",
         tags={"source": "cmms", "actor": "work-order-4711", "reason": "gearbox vibration"})
status = "MATCH (r:Robot {serial: 'r1'}) RETURN r.status"
print("\nr1 now:   ", db.rows(status))
print("r1 before:", db.rows(status, as_of=before))
latest = db.get(f"/v1/graphs/{GRAPH}/history?id=Robot/r1")["versions"][0]
print("last change:", latest["changed"], "by", latest["commit"]["author"],
      "-", latest["commit"]["message"], latest["commit"]["tags"])
print("diff since before:", [(n["id"], n["changed"]) for n in db.get(f"/v1/graphs/{GRAPH}/diff?from={before}&mode=nodes")["nodes"]])

# A contractor who sees Plant South and no spare parts: a membrane.
try:
    db.delete("/principals/user:contractor")
except TvennDBError as e:
    if e.status != 404:
        raise
db.post("/principals", {"kind": "user", "name": "contractor", "password": "contractor-password-1",
                        "access": {"grants": {GRAPH: "read"},
                                   "membranes": {GRAPH: {"allow_roots": ["Site/south"], "deny_labels": ["Part"]}}}})
key = db.post("/principals/user:contractor/keys", {"name": "service-app"})["token"]
contractor = TvennDB.__new__(TvennDB)
contractor.url, contractor.graph, contractor.token = db.url, GRAPH, key
print("\nthe contractor sees")
print("  robots:", contractor.rows("MATCH (r:Robot) RETURN r.serial ORDER BY r.serial"))
print("  sites: ", contractor.rows("MATCH (s:Site) RETURN s.name"))
print("  parts: ", contractor.rows("MATCH (p:Part) RETURN count(p)"))
