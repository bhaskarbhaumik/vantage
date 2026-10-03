"""GCP Cloud Run Job deploy commands."""

from __future__ import annotations

import os

from ..models.config import Config


def gcp_cmds(cfg: Config, build: bool) -> tuple[list[list[str]], list[str]]:
    g = cfg.cloud.gcp
    project = os.environ.get(g.get("project_env", "GCP_PROJECT"), "") or "$GCP_PROJECT"
    region = g.get("region", "us-central1")
    repo = g.get("artifact_repo", "vantage")
    service = g.get("service", "vantage")
    image = f"{region}-docker.pkg.dev/{project}/{repo}/{cfg.cloud.image}:latest"

    cmds: list[list[str]] = []
    if build:
        cmds.append([
            "gcloud", "artifacts", "repositories", "create", repo,
            "--repository-format=docker", f"--location={region}", f"--project={project}",
            "--quiet",
        ])
        cmds.append(["gcloud", "builds", "submit", "--tag", image, f"--project={project}"])
    cmds.append([
        "gcloud", "run", "jobs", "deploy", service,
        "--image", image, f"--region={region}", f"--project={project}",
        f"--memory={g.get('memory', '2Gi')}", f"--cpu={g.get('cpu', '2')}",
        f"--task-timeout={g.get('timeout', '3600s')}", "--max-retries=1",
        "--set-secrets=ANTHROPIC_API_KEY=anthropic-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest",
        "--set-env-vars=VANTAGE_BACKEND=api,VANTAGE_OUTPUT_DIR=/data/runs",
    ])
    notes = [
        "Store secrets first: gcloud secrets create anthropic-api-key --data-file=- (etc.).",
        "Run the job:  gcloud run jobs execute vantage --region "
        f"{region} --args='run,--client,ACME,--slug,acme-2026-08,--backend,api'",
        "For persisted output, mount a GCS volume or add a Cloud Storage sink.",
    ]
    return cmds, notes
