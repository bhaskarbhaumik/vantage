"""``vantage export`` — turn a finished ``<slug>-vantage.md`` dossier into collateral.

Four outputs from one dossier: a PowerPoint deck (.pptx), a Word whitepaper (.docx), a PDF of it
(via LibreOffice) and a fully self-contained single-file HTML microsite or HTML deck. Every page,
slide and screen carries the configured classification marking.

The public surface is :mod:`vantage.export.api`; this package imports nothing heavy at import
time, so ``vantage --help`` stays fast and the export extra stays optional.
"""

from __future__ import annotations

__all__ = ["ExportOptions", "ExportResult", "Check", "doctor", "export", "find_dossier",
           "options_from_config"]


def __getattr__(name: str):
    if name in __all__:
        from . import api

        return getattr(api, name)
    raise AttributeError(name)
