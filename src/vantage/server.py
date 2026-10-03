"""Minimal stdlib HTTP server for service-style cloud deployments.

`GET /healthz` → liveness. `POST /run` with a JSON RunJob body → runs the pipeline synchronously
and returns the result JSON. Dependency-free (http.server). For high throughput, put a queue in
front — a dossier run takes minutes; this is intended for Cloud Run / Container Apps behind a job
trigger or a low-concurrency service.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .blueprint import Blueprint
from .engine import get_backend
from .logging import EventEmitter, get_logger
from .pipeline.orchestrator import RunJob
from .settings import harness_dir, load_config, output_dir

log = get_logger()


def _today() -> str:
    return _dt.date.today().isoformat()


def _make_handler(cfg, bp, hd):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, obj: dict) -> None:
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path.rstrip("/") in ("/healthz", "/health", ""):
                self._send(200, {"ok": True, "service": "vantage", "backend": cfg.engine.backend})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            if not self.path.startswith("/run"):
                self._send(404, {"error": "not found"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            try:
                data = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                self._send(400, {"error": "invalid JSON"})
                return
            if not data.get("client_legal_name") or not data.get("slug"):
                self._send(400, {"error": "client_legal_name and slug are required"})
                return
            job = RunJob(
                client_legal_name=data["client_legal_name"], slug=data["slug"],
                research_as_of=data.get("research_as_of") or _today(),
                client_common_name=data.get("client_common_name", ""),
                ticker_or_private=data.get("ticker_or_private", cfg.run_defaults.ticker_or_private),
                primary_geography=data.get("primary_geography", cfg.run_defaults.primary_geography),
                target_vertical=data.get("target_vertical", cfg.run_defaults.target_vertical),
                tier=(data.get("tier") or cfg.engine.tier).upper(),
                capability_pack=data.get("capability_pack", cfg.run_defaults.capability_pack),
                account_team_input_sheet=data.get("account_team_input_sheet", cfg.run_defaults.account_team_input_sheet),
                account_context=data.get("account_context", cfg.run_defaults.account_context),
                known_relationship_context=data.get("known_relationship_context", cfg.run_defaults.known_relationship_context),
                strategic_pursuit_objectives=data.get("strategic_pursuit_objectives", cfg.run_defaults.strategic_pursuit_objectives),
            )
            backend = data.get("backend") or cfg.engine.backend
            emitter = EventEmitter(jsonl_path=output_dir(cfg) / job.slug / "run.jsonl")
            try:
                be = get_backend(backend, cfg, bp, hd, emitter)
                result = asyncio.run(be.run(job))
            except Exception as e:  # pragma: no cover
                self._send(500, {"error": str(e)})
                return
            self._send(200, {
                "slug": result.slug, "run_dir": result.run_dir, "dossier": result.dossier,
                "entity": result.entity, "ownership_form": result.ownership_form,
                "jurisdictions": result.jurisdictions,
                "entity_ambiguity": result.entity_ambiguity,
                "agents_ok": result.agents_ok, "agents_total": result.agents_total,
                "verification": result.verification, "usage": result.usage,
                "errors": result.errors,
            })

        def log_message(self, *args) -> None:  # silence default logging
            pass

    return Handler


def serve(host: str = "0.0.0.0", port: int | None = None) -> None:
    cfg = load_config()
    hd = harness_dir(cfg)
    bp = Blueprint(hd)
    port = port or int(os.environ.get("PORT", "8080"))
    httpd = ThreadingHTTPServer((host, port), _make_handler(cfg, bp, hd))
    log.info(f"vantage serving on {host}:{port} (backend {cfg.engine.backend})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()
