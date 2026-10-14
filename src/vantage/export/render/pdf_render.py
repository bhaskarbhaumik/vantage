"""DOCX → PDF via headless LibreOffice.

LibreOffice honours the template's sections, headers/footers and ``Page N`` fields. A private
user profile per conversion keeps a running LibreOffice from hijacking the request and lets
concurrent conversions coexist.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


class PdfConversionError(RuntimeError):
    pass


MAC_APP = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")


def soffice_binary(configured: str = "soffice") -> str | None:
    """Resolve ``export.helpers.libreoffice_bin`` (a name on PATH or an absolute path)."""
    candidates = [configured, "soffice", "libreoffice"]
    for candidate in candidates:
        if not candidate:
            continue
        path = Path(candidate).expanduser()
        if path.is_absolute() and path.exists():
            return str(path)
        found = shutil.which(candidate)
        if found:
            return found
    return str(MAC_APP) if MAC_APP.exists() else None


def docx_to_pdf(docx_path: Path, out_path: Path | None = None, *, binary: str | None = None,
                timeout: float = 600) -> Path:
    """Convert ``docx_path`` to PDF. Returns the written path."""
    binary = binary or soffice_binary()
    if not binary:
        raise PdfConversionError(
            "LibreOffice not found — install it (macOS: `brew install --cask libreoffice`) or "
            "set export.helpers.libreoffice_bin; the .docx was still produced.")
    docx_path = Path(docx_path)
    out_path = Path(out_path) if out_path else docx_path.with_suffix(".pdf")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vantage-export-lo-") as profile:
        try:
            result = subprocess.run(
                [binary, "--headless", "--norestore", "--invisible",
                 f"-env:UserInstallation=file://{profile}",
                 "--convert-to", "pdf:writer_pdf_Export", "--outdir", str(out_path.parent),
                 str(docx_path)],
                capture_output=True, check=False, text=True, timeout=timeout,
                env={**os.environ, "HOME": profile},
            )
        except subprocess.TimeoutExpired as exc:
            raise PdfConversionError(f"LibreOffice timed out after {timeout:.0f}s") from exc
        except OSError as exc:
            raise PdfConversionError(f"LibreOffice could not start: {exc}") from exc
    produced = out_path.parent / f"{docx_path.stem}.pdf"
    if not produced.exists():
        raise PdfConversionError(
            f"LibreOffice produced no PDF for {docx_path.name}.\n"
            f"stdout: {result.stdout.strip()[:400]}\nstderr: {result.stderr.strip()[:400]}")
    if produced != out_path:
        produced.replace(out_path)
    return out_path


def page_count(pdf_path: Path) -> int | None:
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(pdf_path)).pages)
    except Exception:
        return None
