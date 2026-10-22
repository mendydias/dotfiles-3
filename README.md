# Dotfiles

Chezmoi source for selected files from `~/.config`. The live home directory is not a Git repository.

## Requirements

- [chezmoi](https://www.chezmoi.io/)
- Fish, Fisher, zoxide, Neovim, fzf, fd, and bat
- GitHub CLI (`gh`) for the private upstream repository
- SDKMAN, installed separately under `~/.sdkman`

## First-time setup

```fish
chezmoi init git@github.com:<user>/dotfiles.git
chezmoi apply
fisher update
```

SDKMAN is not stored here. Install it with the official Bash installer (`rcupdate=false` so it does not edit Bash/Zsh rc files), then use `sdk` from Fish through the Fisher plugin.

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
