"""Regenerate the editor/validation schema: uv run python scripts/generate-config-schema.py."""

import json
from pathlib import Path

from vantage.models.config import Config


def config_schema() -> dict:
    schema = Config.model_json_schema()
    schema.update({
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://raw.githubusercontent.com/bhaskarbhaumik/vantage/main/config/default.schema.json",
        "title": "Vantage configuration",
        "description": "Defaults < user config < VANTAGE_* environment < CLI overrides. "
                       "See docs/configuration.md for model sources and backend applicability.",
    })
    schema["properties"]["$schema"] = {"type": "string"}
    schema["properties"]["_note"] = {"type": "string"}
    return schema


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "config/default.schema.json"
    target.write_text(json.dumps(config_schema(), indent=2) + "\n")
