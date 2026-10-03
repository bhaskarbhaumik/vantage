"""Pluggable execution backends. Default is ``workflow`` (Claude Code, subscription).

- ``workflow``  — wraps the Claude Code Workflow harness (no API key). **Default.**
- ``api``       — direct multi-provider API fan-out. The full headless engine.
- ``agent-sdk`` — Claude Agent SDK per-agent runner over the shared DAG.
- ``langgraph`` — a LangGraph StateGraph driving the shared stage pipeline.
- ``adk``       — Google ADK sequential-agent integration.
- ``crewai``    — CrewAI integration.
"""

from .base import Backend  # noqa: F401
from .registry import BACKENDS, get_backend  # noqa: F401
