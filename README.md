<h1>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="images/logo/svg/horizontal-tagline/tvenndb-horizontal-tagline-on-dark.svg">
    <img alt="TvennDB, graph database for digital twins" src="images/logo/svg/horizontal-tagline/tvenndb-horizontal-tagline-on-light.svg" height="72">
  </picture>
</h1>

A sharded, versioned, ontology-enforced graph database for industrial
digital twins, by Hubbiot AB. This is **TvennDB Free**: free to use, also in
production and commercially.

- **Ontology-enforced writes**: labels with typed, constrained properties and
  keys; relations with allowed ends and cardinality. Writes that do not fit
  are refused.
- **Git-like history**: every write is a commit with author and message;
  any query can run `as_of` any past moment; every node's versions and the
  diff between two moments are one call away.
- **Sharded and replicated**: everything under one asset lives on one shard;
  shard groups replicate with Raft; multi-shard writes commit atomically.
- **GQL**, vector search, full-text search and property indexes in one query
  language.
- **Access control**: users, API keys and roles per graph, and membranes
  that hide labels or confine a principal to subtrees.
- **Built for AI assistants**: an MCP endpoint on every gateway, under the
  same access control as the API.
- **A web Explorer** for the graph, its history, the ontology, events,
  access and storage.

This repository holds the examples, the issue tracker and the releases.
TvennDB ships as container images and a Helm chart; the source code is not
published.

## Quick start

```bash
git clone https://github.com/hubbiot/tvenndb.git && cd tvenndb/compose
cp .env.example single/.env       # set TVENNDB_ADMIN_PASSWORD (12+ characters)
cd single && docker compose up -d
```

Open <http://localhost:7000/ui/> and sign in as `admin`, then run the
examples:

```bash
cd ../../examples
TVENNDB_PASSWORD=<your password> ./quickstart.sh
```

## Images and chart

| Artifact | Where |
|---|---|
| Gateway (API, Explorer, MCP; also a single-process dev mode) | `ghcr.io/hubbiot/tvenndb-gateway` |
| Shard | `ghcr.io/hubbiot/tvenndb-shard` |
| Command line tool `tvenn` | `ghcr.io/hubbiot/tvenndb`, and static Linux binaries (x86_64, aarch64) under [Releases](https://github.com/hubbiot/tvenndb/releases) |
| Helm chart | `oci://ghcr.io/hubbiot/charts/tvenndb` |

Images are built for `linux/amd64` and `linux/arm64`; `docker pull` picks
the right one. Each release lists its image digests; pin them in production.

## What is here

| Path | What |
|---|---|
| [compose/single](compose/single) | one container: a gateway with embedded shards; development and small installations |
| [compose/cluster](compose/cluster) | a replicated shard group of three behind a gateway, on one Docker host |
| [helm](helm) | Kubernetes: values for development and high availability |
| [examples/quickstart.sh](examples/quickstart.sh) | the HTTP API with curl: ontology, writes, queries, time travel, history |
| [examples/python](examples/python) | the same in Python (standard library only), plus vector and full-text search |
| [examples/python/plant_twin.py](examples/python/plant_twin.py) | an industrial twin: impact of a stop, where a part is used, service planning, what changed and why, a contractor confined to one site |
| [examples/api-keys.sh](examples/api-keys.sh) | a service principal with read access and an API key |
| [examples/mcp](examples/mcp) | connecting AI assistants (Claude Code, VS Code, Cursor, others) |
| [images/logo](images/logo) | the TvennDB logo in every version and colour, and the favicon set |
| [design](design) | the TvennDB design: colours, type, stylesheets, fonts and page patterns |

## Editions

TvennDB Free, here, holds the core of TvennDB: GQL, the ontology, history
and time travel, vector and full-text search, sharding, replication,
transactions across shards, backup and restore, users, API keys, roles,
membranes, the MCP endpoint, events and webhooks, import and export, the
Explorer and Prometheus metrics.

TvennDB Enterprise is **not yet available**. It will add single sign-on,
the audit log, usage reports, rate and size limits per key, and online
rebalancing and partition moves, under a commercial licence from Hubbiot AB.
On TvennDB Free their API routes answer `501`;
`docker run --rm ghcr.io/hubbiot/tvenndb-gateway:<version> --version` names
the edition. Interested? Get in touch through
[hubbiot.com](https://hubbiot.com/tvenndb/#editions).

## Licence

TvennDB Free (the images, binaries and chart) is free to use,
including in production and commercially, under the
[Elastic License 2.0](LICENSE). In short, you may use, copy and
redistribute it, also as part of your own products; you may not provide it
to others as a hosted or managed service, work around licence-key
functionality, or remove its licence notices. The licence text decides, not
this summary. The images carry `LICENSE`, `NOTICE` and
`THIRD-PARTY-NOTICES` under `/usr/share/doc/tvenndb/`.

The examples, compose files and Helm values in this repository are under
the same licence, so you can copy and adapt them for your own installations.

The TvennDB name and logo are trademarks of Hubbiot AB and are not covered
by the licence; [images/logo](images/logo/README.md) says how to use them.
The fonts in [design/fonts](design/fonts) are under the SIL Open Font
License 1.1.

## Support

- Questions and bugs: [issues](https://github.com/hubbiot/tvenndb/issues).
- Security vulnerabilities: privately, see [SECURITY.md](SECURITY.md).
- Commercial licences and support: <https://hubbiot.com/tvenndb>.
