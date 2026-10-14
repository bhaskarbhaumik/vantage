# Authentication and billing

**Vantage runs on your Claude subscription by default, and API billing is always an explicit
opt-in.**

## The two modes

| `auth.mode` | Who pays | What is read |
|---|---|---|
| `subscription` *(default)* | Your Claude plan, through the Claude Code CLI | **No API key**, even one that is exported |
| `api-key` | The provider account behind each key, **per token** | The keys named by the config, from environment variables |

In `subscription` mode the engine deliberately ignores `ANTHROPIC_API_KEY` and the other provider
keys. An exported key left over from another tool cannot turn a plan-funded run into a metered
one.

Subscription mode works with the `workflow` and `agent-sdk` backends. The others talk to provider
APIs directly and report *cannot use the Claude subscription* until you opt into `api-key`.

## Opting into API billing

> **Billing warning.** Every `api-key` run is billed per token to the provider accounts whose keys
> you supply. A `FULL_ANNEX` dossier runs 29 agents with web research and can consume a large
> number of tokens. Try `--tier EXECUTIVE` first.

```bash
uv run vantage auth status                                  # current mode, classes, key presence
export ANTHROPIC_API_KEY=...                                # in your shell or .env, never in config
uv run vantage run --client "Example Corp" --backend api --auth api-key            # this run only
uv run vantage run --client "Example Corp" --backend api --auth api-key --ask-key  # prompt for a missing key
uv run vantage auth use api-key                             # make it the persistent default
uv run vantage auth use subscription                        # and back
```

- `--ask-key` prompts on the terminal for any key that is not already in the environment. The key
  lives in that process only; it is never stored or logged. It is ignored (with a warning) in
  subscription mode.
- Persisting `api-key` (`auth use` or `config set auth.mode api-key`) prints a billing warning.
- In api-key mode `vantage run` also warns at the start of every run that it is billed per token.

## Credential classes

The agents fall into two classes with different cost profiles, so they can bill to different
accounts or vendors:

| Class | Agents | Config |
|---|---|---|
| `orchestrator` | preflight, backbone, merge, reconcile, synthesis, verification, assembly (13) | `auth.orchestrator` |
| `research` | the section-wise deep-research agents: Wave A, Wave B, vertical annex (16) | `auth.research` |

Each takes `provider`, `api_key_env`, `model` and `model_env`; unset fields inherit from the
agent's model tier. For example, research fan-out on Gemini with its own key, orchestration on
Claude:

```json
"auth": {
  "mode": "api-key",
  "research": { "provider": "gemini", "api_key_env": "VANTAGE_RESEARCH_KEY" }
}
```

Enable the provider first (`providers.gemini.enabled: true`). A key is resolved from the profile's
`api_key_env`, then `providers.<provider>.api_key_env`, then the provider's standard variable. If
it is missing: with `--ask-key`, a hidden prompt; otherwise the run fails and names the variable.

`ANTHROPIC_MODEL` (the variable named by `auth.model_env`), if set, pins every Anthropic-routed
agent to one model. `doctor` and `run` warn, because it collapses the `role_model_map` tiers.

## What can still move you off your plan

These redirect the **Claude Code CLI itself** (to a gateway, Amazon Bedrock or Google Vertex) and
are outside Vantage's control: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`. Leave them unset if
you expect a plan-funded run. Check with:

```bash
for v in ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN VANTAGE_AUTH_MODE; do
  printenv "$v" >/dev/null 2>&1 && echo "$v is set" || echo "$v is unset"
done
```

Other things that spend money only when you turn them on: the `napkin` export helper
(`export.helpers.illustrations`, spends Napkin credits) and the keyed export helpers
([Export](export.md#visual-helpers)).

## Rules the code keeps

- Keys live in environment variables only. Config keys ending in `_env` hold the *name* of a
  variable. `vantage config set` refuses values that look like credentials.
- Keys are never written to disk and never logged. `doctor` and `auth status` report only whether
  a variable is set.
- A change that could make a run metered without the user asking is a bug
  ([CONTRIBUTING.md](../CONTRIBUTING.md#configuration-and-secrets)).
