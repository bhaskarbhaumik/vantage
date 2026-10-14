"""Configuration models — the typed shape of config/default.json."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DEFAULT_BACKENDS = ["workflow", "api", "agent-sdk", "langgraph", "adk", "crewai"]

#: How the run pays for tokens. ``subscription`` = the user's Claude plan via the Claude Code CLI,
#: no API key read or required; ``api-key`` = direct provider APIs, billed per token. Opt-in only.
AUTH_MODES = ("subscription", "api-key")


class SectionCfg(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ModelRef(SectionCfg):
    provider: Literal["anthropic", "openai", "gemini"] = "anthropic"
    model: str = Field(min_length=1)
    max_tokens: int | None = Field(default=None, ge=1024)
    temperature: float | None = Field(default=None, ge=0, le=2)
    effort: Literal["low", "medium", "high", "xhigh", "max"] | None = None


class ThinkingCfg(SectionCfg):
    enabled: bool = True
    mode: Literal["auto", "adaptive", "enabled"] = "auto"
    budget_tokens: int = Field(default=8000, ge=1024)
    effort: Literal["low", "medium", "high", "xhigh", "max"] = "medium"


class ModelsCfg(SectionCfg):
    synthesis: ModelRef = ModelRef(model="claude-opus-5-5", effort="high")
    research: ModelRef = ModelRef(model="claude-sonnet-5-5", effort="high")
    cheap: ModelRef = ModelRef(model="claude-haiku-4-5-20251001")
    temperature: float = Field(default=1.0, ge=0, le=2)
    max_tokens: int = Field(default=16000, ge=1024)
    thinking: ThinkingCfg = Field(default_factory=ThinkingCfg)


class AuthProfileCfg(SectionCfg):
    """Credential + model overrides for one class of agent. Unset fields inherit."""

    #: anthropic | openai | gemini. Unset -> whatever the role's model tier names.
    provider: Literal["anthropic", "openai", "gemini"] | None = None
    #: Env var holding this profile's key. Unset -> providers.<provider>.api_key_env.
    api_key_env: str | None = None
    #: Pin every agent in this class to one model. Unset -> the role's model tier.
    model: str | None = None
    #: Env var that overrides ``model`` at run time (highest precedence).
    model_env: str | None = None


class AuthCfg(SectionCfg):
    """Subscription-first credential policy. See ``vantage.auth`` for the resolution rules."""

    mode: Literal["subscription", "api-key"] = "subscription"
    #: Consulted in api-key mode only. Never holds a key — only the name of the variable that does.
    api_key_env: str = "ANTHROPIC_API_KEY"
    model_env: str = "ANTHROPIC_MODEL"
    #: Prompt on the terminal for a missing key. Opt-in (--ask-key) so an unattended run fails
    #: fast instead of blocking on stdin nobody is watching.
    prompt_for_key: bool = False
    #: Preflight, backbone, merge, reconcile, synthesis, verification, assembly.
    orchestrator: AuthProfileCfg = Field(default_factory=AuthProfileCfg)
    #: The section-wise deep-research agents (Wave A, Wave B, vertical annex).
    research: AuthProfileCfg = Field(default_factory=AuthProfileCfg)

    @property
    def subscription(self) -> bool:
        return self.mode == "subscription"

    def profile_for(self, role: str) -> AuthProfileCfg:
        from ..blueprint.stages import SECTION_RESEARCH_AGENTS

        return self.research if role in SECTION_RESEARCH_AGENTS else self.orchestrator


class EngineCfg(SectionCfg):
    backend: Literal["workflow", "api", "agent-sdk", "langgraph", "adk", "crewai"] = "workflow"
    available_backends: list[str] = Field(default_factory=lambda: list(DEFAULT_BACKENDS))
    #: Output tier per blueprint §4: EXECUTIVE | STANDARD | FULL_ANNEX.
    tier: Literal["EXECUTIVE", "STANDARD", "FULL_ANNEX"] = "FULL_ANNEX"
    #: Wave A launches ten concurrent research agents; anything lower serialises them.
    max_concurrency: int = Field(default=10, ge=1, le=32)
    output_dir: str = Field(default="~/.cache/vantage/run", min_length=1)
    harness_dir: str | None = None
    max_iterations: int = Field(default=24, ge=1, le=200,
                                description="Maximum direct-API turns per agent.")
    tool_result_max_chars: int = Field(default=24000, ge=256)
    tool_timeout_seconds: float = Field(default=120, gt=0)


class ProviderCfg(SectionCfg):
    enabled: bool = False
    api_key_env: str = ""
    default_model: str | None = None
    timeout_seconds: float = Field(default=120, gt=0)
    max_attempts: int = Field(default=5, ge=1, le=10)
    max_concurrency: int | None = Field(default=None, ge=1, le=32,
                                       description="null inherits engine.max_concurrency.")
    retry_min_seconds: float = Field(default=2, ge=0)
    retry_max_seconds: float = Field(default=30, ge=0)

    @model_validator(mode="after")
    def retry_bounds(self) -> ProviderCfg:
        if self.retry_max_seconds < self.retry_min_seconds:
            raise ValueError("retry_max_seconds must be >= retry_min_seconds")
        return self


class WebSearchCfg(SectionCfg):
    enabled: bool = True
    provider: Literal["tavily", "brave"] = "tavily"
    api_key_env: str = "TAVILY_API_KEY"
    max_results: int = Field(default=6, ge=1, le=20)
    search_depth: Literal["basic", "advanced"] = "advanced"
    timeout_seconds: float = Field(default=20, gt=0)
    snippet_max_chars: int = Field(default=500, ge=100)


class EdgarCfg(SectionCfg):
    enabled: bool = True
    identity_env: str = "SEC_EDGAR_IDENTITY"
    filings_limit: int = Field(default=8, ge=1, le=100)
    statement_max_chars: int = Field(default=2500, ge=100)


class MarketDataCfg(SectionCfg):
    enabled: bool = True


class ToolsCfg(SectionCfg):
    web_search: WebSearchCfg = Field(default_factory=WebSearchCfg)
    edgar: EdgarCfg = Field(default_factory=EdgarCfg)
    market_data: MarketDataCfg = Field(default_factory=MarketDataCfg)


class CloudCfg(BaseModel):
    model_config = ConfigDict(extra="allow")
    target: Literal["gcp", "azure", "aws"] = "gcp"
    image: str = "vantage"
    gcp: dict = Field(default_factory=dict)
    azure: dict = Field(default_factory=dict)
    aws: dict = Field(default_factory=dict)


class RunDefaultsCfg(SectionCfg):
    primary_geography: str = "AUTO-DETECT"
    target_vertical: str = "AUTO-DETECT"
    ticker_or_private: str = "AUTO-DETECT"
    capability_pack: Literal["ATTACHED", "NOT_ATTACHED"] = "NOT_ATTACHED"
    account_team_input_sheet: Literal["ATTACHED", "NOT_ATTACHED"] = "NOT_ATTACHED"
    account_context: str = "NONE"
    known_relationship_context: str = "NONE"
    strategic_pursuit_objectives: str = "NONE"


class OutputCfg(SectionCfg):
    """Supported output contract; other formats and state deletion are not implemented."""

    formats: list[Literal["md"]] = Field(default_factory=lambda: ["md"], min_length=1, max_length=1)
    keep_state: Literal[True] = True


ExportFormat = Literal["pptx", "docx", "pdf", "html"]


class ExportHelpersCfg(SectionCfg):
    """External helper CLIs ``vantage export`` calls when they are on PATH.

    Every helper is optional: a missing binary or key degrades to the built-in fallback and is
    reported by ``vantage doctor``, never a failed export.
    """

    #: ``get-icon`` — icons for slide headers, KPI tiles and section dividers.
    icons: bool = True
    #: ``get-brand`` — logo, palette and typography for ``export.brand`` and the client cover logo.
    brand: bool = True
    #: ``get-stock`` — semantically matched splash images for covers and section openers.
    stock_images: bool = True
    #: Diagram renderer for figure-spec blocks. ``auto`` picks dgm, then drawio, then Mermaid.
    diagrams: Literal["auto", "dgm", "drawio", "mermaid", "none"] = "auto"
    #: ``napkin`` concept illustrations. Spends Napkin credits, so it is opt-in.
    illustrations: Literal["none", "napkin"] = "none"
    #: Chart renderer for chart-spec blocks.
    charts: Literal["matplotlib", "plotly"] = "matplotlib"
    #: LibreOffice binary used to convert the whitepaper to PDF.
    libreoffice_bin: str = "soffice"
    #: Seconds before any one helper call is abandoned.
    timeout_seconds: float = Field(default=60, gt=0)


class ExportCfg(SectionCfg):
    """Defaults for ``vantage export`` — turning a finished dossier into collateral."""

    formats: list[ExportFormat] = Field(
        default_factory=lambda: ["pptx", "docx", "pdf", "html"], min_length=1)
    #: exec ≈ 18 slides / ~40 pp · standard ≈ 31 slides / ~125 pp · full = every section + appendix.
    depth: Literal["exec", "standard", "full"] = "standard"
    #: Shape of the self-contained HTML output.
    site_mode: Literal["microsite", "deck"] = "microsite"
    #: ``deterministic`` maps the dossier to plans directly; ``agents`` lets Claude author them.
    authoring: Literal["deterministic", "agents"] = "deterministic"
    #: Output directory. null = ``<run dir>/exports``.
    out_dir: str | None = None
    #: Marking printed on every page, slide and screen.
    classification: str = Field(default="Confidential", min_length=1)
    #: Domain of the organization whose brand themes the collateral (via get-brand).
    #: null = the neutral Vantage theme.
    brand: str | None = None
    #: Put the client's own logo on the cover (via get-brand).
    client_logo: bool = True
    helpers: ExportHelpersCfg = Field(default_factory=ExportHelpersCfg)


class UiCfg(SectionCfg):
    """Terminal presentation for the CLI and the Ink TUI."""

    #: ``nerd`` assumes a Nerd Font; ``unicode`` uses plain symbols; ``ascii`` is 7-bit only.
    icons: Literal["nerd", "unicode", "ascii"] = "nerd"
    #: ``auto`` honours NO_COLOR and whether stdout is a TTY.
    color: Literal["auto", "always", "never"] = "auto"
    theme: Literal["dark", "light"] = "dark"
    #: Spinners and live redraws. Off for screen readers and CI logs.
    animations: bool = True


class Config(BaseModel):
    """Top-level engine configuration. Tolerant of unknown keys ($schema, _note, …)."""

    model_config = ConfigDict(extra="ignore")

    version: str = "2.2"
    engine: EngineCfg = Field(default_factory=EngineCfg)
    auth: AuthCfg = Field(default_factory=AuthCfg)
    models: ModelsCfg = Field(default_factory=ModelsCfg)
    role_model_map: dict[str, Literal["synthesis", "research", "cheap"]] = Field(default_factory=dict)
    providers: dict[str, ProviderCfg] = Field(default_factory=dict)
    tools: ToolsCfg = Field(default_factory=ToolsCfg)
    cloud: CloudCfg = Field(default_factory=CloudCfg)
    run_defaults: RunDefaultsCfg = Field(default_factory=RunDefaultsCfg)
    output: OutputCfg = Field(default_factory=OutputCfg)
    export: ExportCfg = Field(default_factory=ExportCfg)
    ui: UiCfg = Field(default_factory=UiCfg)

    def model_for_role(self, role: str) -> ModelRef:
        """Resolve an agent label to its model tier, defaulting to `research`."""
        tier = self.role_model_map.get(role, "research")
        return getattr(self.models, tier, self.models.research)
