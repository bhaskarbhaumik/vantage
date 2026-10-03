# AWS — ECS Fargate task

```bash
# 1. Build + push + register (or: vantage-engine deploy --target aws)
uv run vantage-engine deploy --target aws

# 2. Fill in deploy/aws/task-def.json: <ACCOUNT_ID>, <REGION>, role ARNs, EFS id, secret ARNs.
#    Store secrets in Secrets Manager: anthropic-api-key, tavily-api-key, sec-edgar-identity.

# 3. Run a task
aws ecs run-task --cluster vantage --task-definition vantage --launch-type FARGATE \
  --network-configuration 'awsvpcConfiguration={subnets=[subnet-...],assignPublicIp=ENABLED}' \
  --overrides '{"containerOverrides":[{"name":"vantage","command":["run","--client","Acme Industries, Inc.","--slug","acme-2026-08","--backend","api"]}]}'
```

Config: `config/default.json → cloud.aws` (region, ECR repo, cluster, cpu/memory) and
`deploy/aws/task-def.json` (the Fargate task definition template). Persist output with the EFS
volume already declared in the task def.
