# GCP — Cloud Run Job

```bash
# 1. Secrets
printf '%s' "$ANTHROPIC_API_KEY" | gcloud secrets create anthropic-api-key --data-file=-
printf '%s' "$TAVILY_API_KEY"    | gcloud secrets create tavily-api-key --data-file=-

# 2. Build + deploy the job (or: vantage deploy --target gcp)
uv run vantage deploy --target gcp

# 3. Execute a dossier
gcloud run jobs execute vantage --region us-central1 \
  --args='run,--client,Acme Industries\, Inc.,--slug,acme-2026-08,--backend,api,--depth,STANDARD'
```

Config: `config/default.json → cloud.gcp` (project via `$GCP_PROJECT`, region, artifact repo,
memory/cpu/timeout). Persist output with a Cloud Storage volume mount on the job.
