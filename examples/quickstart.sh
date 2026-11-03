#!/usr/bin/env bash
# A first graph over the HTTP API: sign in, activate an ontology, write with
# GQL, query, read the past with as_of and list a node's history.
#
# Needs curl and python3 (for JSON), and a running TvennDB (see ../compose).
#   TVENNDB_PASSWORD=<admin password> ./quickstart.sh
set -euo pipefail

URL="${TVENNDB_URL:-http://localhost:7000}"
USER_NAME="${TVENNDB_USER:-admin}"
PASSWORD="${TVENNDB_PASSWORD:?set TVENNDB_PASSWORD to the admin password}"
GRAPH="${TVENNDB_GRAPH:-default}"
HERE="$(cd "$(dirname "$0")" && pwd)"

json() { python3 -c 'import json,sys; print(json.dumps(dict(zip(sys.argv[1::2], sys.argv[2::2]))))' "$@"; }
field() { python3 -c 'import json,sys; v=json.load(sys.stdin)
for k in sys.argv[1].split("."): v=v[k]
print(v if isinstance(v, str) else json.dumps(v))' "$1"; }

# 1. Sign in. The token is a session; API keys work the same way (api-keys.sh).
TOKEN=$(curl -sf -X POST "$URL/auth/login" -H 'content-type: application/json' \
  -d "$(json username "$USER_NAME" password "$PASSWORD")" | field token)
auth=(-H "authorization: Bearer $TOKEN" -H 'content-type: application/json')

# 2. The ontology: labels with typed properties and a key, relations with
#    their ends. Writes that do not fit it are refused with 422.
body=$(python3 -c 'import json,sys; print(json.dumps({"ontology": json.load(open(sys.argv[1])), "message": "quick start ontology"}))' \
  "$HERE/plant-ontology.json")
echo "ontology: $(curl -sf -X PUT "$URL/v1/graphs/$GRAPH/ontology" "${auth[@]}" -d "$body")"

# 3. Write and read with GQL. Every write is a commit with a message.
q() {
  curl -sf -X POST "$URL/v1/graphs/$GRAPH/query" "${auth[@]}" \
    -d "$(python3 -c 'import json,sys; print(json.dumps({"query": sys.argv[1], "message": "quick start"}))' "$1")"
}
q "MATCH (s:Site) DETACH DELETE s" >/dev/null   # start over when run again
q "MATCH (l:Line) DETACH DELETE l" >/dev/null
q "MATCH (r:Robot) DETACH DELETE r" >/dev/null
q "INSERT (:Site {code:'s1', name:'Plant 1'})-[:HAS_LINE]->(:Line {code:'s1-l1', name:'Line 1'})" >/dev/null
q "MATCH (l:Line {code:'s1-l1'}) INSERT (l)-[:HAS_ROBOT]->(:Robot {serial:'r1', status:'running', hours: 120.5})" >/dev/null
q "MATCH (l:Line {code:'s1-l1'}) INSERT (l)-[:HAS_ROBOT]->(:Robot {serial:'r2', status:'idle', hours: 8})" >/dev/null
BEFORE=$(q "MATCH (a:Robot {serial:'r1'}), (b:Robot {serial:'r2'}) INSERT (a)-[:FEEDS]->(b)" | field stats.ts)

echo "robots: $(q "MATCH (s:Site)-[:HAS_LINE]->(:Line)-[:HAS_ROBOT]->(r:Robot) RETURN s.name, r.serial, r.status ORDER BY r.serial" | field rows)"

# 4. Change something, then read the graph as it was before the change.
q "MATCH (r:Robot {serial:'r1'}) SET r.status = 'maintenance', r.hours = r.hours + 8" >/dev/null
echo "r1 now:    $(q "MATCH (r:Robot {serial:'r1'}) RETURN r.status, r.hours" | field rows)"
echo "r1 before: $(curl -sf -X POST "$URL/v1/graphs/$GRAPH/query" "${auth[@]}" \
  -d "{\"query\": \"MATCH (r:Robot {serial: \$s}) RETURN r.status, r.hours\", \"params\": {\"s\": \"r1\"}, \"as_of\": $BEFORE}" | field rows)"

# 5. Every version of a node, with the commit that made it.
echo "history of Robot/r1:"
curl -sf "$URL/v1/graphs/$GRAPH/history?id=Robot/r1" "${auth[@]}" | python3 -m json.tool | head -40

echo
echo "Open $URL/ui/ and sign in as $USER_NAME to see the graph in the Explorer."
