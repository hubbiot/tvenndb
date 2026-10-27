# TvennDB on Kubernetes

The chart is published as an OCI artifact on GitHub's container registry:

```bash
helm show values oci://ghcr.io/hubbiot/charts/tvenndb --version 1.0.1
helm install tvenndb oci://ghcr.io/hubbiot/charts/tvenndb --version 1.0.1 \
  -n tvenndb --create-namespace -f values-dev.yaml
```

| File | For |
|---|---|
| [values-dev.yaml](values-dev.yaml) | development and CI: one gateway, one shard, small requests |
| [values-ha.yaml](values-ha.yaml) | production: 3 gateways, 3 shard members on separate nodes, Ingress, S3 backups, Prometheus |

## What the chart sets up

- **Gateways** (StatefulSet): the API, the Explorer at `/ui/`, MCP at `/mcp`.
  More than one form a group that agrees on transactions; every member
  serves reads.
- **Shard groups** (one StatefulSet per group): the data. The members of a
  group replicate it with Raft, so three members tolerate the loss of one.
- **TLS everywhere**: the chart generates a CA and certificates at install
  and keeps them across upgrades, or uses yours (`tls.existingSecret`).
  Gateway to shard and member to member traffic is mutual TLS.
- **NetworkPolicies** that allow exactly the traffic the chart needs,
  PodDisruptionBudgets, and optional ServiceMonitors and alerting rules.

## First sign-in

The first start creates the user `admin`. With `auth.adminPassword` and
`auth.existingSecret` both empty, a password is generated:

```bash
kubectl -n tvenndb exec tvenndb-gateway-0 -- cat /data/initial-admin-password
kubectl -n tvenndb port-forward svc/tvenndb-gateway 7000:7000
# https://localhost:7000/ui/ (the chart's own CA signs the certificate)
```

Then make API keys for applications instead of sharing the password
([../examples/api-keys.sh](../examples/api-keys.sh)).

## Pinning images

Releases list the image digests. Pin them so a node never pulls anything else:

```yaml
image:
  tag: 1.0.1
  gatewayDigest: sha256:...
  shardDigest: sha256:...
```

## Air-gapped clusters

Copy the images and the chart into your registry, then point the chart at it:

```bash
for i in tvenndb-gateway tvenndb-shard; do
  skopeo copy --all docker://ghcr.io/hubbiot/$i:1.0.1 docker://registry.internal/tvenndb/$i:1.0.1
done
helm pull oci://ghcr.io/hubbiot/charts/tvenndb --version 1.0.1
helm push tvenndb-1.0.1.tgz oci://registry.internal/tvenndb/charts
```

```yaml
image:
  repository: registry.internal/tvenndb
```
