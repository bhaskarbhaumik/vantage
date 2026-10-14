# Azure — Container Apps Job

```bash
# 1. Build + create the job (or: vantage deploy --target azure)
uv run vantage deploy --target azure

# 2. Start a dossier run
az containerapp job start --name vantage --resource-group "$AZURE_RESOURCE_GROUP" \
  --args 'run --client "Acme Industries, Inc." --slug acme-2026-08 --backend api --depth STANDARD'
```

Config: `config/default.json → cloud.azure` (resource group via `$AZURE_RESOURCE_GROUP`, location,
environment, cpu/memory). Secrets are Container Apps secrets referenced as `secretref:`. Persist
output with an Azure Files share mounted at `/data`.
