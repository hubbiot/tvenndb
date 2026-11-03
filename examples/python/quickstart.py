"""The quick start in Python: ontology, writes, a query and time travel.

    TVENNDB_PASSWORD=<admin password> python3 quickstart.py
"""
import json
from pathlib import Path

from tvenndb_http import TvennDB

db = TvennDB(graph="default")

ontology = json.loads((Path(__file__).parent.parent / "plant-ontology.json").read_text())
print("ontology:", db.put(f"/v1/graphs/{db.graph}/ontology", {"ontology": ontology, "message": "python quick start"}))

for label in ("Site", "Line", "Robot"):  # start over when run again
    db.query(f"MATCH (n:{label}) DETACH DELETE n", message="reset")

db.query("INSERT (:Site {code: $site, name: 'Plant 1'})-[:HAS_LINE]->(:Line {code: $line, name: 'Line 1'})",
         {"site": "s1", "line": "s1-l1"}, message="new site")
robots = [{"serial": "r1", "status": "running", "hours": 120.5}, {"serial": "r2", "status": "idle", "hours": 8.0}]
for r in robots:
    db.query("MATCH (l:Line {code: 's1-l1'}) INSERT (l)-[:HAS_ROBOT]->(:Robot {serial: $serial, status: $status, hours: $hours})",
             r, message=f"robot {r['serial']} installed")

before = db.get("/v1/time")["ts"]
db.query("MATCH (r:Robot {serial: 'r1'}) SET r.status = 'maintenance'", message="r1 to maintenance")

q = "MATCH (r:Robot) RETURN r.serial, r.status ORDER BY r.serial"
print("now:   ", db.rows(q))
print("before:", db.rows(q, as_of=before))
