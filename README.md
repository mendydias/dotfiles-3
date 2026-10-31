# Dotfiles

Chezmoi source for selected desktop configuration and global agent skills. The live home directory is not a Git repository.

This machine’s source lives at `~/.local/share/chezmoi` on `main`, with `origin` configured. Commit and push only when explicitly requested.

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
| `chezmoi add <file>` | Import one reviewed live file into the source repo |
| `chezmoi diff` | Show pending changes |
| `chezmoi apply` | Write source state to `$HOME` |
| `fisher update` | Install or update pinned Fisher plugins |

## What is tracked

Fish configuration, Ghostty, reviewed Hyprland Lua, Micro settings, environment snippets, user units, 1Password autostart, Neovim extras and lockfile, Herdr preferences, Git configuration, and reviewed DMS preferences.

DMS preferences live at `~/.config/dms/settings.json`; `~/.config/DankMaterialShell` is a relative symlink to `dms`. Home-directory paths in DMS, Hyprland, and the planning skill are rendered from chezmoi templates.

Orca imports are limited to `~/.orca/keybindings.json` and the keybind guide generator and tests in `~/.config/orca`. Generate the untracked HTML guide with:

```sh
python3 ~/.config/orca/keybind_sheet.py
```

Global skills include instructions, licenses, references, scripts, and UI assets under `~/.agents/skills` and `~/.codex/skills/.system`. The shared skills' provenance is recorded in `~/.agents/skills/SOURCES.md`. There was no `~/.skills` directory at import time.

## What is not tracked

Secrets, browser profiles, password-manager data, Fish `fish_variables`, Fisher plugin payloads, SDKMAN runtimes, nested Git checkouts, and machine-specific state. Orca credentials, Electron profiles, databases, sessions, generated HTML, and the Codex system-skill installation marker remain untracked. Reviewed existing DMS-generated Hyprland files and Ghostty colors are intentional snapshots; downloaded DMS plugins and themes are not included.

See `AGENTS.md` for the import, exclusion, and validation rules.

## Hyprland shortcut descriptions

Keep custom Hyprland shortcuts in `dot_config/hypr/user.lua.tmpl`; put overrides of
DMS-owned shortcuts in `dot_config/hypr/dms/binds-user.lua`. Do not edit
`dms/binds.lua`, which DMS can regenerate.

Give every shortcut a purpose-focused description in the `hl.bind` options,
for example:

```lua
hl.bind("SUPER + ALT + S", toggle_spotify, { description = "Toggle Spotify scratchpad" })
```

Keep each `hl.bind` registration on one line and write its key combination as a
literal. DMS statically discovers bindings for its keybind display; registrations
generated inside loops or assembled from key variables may not appear. Callback
logic can live in helpers, but register each key separately. Describe what the
shortcut does, not the command or internal dispatcher it runs.

Check the parsed result with:

```sh
dms keybinds show hyprland
```

## Importing a live-system snapshot

When explicitly requested, treat reviewed live files as the source for that import. Add individual files rather than recursively importing application directories. Review `git diff`, `chezmoi diff`, and `chezmoi apply --dry-run --verbose` before committing coherent groups.

Chezmoi normalizes permissions: the live DMS settings file has mode `0654`, which imports with the executable attribute, and the live `~/.local` directory has mode `0750` rather than chezmoi's `0755`. A full apply would change those modes. Importing a snapshot does not require applying it back to the live system.
