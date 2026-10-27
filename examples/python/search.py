"""Vector and full-text search over document chunks, in their own graph.

Each manual is split into chunks; a chunk carries its text (full-text index)
and an embedding (vector index). The embeddings here are a toy: words hashed
into 16 dimensions, so the example runs with nothing installed. A real
application computes them with an embedding model (for example
all-MiniLM-L6-v2, 384 dimensions) and declares that dimension in the ontology.

    TVENNDB_PASSWORD=<admin password> python3 search.py
"""
import hashlib
import math

from tvenndb_http import TvennDB

DIM = 16
GRAPH = "manuals"


def embed(text: str) -> list[float]:
    v = [0.0] * DIM
    for word in text.lower().split():
        h = hashlib.sha256(word.strip(".,").encode()).digest()
        v[h[0] % DIM] += 1.0 if h[1] % 2 else -1.0
    norm = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norm for x in v]


ONTOLOGY = {
    "labels": {
        "Manual": {"key": "id", "properties": {"id": {"type": "string", "required": True},
                                               "title": {"type": "string"}}},
        "Chunk": {"key": "id", "properties": {
            "id": {"type": "string", "required": True},
            "text": {"type": "string", "fulltext": True},
            "embedding": {"type": "vector", "dim": DIM}}},
    },
    "relations": {"HAS_CHUNK": {"from": ["Manual"], "to": ["Chunk"], "containment": True}},
}

MANUALS = {
    "gearbox": ("Gearbox service manual", [
        "Check the gearbox oil level every 500 operating hours.",
        "Vibration above 4 mm/s on the gearbox housing indicates bearing wear.",
        "Replace the gearbox seals when oil leaks at the output shaft.",
    ]),
    "gripper": ("Vacuum gripper manual", [
        "Clean the suction cups weekly to keep the vacuum stable.",
        "A vacuum below 60 kPa means a leaking hose or a worn cup.",
    ]),
}

db = TvennDB(graph=GRAPH)
db.put(f"/v1/graphs/{GRAPH}", {})  # create the graph (idempotent)
db.put(f"/v1/graphs/{GRAPH}/ontology", {"ontology": ONTOLOGY, "message": "manuals ontology"})
db.query("MATCH (m:Manual) DETACH DELETE m", message="reset")
db.query("MATCH (c:Chunk) DETACH DELETE c", message="reset")

for mid, (title, chunks) in MANUALS.items():
    db.query("INSERT (:Manual {id: $id, title: $title})", {"id": mid, "title": title}, message=f"manual {mid}")
    for i, text in enumerate(chunks):
        db.query("MATCH (m:Manual {id: $m}) INSERT (m)-[:HAS_CHUNK]->(:Chunk {id: $id, text: $text, embedding: $e})",
                 {"m": mid, "id": f"{mid}-{i}", "text": text, "e": embed(text)}, message="chunk")

question = "gearbox vibration bearing"
print(f"vector search for {question!r}:")
for text, score in db.rows(
        "CALL vector_search('Chunk', 'embedding', $q, 3) YIELD node, score RETURN node.text, score",
        {"q": embed(question)}):
    print(f"  {score:.3f}  {text}")

print(f"full-text search for {question!r}:")
for text, score in db.rows(
        "CALL text_search('Chunk', 'text', $q, 3) YIELD node, score RETURN node.text, score",
        {"q": question}):
    print(f"  {score:.3f}  {text}")

print("vector search within one manual (root):")
for text, score in db.rows(
        "CALL vector_search('Chunk', 'embedding', $q, 2, {root: 'Manual/gripper'}) YIELD node, score RETURN node.text, score",
        {"q": embed("vacuum leak")}):
    print(f"  {score:.3f}  {text}")
