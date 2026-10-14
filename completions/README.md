# Shell completion

Completion scripts for `vantage` and its alias `vantage-engine`. They are thin shims: the shell
calls the program back (`_VANTAGE_COMPLETE=complete_<shell>`), so commands, every generated
config flag (`vantage options`), choice values and run slugs from your output dir all complete.

| Shell | `vantage` | `vantage-engine` |
|---|---|---|
| bash | `vantage.bash` | `vantage-engine.bash` |
| zsh | `_vantage` | `_vantage-engine` |
| fish | `vantage.fish` | `vantage-engine.fish` |

## Install

The quickest route lets the CLI write the file and tell you where it went:

```sh
vantage completion zsh --install      # ~/.zfunc/_vantage
vantage completion bash --install     # ~/.local/share/bash-completion/completions/vantage
vantage completion fish --install     # ~/.config/fish/completions/vantage.fish
vantage completion zsh --install --prog-name vantage-engine
```

Or copy the committed files by hand:

```sh
# bash (bash-completion 2.x loads this directory automatically)
mkdir -p ~/.local/share/bash-completion/completions
cp completions/vantage.bash ~/.local/share/bash-completion/completions/vantage

# zsh: put the file on $fpath before compinit runs
mkdir -p ~/.zfunc && cp completions/_vantage ~/.zfunc/
echo 'fpath+=~/.zfunc; autoload -Uz compinit; compinit' >> ~/.zshrc

# fish
cp completions/vantage.fish ~/.config/fish/completions/
```

Or load it for the current session only:

```sh
source <(vantage completion bash)
source <(vantage completion zsh)
vantage completion fish | source
```

The committed files are generated; `tests/test_cli.py` fails if they drift from
`vantage completion <shell>`. To regenerate:

```sh
for p in vantage vantage-engine; do
  uv run vantage completion bash --prog-name $p > completions/$p.bash
  uv run vantage completion zsh  --prog-name $p > completions/_$p
  uv run vantage completion fish --prog-name $p > completions/$p.fish
done
```
