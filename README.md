# Dotfiles

Chezmoi source for selected files from `~/.config`. The live home directory is not a Git repository.

This machine’s source already lives at `~/.local/share/chezmoi` on `main`. There is no Git remote yet. A private GitHub repository can be attached later; do not add `origin` or push until that is asked for.

## Requirements

- [chezmoi](https://www.chezmoi.io/)
- Fish, Fisher, zoxide, Neovim, fzf, fd, and bat
- SDKMAN, installed separately under `~/.sdkman`

## Local workflow

```fish
chezmoi diff
chezmoi apply
fisher update
```

SDKMAN is not stored here. It was installed with the official Bash installer (`rcupdate=false` so it does not edit Bash/Zsh rc files). Use `sdk` from Fish through the Fisher plugin.

Do not install Java or build tools until you choose the versions you want.

## Everyday commands

| Command | Purpose |
| --- | --- |
| `chezmoi edit <file>` | Edit a managed file in the source repo |
| `chezmoi diff` | Show pending changes |
| `chezmoi apply` | Write source state to `$HOME` |
| `fisher update` | Install or update pinned Fisher plugins |

## What is tracked

Fish configuration, Ghostty, reviewed Hyprland Lua, Micro settings, environment snippets, the Hyprland session target, 1Password autostart, and reviewed DankMaterialShell preferences.

## What is not tracked

Secrets, browser profiles, password-manager data, Fish `fish_variables`, Fisher plugin payloads, SDKMAN runtimes, generated themes, nested Git checkouts, and machine-specific state.

See `AGENTS.md` for the import, exclusion, and validation rules.

## Later: attach a private remote

After a private GitHub repository exists, add it explicitly. Do not do this as a side effect of editing or applying:

```fish
git -C ~/.local/share/chezmoi remote add origin git@github.com:<user>/dotfiles.git
git -C ~/.local/share/chezmoi push -u origin main
```
