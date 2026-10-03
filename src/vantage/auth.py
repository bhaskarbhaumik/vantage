"""Credential resolution for the Vantage engine.

The default is the user's **Claude subscription**: in ``subscription`` mode nothing here reads an
API key, and a key sitting in the environment is deliberately ignored. That is the whole point of
the mode — an ``ANTHROPIC_API_KEY`` exported for some other tool must never silently turn a
subscription run into a metered one. API billing is opt-in, per run (``--auth api-key``) or per
config (``auth.mode``).

Two credential *classes* exist, because they have different cost profiles and the user may want
different vendors behind them:

* **orchestrator** — preflight, backbone, merge, reconcile, synthesis, verification, assembly.
  Governed by ``auth.orchestrator`` in ``~/.config/vantage/default.json``.
* **research** — the section-wise deep-research agents (Wave A, Wave B, vertical annex).
  Governed by ``auth.research``; may point at a different provider and a different key entirely.

Keys are never written to the config file and never logged. A prompted key lives in this
process's environment only.
"""

from __future__ import annotations

import os
import sys

from .models.config import AuthProfileCfg, Config

#: Backends that run on the Claude subscription. ``workflow`` shells out to the Claude Code CLI;
#: ``agent-sdk`` inherits Claude Code's own credentials when no key is present.
SUBSCRIPTION_BACKENDS = frozenset({"workflow", "agent-sdk"})

#: Fallback key env per provider, used when neither the profile nor ``providers.*`` names one.
_DEFAULT_KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GOOGLE_API_KEY",
}


class AuthError(RuntimeError):
    """A credential the run needs could not be resolved."""


def key_env(cfg: Config, provider: str, profile: AuthProfileCfg | None = None) -> str:
    """Name of the environment variable holding ``provider``'s key for this profile."""
    if profile is not None and profile.api_key_env:
        return profile.api_key_env
    pc = cfg.providers.get(provider)
    if pc and pc.api_key_env:
        return pc.api_key_env
    if provider == "anthropic" and cfg.auth.api_key_env:
        return cfg.auth.api_key_env
    return _DEFAULT_KEY_ENV.get(provider, f"{provider.upper()}_API_KEY")


def model_env(cfg: Config, provider: str, profile: AuthProfileCfg | None = None) -> str | None:
    """Name of the env var that pins this profile's model, or ``None`` if none applies.

    A profile's own ``model_env`` applies to whatever provider it routes to. The global default
    (``ANTHROPIC_MODEL``) applies only to anthropic-routed agents — pointing an OpenAI agent at
    ``ANTHROPIC_MODEL`` would hand it a model name its API rejects.
    """
    if profile is not None and profile.model_env:
        return profile.model_env
    if provider == "anthropic" and cfg.auth.model_env:
        return cfg.auth.model_env
    return None


def resolve_model(cfg: Config, provider: str, profile: AuthProfileCfg, fallback: str) -> str:
    """Model for one agent: env pin → profile pin → the role's tier model."""
    env = model_env(cfg, provider, profile)
    if env and os.environ.get(env):
        return os.environ[env].strip()
    return profile.model or fallback


def resolve_key(
    cfg: Config, provider: str, profile: AuthProfileCfg | None = None, *, allow_prompt: bool = False
) -> str:
    """Return the API key for ``provider``.

    ``allow_prompt`` is reserved for :func:`prompt_missing`, which runs once before the fan-out
    starts. Agents must never prompt: ten Wave A agents racing for one stdin would interleave
    their prompts and read each other's input.

    A prompted key is exported into this process's environment so the provider SDKs — which read
    it themselves — find it. It is never written to the config file and never logged.
    """
    env = key_env(cfg, provider, profile)
    existing = os.environ.get(env)
    if existing:
        return existing

    if not (allow_prompt and cfg.auth.prompt_for_key):
        raise AuthError(
            f"{env} is not set. Export it, or re-run with --ask-key to be prompted, "
            f"or drop --auth api-key to run on your Claude subscription."
        )
    if not (sys.stdin.isatty() and sys.stderr.isatty()):
        raise AuthError(f"{env} is not set and there is no terminal to prompt on.")

    import getpass

    key = getpass.getpass(f"{provider} API key ({env}, not stored): ").strip()
    if not key:
        raise AuthError(f"no {env} provided")
    os.environ[env] = key  # process-local only; never written to disk or logged
    return key


def prompt_missing(cfg: Config) -> list[str]:
    """Resolve every routed credential once, before any agent starts.

    Returns the providers whose key was entered interactively. No-op in subscription mode, and a
    no-op without ``--ask-key`` — a missing key then surfaces as a readiness issue instead.
    """
    if cfg.auth.subscription or not cfg.auth.prompt_for_key:
        return []
    entered: list[str] = []
    for provider, env in sorted(routed_providers(cfg).items()):
        if os.environ.get(env):
            continue
        resolve_key(cfg, provider, allow_prompt=True)
        entered.append(provider)
    return entered


def routed_providers(cfg: Config) -> dict[str, str]:
    """Every provider this config can route an agent to → the key env var it would use.

    Walks the actual role map rather than ``providers.*``, so a provider that is configured but
    never routed to does not produce a spurious "key missing" warning.
    """
    from .blueprint.stages import AGENTS

    out: dict[str, str] = {}
    for role in AGENTS:
        profile = cfg.auth.profile_for(role)
        provider = profile.provider or cfg.model_for_role(role).provider
        out.setdefault(provider, key_env(cfg, provider, profile))
    return out


def readiness(cfg: Config, backend: str) -> list[str]:
    """Human-readable auth problems for ``backend`` under the current mode (empty = ready)."""
    if cfg.auth.subscription:
        if backend in SUBSCRIPTION_BACKENDS:
            return []
        return [
            f"backend '{backend}' talks to provider APIs directly and cannot use the Claude "
            f"subscription — re-run with --auth api-key (billed per token), or use "
            f"--backend workflow"
        ]

    issues: list[str] = []
    for provider, env in sorted(routed_providers(cfg).items()):
        configured = cfg.providers.get(provider)
        if configured is not None and not configured.enabled:
            issues.append(f"routed provider '{provider}' is disabled (providers.{provider}.enabled)")
        if os.environ.get(env):
            continue
        if cfg.auth.prompt_for_key:
            issues.append(f"{env} not set (routed provider '{provider}') — will prompt at run time")
        else:
            issues.append(f"{env} not set (routed provider '{provider}')")
    return issues


def model_pin_warning(cfg: Config) -> str | None:
    """Warn when a model env var flattens the synthesis/research/cheap tiers onto one model."""
    if cfg.auth.subscription:
        return None
    env = cfg.auth.model_env
    pinned = os.environ.get(env) if env else None
    if not pinned:
        return None
    return (
        f"{env}={pinned} pins every anthropic-routed agent to one model — the "
        f"synthesis/research/cheap tiers in role_model_map are ignored for this run."
    )
