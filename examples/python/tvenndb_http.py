"""A small TvennDB HTTP helper on the Python standard library alone.

Enough for the examples next to it: sign in with a password or an API key,
run GQL with parameters, read the past with ``as_of``. Copy it into your own
project or call the HTTP API from any language the same way.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class TvennDBError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


class TvennDB:
    def __init__(self, url: str | None = None, graph: str = "default"):
        self.url = (url or os.environ.get("TVENNDB_URL", "http://localhost:7000")).rstrip("/")
        self.graph = graph
        key = os.environ.get("TVENNDB_API_KEY")
        if key:
            self.token = key
        else:
            user = os.environ.get("TVENNDB_USER", "admin")
            password = os.environ.get("TVENNDB_PASSWORD")
            if not password:
                raise SystemExit("set TVENNDB_API_KEY, or TVENNDB_PASSWORD (and TVENNDB_USER)")
            self.token = self._call("POST", "/auth/login", {"username": user, "password": password}, auth=False)["token"]

    def _call(self, method: str, path: str, body: dict | None = None, auth: bool = True) -> dict:
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(self.url + path, data=data, method=method)
        req.add_header("content-type", "application/json")
        if auth:
            req.add_header("authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as e:
            raise TvennDBError(e.code, e.read().decode(errors="replace")) from None

    def get(self, path: str) -> dict:
        return self._call("GET", path)

    def put(self, path: str, body: dict) -> dict:
        return self._call("PUT", path, body)

    def post(self, path: str, body: dict) -> dict:
        return self._call("POST", path, body)

    def query(self, gql: str, params: dict | None = None, *, message: str | None = None,
              as_of: int | None = None, tags: dict | None = None, event_time: str | None = None) -> dict:
        """Run GQL. A write records ``message``, ``tags`` (your own source, actor
        or reason) and ``event_time`` (when it happened in the world) with its commit."""
        body: dict = {"query": gql}
        if params:
            body["params"] = params
        if message:
            body["message"] = message
        if as_of is not None:
            body["as_of"] = as_of
        if tags:
            body["tags"] = tags
        if event_time:
            body["event_time"] = event_time
        return self.post(f"/v1/graphs/{self.graph}/query", body)

    def delete(self, path: str) -> dict:
        return self._call("DELETE", path)

    def rows(self, gql: str, params: dict | None = None, **kw) -> list:
        return self.query(gql, params, **kw)["rows"]
