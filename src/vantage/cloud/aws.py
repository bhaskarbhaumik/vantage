"""AWS ECS Fargate task deploy commands (build → ECR → register task def)."""

from __future__ import annotations

import os

from ..models.config import Config


def aws_cmds(cfg: Config, build: bool) -> tuple[list[list[str]], list[str]]:
    w = cfg.cloud.aws
    region = os.environ.get("AWS_REGION", w.get("region", "us-east-1"))
    acct = os.environ.get("AWS_ACCOUNT_ID", "$AWS_ACCOUNT_ID")
    ecr = w.get("ecr_repo", "vantage")
    registry = f"{acct}.dkr.ecr.{region}.amazonaws.com"
    image = f"{registry}/{ecr}:latest"

    cmds: list[list[str]] = []
    if build:
        cmds.append(["aws", "ecr", "create-repository", "--repository-name", ecr, "--region", region])
        # login: piped in real use; shown as two steps
        cmds.append(["bash", "-lc",
                     f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {registry}"])
        cmds.append(["docker", "build", "-t", image, "."])
        cmds.append(["docker", "push", image])
    cmds.append(["aws", "ecs", "register-task-definition", "--cli-input-json",
                 "file://deploy/aws/task-def.json", "--region", region])
    notes = [
        "Fill deploy/aws/task-def.json with your execution-role ARN, the image URI above, and "
        "secrets from AWS Secrets Manager (ANTHROPIC_API_KEY, TAVILY_API_KEY).",
        "Run a task:  aws ecs run-task --cluster vantage --task-definition vantage "
        "--launch-type FARGATE --overrides '{\"containerOverrides\":[{\"name\":\"vantage\","
        "\"command\":[\"run\",\"--client\",\"ACME\",\"--slug\",\"acme-2026-08\",\"--backend\",\"api\"]}]}'",
        "Attach an EFS volume for persisted /data output.",
    ]
    return cmds, notes
