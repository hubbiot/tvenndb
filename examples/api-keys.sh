#!/usr/bin/env bash
# A service principal with read access to one graph, and an API key for it.
# Use keys for applications, scripts and MCP clients instead of a password.
#
#   TVENNDB_PASSWORD=<admin password> ./api-keys.sh [name] [graph]
set -euo pipefail

URL="${TVENNDB_URL:-http://localhost:7000}"
PASSWORD="${TVENNDB_PASSWORD:?set TVENNDB_PASSWORD to the admin password}"
NAME="${1:-dashboard}"
GRAPH="${2:-default}"

py() { python3 -c "$@"; }
TOKEN=$(curl -sf -X POST "$URL/auth/login" -H 'content-type: application/json' \
  -d "$(py 'import json,sys; print(json.dumps({"username": sys.argv[1], "password": sys.argv[2]}))' "${TVENNDB_USER:-admin}" "$PASSWORD")" \
  | py 'import json,sys; print(json.load(sys.stdin)["token"])')
auth=(-H "authorization: Bearer $TOKEN" -H 'content-type: application/json')

# The principal: "read" on one graph. Other roles: "write", "schema", "admin";
# "*" grants on every graph. Membranes narrow it further (docs: API "Administration").
# Service principals are named svc:<name>; a second run reuses the one it made.
ID="svc:$NAME"
if ! curl -sf "$URL/v1/principals/$ID" "${auth[@]}" >/dev/null; then
  curl -sf -X POST "$URL/v1/principals" "${auth[@]}" -o /dev/null -d "$(py 'import json,sys; print(json.dumps(
    {"kind": "service", "name": sys.argv[1], "access": {"grants": {sys.argv[2]: "read"}}}))' "$NAME" "$GRAPH")"
fi

# The key is shown once; store it in your secret manager.
KEY=$(curl -sf -X POST "$URL/v1/principals/$ID/keys" "${auth[@]}" -d '{"name": "example", "ttl_days": 90}' \
  | py 'import json,sys; print(json.load(sys.stdin)["token"])')
echo "principal: $ID"
echo "api key:   $KEY"

# Use it: as a bearer token or in X-API-Key.
echo "graphs it can read: $(curl -sf "$URL/v1/graphs" -H "x-api-key: $KEY" \
  | py 'import json,sys; print([g["name"] for g in json.load(sys.stdin)["graphs"]])')"
echo "a write is refused: HTTP $(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL/v1/graphs/$GRAPH/query" \
  -H "authorization: Bearer $KEY" -H 'content-type: application/json' -d '{"query": "INSERT (:Site {code: '"'"'x'"'"'})"}')"
