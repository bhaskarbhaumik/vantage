# Deployment

The engine ships as one container image (`Dockerfile`) that runs as either:

- a **service**: `vantage serve` (the image default) with `GET /healthz` and `POST /run`, where the
  body is a JSON run job and the response is the result; or
- a **batch job**: the image's arguments become a `vantage run` command, for example
  `run --client "Example Corp" --slug example-2026-10 --backend api`.

A dossier takes minutes, so the **job/task** model is the recommended default on every cloud. The
image's entry point is `vantage-engine`, the alias of `vantage`. Per-cloud details and manifests
live in [deploy/](../deploy/README.md).

## The default backend does not deploy

`workflow` runs on the Claude Code CLI and needs an interactive Claude login, so cloud deployments
use `--backend api` (or a framework backend) with `--auth api-key`. That is **billed per token**
([Authentication and billing](auth.md)). The deploy helper sets `VANTAGE_BACKEND=api` in the
task environment.

## Build and deploy

```bash
uv run vantage deploy --target gcp   --dry-run     # print the exact commands
uv run vantage deploy --target azure --dry-run
uv run vantage deploy --target aws   --dry-run
uv run vantage deploy --target gcp                 # run them (needs gcloud / az / aws, signed in)
uv run vantage deploy --target gcp --no-build      # reuse an image you already pushed
```

`--target` defaults to `cloud.target`. On `deploy`, `-t` means `--target`, so spell the global
`--tier` in full there. The per-cloud settings (`cloud.gcp.region`, `cloud.azure.location`,
`cloud.aws.cluster`, …) are in the [configuration](configuration.md#cloud), and the cloud CLIs
read `GCP_PROJECT`, `AZURE_RESOURCE_GROUP`, `AWS_REGION` and friends from the environment.

Add framework or cloud extras to the image at build time:

```bash
docker build --build-arg EXTRAS="langgraph,cloud-gcp" -t vantage .
```

The image installs the core engine; add `export` to `EXTRAS` if the container should run
`vantage export`.

## Secrets

Never bake keys into the image. Provide at least:

| Secret | Used by |
|---|---|
| `ANTHROPIC_API_KEY` | `api`, `agent-sdk`, `langgraph`, `adk`, `crewai` |
| `TAVILY_API_KEY` | Web search |
| `SEC_EDGAR_IDENTITY` | SEC EDGAR (`"Name email@example.com"`) |
| `OPENAI_API_KEY`, `GOOGLE_API_KEY` | Optional multi-provider routing |

- **GCP:** Secret Manager (`--set-secrets`), see [deploy/gcp](../deploy/gcp/README.md).
- **Azure:** Container Apps secrets (`--secrets`), see [deploy/azure](../deploy/azure/README.md).
- **AWS:** Secrets Manager (`secrets[].valueFrom`), see [deploy/aws](../deploy/aws/README.md) and
  `deploy/aws/task-def.json`.

## Persisting output

Runs write to `/data/runs` (`VANTAGE_OUTPUT_DIR`) and the image declares `/data` as a volume.
Mount durable storage (a Cloud Storage volume on Cloud Run, an Azure Files share on Container
Apps, EFS on Fargate), or the output lives only as long as the task.

## The HTTP service

`vantage serve --host 0.0.0.0 --port 0` listens on `$PORT`, or 8080 when `--port` is `0` and
`PORT` is unset. It is a small standard-library server that runs one job per request,
synchronously. Put a queue or a job trigger in front of it for anything beyond low concurrency.
