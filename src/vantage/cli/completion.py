"""Shell completion for ``vantage`` and ``vantage-engine`` (bash, zsh, fish).

The scripts are Click/Typer's callback style: the shell re-invokes the program with
``_VANTAGE_COMPLETE=complete_<shell>`` and the command tree answers, so subcommands, every
generated config flag, choice values and run slugs (from the output dir) all complete. The
same scripts are committed under ``completions/`` for packagers.
"""

from __future__ import annotations

import os
from pathlib import Path

SHELLS = ("bash", "zsh", "fish")
PROGS = ("vantage", "vantage-engine")


def _init() -> None:
    try:
        from typer._completion_classes import completion_init
    except ImportError:  # pragma: no cover
        from typer.completion import completion_init  # type: ignore[no-redef]
    completion_init()


_init()


def complete_var(prog: str) -> str:
    return "_{}_COMPLETE".format(prog.replace("-", "_").upper())


def script(shell: str, prog: str = "vantage") -> str:
    """The completion script for ``shell`` (trailing newline included)."""
    from typer._completion_shared import get_completion_script

    if shell not in SHELLS:
        raise ValueError(f"unsupported shell {shell!r}; choose {', '.join(SHELLS)}")
    return get_completion_script(prog_name=prog, complete_var=complete_var(prog),
                                 shell=shell).rstrip() + "\n"


def committed_name(shell: str, prog: str) -> str:
    """File name used for the committed static scripts under ``completions/``."""
    return {"bash": f"{prog}.bash", "zsh": f"_{prog}", "fish": f"{prog}.fish"}[shell]


def install_path(shell: str, prog: str, home: Path | None = None) -> Path:
    """Where a user-level install goes. bash/fish locations are auto-loaded; zsh uses ~/.zfunc."""
    home = home or Path.home()
    if shell == "bash":
        data = Path(os.environ.get("XDG_DATA_HOME") or home / ".local" / "share")
        return data / "bash-completion" / "completions" / prog
    if shell == "zsh":
        return home / ".zfunc" / f"_{prog}"
    if shell == "fish":
        conf = Path(os.environ.get("XDG_CONFIG_HOME") or home / ".config")
        return conf / "fish" / "completions" / f"{prog}.fish"
    raise ValueError(shell)


def install(shell: str, prog: str = "vantage", home: Path | None = None) -> tuple[Path, list[str]]:
    """Write the script; return ``(path, follow-up notes)``. Never edits shell rc files."""
    home = home or Path.home()
    path = install_path(shell, prog, home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script(shell, prog))
    notes: list[str] = []
    if shell == "zsh":
        zshrc = Path(os.environ.get("ZDOTDIR") or home) / ".zshrc"
        try:
            rc = zshrc.read_text()
        except OSError:
            rc = ""
        if ".zfunc" not in rc:
            notes.append(f"add to {zshrc} (before compinit):  "
                         "fpath+=~/.zfunc; autoload -Uz compinit; compinit")
    elif shell == "bash":
        notes.append("loaded automatically by bash-completion 2.x; without it add "
                     f"`source {path}` to ~/.bashrc")
    notes.append("open a new shell to pick it up")
    return path, notes
