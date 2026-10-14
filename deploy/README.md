# Deploying the Vantage engine

The engine ships as one portable image (`Dockerfile`) that runs either as a **service**
(`vantage serve` — `GET /healthz`, `POST /run`) or a **batch job**
(`vantage run --client … --slug … --backend api`). Dossier runs take minutes, so the
**job/task** model is the default recommendation on every cloud.

Deploy with the built-in helper (prints the exact commands with `--dry-run`):

```bash
uv run vantage deploy --target gcp   --dry-run
uv run vantage deploy --target azure --dry-run
uv run vantage deploy --target aws   --dry-run
```

Drop `--dry-run` to execute (needs the cloud CLI: `gcloud` / `az` / `aws`, authenticated).

## Secrets (all clouds)

Never bake keys into the image. Provide at minimum:

| Secret | Used by |
|--------|---------|
| `ANTHROPIC_API_KEY` | api / agent-sdk / langgraph / adk / crewai backends |
| `TAVILY_API_KEY` | web search |
| `SEC_EDGAR_IDENTITY` | SEC EDGAR (`"Name email@example.com"`) |
| `OPENAI_API_KEY`, `GOOGLE_API_KEY` | optional multi-provider routing |

- **GCP** → Secret Manager (`--set-secrets`), see `gcp/README.md`.
- **Azure** → Container Apps secrets (`--secrets`), see `azure/README.md`.
- **AWS** → Secrets Manager (`secrets[].valueFrom`), see `aws/README.md` + `aws/task-def.json`.

## Persisting output

Runs write to `/data/runs` (`VANTAGE_OUTPUT_DIR`). Mount durable storage: a GCS volume (Cloud
Run), an Azure Files share (ACA), or EFS (Fargate) — otherwise output lives only for the task's
lifetime.

## The default (`workflow`) backend does not deploy to cloud

It runs on the Claude Code subscription and needs an interactive Claude Code session, so cloud
deployments use `--backend api` (or a framework backend). Set `VANTAGE_BACKEND=api` in the
task/job env (already done by the deploy helper).
