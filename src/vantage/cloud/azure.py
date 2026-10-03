"""Azure Container Apps Job deploy commands."""

from __future__ import annotations

import os

from ..models.config import Config


def azure_cmds(cfg: Config, build: bool) -> tuple[list[list[str]], list[str]]:
    a = cfg.cloud.azure
    rg = os.environ.get(a.get("resource_group_env", "AZURE_RESOURCE_GROUP"), "") or "$AZURE_RESOURCE_GROUP"
    location = a.get("location", "eastus")
    env_name = a.get("env", "vantage-env")
    job = a.get("app", "vantage")
    acr = f"{cfg.cloud.image}acr"  # ACR names are alphanumeric only
    image = f"{acr}.azurecr.io/{cfg.cloud.image}:latest"

    cmds: list[list[str]] = []
    if build:
        cmds.append(["az", "acr", "create", "--resource-group", rg, "--name", acr, "--sku", "Basic"])
        cmds.append(["az", "acr", "build", "--registry", acr, "--image", f"{cfg.cloud.image}:latest", "."])
    cmds.append(["az", "containerapp", "env", "create", "--name", env_name,
                 "--resource-group", rg, "--location", location])
    cmds.append([
        "az", "containerapp", "job", "create",
        "--name", job, "--resource-group", rg, "--environment", env_name,
        "--image", image, "--trigger-type", "Manual",
        "--cpu", str(a.get("cpu", 2.0)), "--memory", str(a.get("memory", "4Gi")),
        "--replica-timeout", "3600", "--replica-retry-limit", "1",
        "--secrets", "anthropic-key=$ANTHROPIC_API_KEY", "tavily-key=$TAVILY_API_KEY",
        "--env-vars",
        "ANTHROPIC_API_KEY=secretref:anthropic-key", "TAVILY_API_KEY=secretref:tavily-key",
        "VANTAGE_BACKEND=api", "VANTAGE_OUTPUT_DIR=/data/runs",
    ])
    notes = [
        "Start the job:  az containerapp job start --name vantage --resource-group "
        f"{rg} --args 'run --client ACME --slug acme-2026-08 --backend api'",
        "Mount an Azure Files share for persisted /data output.",
    ]
    return cmds, notes
