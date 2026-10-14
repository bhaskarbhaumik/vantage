# Shell completion

`vantage` (and its alias `vantage-engine`) complete in bash, zsh and fish: commands, options, every
hidden [config flag](cli.md#config-flags), choice values, and run slugs from your output
directory.

The scripts are thin shims: the shell calls the program back with
`_VANTAGE_COMPLETE=complete_<shell>` (`_VANTAGE_ENGINE_COMPLETE=…` for the alias) and the command
tree answers. Completion therefore always matches the installed version, and slugs come from the
configured `engine.output_dir`.

## Install

Let the CLI write the file and tell you where it went:

```bash
uv run vantage completion zsh --install      # ~/.zfunc/_vantage
uv run vantage completion bash --install     # ~/.local/share/bash-completion/completions/vantage
uv run vantage completion fish --install     # ~/.config/fish/completions/vantage.fish
uv run vantage completion zsh --install --prog-name vantage-engine
```

`--install` never edits your shell startup files. For zsh it tells you when `~/.zfunc` is not on
`fpath` yet; add this to `~/.zshrc` before `compinit`:

```zsh
fpath+=~/.zfunc; autoload -Uz compinit; compinit
```

bash needs bash-completion 2.x to load the directory automatically; without it, `source` the file
from `~/.bashrc`. Open a new shell afterwards.

Completion calls the `vantage` on your `PATH`, so activate the project environment
(`source .venv/bin/activate`) or otherwise put `vantage` on `PATH` first
([Getting started](getting-started.md#put-the-commands-on-your-path-optional)).

## Current session only

```bash
source <(vantage completion bash)
source <(vantage completion zsh)
vantage completion fish | source
```

## Packagers

Static copies live in [completions/](../completions/README.md): `vantage.bash`, `_vantage`,
`vantage.fish` and the same three for `vantage-engine`. They are generated, and
`tests/test_cli.py` fails if they drift from `vantage completion <shell>`. Regenerate with:

```bash
for p in vantage vantage-engine; do
  uv run vantage completion bash --prog-name $p > completions/$p.bash
  uv run vantage completion zsh  --prog-name $p > completions/_$p
  uv run vantage completion fish --prog-name $p > completions/$p.fish
done
```

The TUI (`vantage-tui`) has no completion script; `vantage-tui --help` lists its screens and
flags.
