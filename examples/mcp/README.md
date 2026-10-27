# TvennDB as an MCP server

Every gateway serves the Model Context Protocol at `/mcp` (Streamable HTTP,
stateless). An AI assistant connected to it can list graphs, read the schema
and ontology, run GQL, and read node history, commits and diffs. The tools
are `describe`, `list_graphs`, `get_schema`, `get_ontology`,
`ontology_versions`, `query`, `node_history`, `commits`, `diff`,
`graph_stats` and `whoami`.

The assistant acts as the principal whose credential it sends, with that
principal's roles and membranes. Give it an API key of a principal
with **read** access, made for that purpose:

```bash
TVENNDB_PASSWORD=<admin password> ../api-keys.sh assistant default
```

Replace `tvk_...` below with the key it prints, and the URL with your
gateway's.

## Claude Code

```bash
claude mcp add --transport http tvenndb http://localhost:7000/mcp \
  --header "Authorization: Bearer tvk_..."
```

## VS Code (`.vscode/mcp.json`)

```json
{
  "servers": {
    "tvenndb": {
      "type": "http",
      "url": "http://localhost:7000/mcp",
      "headers": { "Authorization": "Bearer tvk_..." }
    }
  }
}
```

## Cursor (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "tvenndb": {
      "url": "http://localhost:7000/mcp",
      "headers": { "Authorization": "Bearer tvk_..." }
    }
  }
}
```

## Clients that only start local servers

Bridge with [`mcp-remote`](https://www.npmjs.com/package/mcp-remote):

```json
{
  "mcpServers": {
    "tvenndb": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:7000/mcp", "--header", "Authorization: Bearer tvk_..."]
    }
  }
}
```

## Check it by hand

```bash
curl -s -X POST http://localhost:7000/mcp \
  -H "Authorization: Bearer tvk_..." -H 'content-type: application/json' \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```
