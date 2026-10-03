"""LLM providers and routing.

The conversation is represented in Anthropic content-block form (``text`` / ``tool_use`` /
``tool_result``); the OpenAI and Gemini providers translate to and from that shape, so the
agent executor stays provider-agnostic.
"""

from .base import AssistantTurn, LLMProvider, ProviderError, ToolCall, ToolSpec  # noqa: F401
from .router import ProviderRouter  # noqa: F401
