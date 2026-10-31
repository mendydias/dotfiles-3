# Agent notes for this chezmoi repository

This repository is the chezmoi **source state**. It lives at `~/.local/share/chezmoi` and is the only Git root for these dotfiles. Never initialize Git in the live `~/.config` directory.

## Repository structure

| Path | Destination | Notes |
| --- | --- | --- |
| `AGENTS.md`, `README.md` | not deployed | Repository documentation only |
| `.chezmoiignore` | not deployed | Blocks docs and accidental payloads from `chezmoi apply` |
| `.gitignore` | not deployed | Extra guard against secrets and plugin files |
| `dot_config/chezmoi/chezmoi.toml` | `~/.config/chezmoi/chezmoi.toml` | Auto-commit and auto-push stay off |
| `dot_config/fish/` | `~/.config/fish/` | Human-maintained Fish files only |
| `dot_config/ghostty/` | `~/.config/ghostty/` | Terminal config and the reviewed Dank theme |
| `dot_config/hypr/` | `~/.config/hypr/` | Reviewed Hyprland Lua, not generated color/layout files |
| `dot_config/micro/settings.json` | `~/.config/micro/settings.json` | Editor settings only |
| `dot_config/environment.d/` | `~/.config/environment.d/` | User environment snippets |
| `dot_config/systemd/user/` | `~/.config/systemd/user/` | Selected user units |
| `dot_config/autostart/` | `~/.config/autostart/` | Selected autostart entries |
| `dot_config/dms/executable_settings.json.tmpl` | `~/.config/dms/settings.json` | Reviewed live preferences; template home paths |
| `dot_config/symlink_DankMaterialShell` | `~/.config/DankMaterialShell` | Relative symlink to `dms` |
| `dot_config/private_orca/` | `~/.config/orca/` | Keybind guide generator and tests only |
| `private_dot_orca/keybindings.json` | `~/.orca/keybindings.json` | Personal shortcut overrides only |
| `dot_agents/skills/` | `~/.agents/skills/` | Global skills and their reviewed resources |
| `dot_codex/skills/` | `~/.codex/skills/` | Global Codex skills, not account or runtime state |

Chezmoi maps the `dot_` prefix to a leading `.`. Edit files in this repository, then apply them. Do not treat the live home directory as the source of truth.

## Editing workflow

1. Edit the source file under `~/.local/share/chezmoi` (`chezmoi edit <target>` is fine).
2. Inspect the result with `chezmoi diff` and `chezmoi status`.
3. Apply with `chezmoi apply` or `chezmoi apply --dry-run --verbose` first.
4. Commit only when the user asks. Never `git commit` or `git push` as a side effect of editing or applying.

`chezmoi.toml` disables chezmoi’s own auto-commit and auto-push. Do not re-enable them.

## Explicit imports

Track new files with an **allowlist**. Add one reviewed path at a time:

```fish
chezmoi add ~/.config/ghostty/config
```

Do not run `chezmoi add ~`, `chezmoi add ~/.config`, or any recursive add of a directory that contains secrets, caches, plugins, or nested Git repositories.

After adding a file, read the copy in this repository before committing. If it contains machine-specific paths, generated theme data, or mixed settings/state, either drop it or rewrite it into a readable, intentional form.

## Exclusions

Never import or commit:

- Nested Git repository roots, including DankMaterialShell plugin checkouts
- Downloaded plugins, dependencies, syntax bundles, binaries, caches, logs, histories, databases, and backups
- Browser profiles, password-manager data, authentication files, and credentials
- Fish `fish_variables` (put intentional settings in readable Fish files instead)
- Fisher-generated functions, completions, and snippets under `~/.config/fish` or `~/.local/share/fisher`
- SDKMAN downloads and installed runtimes under `~/.sdkman`
- Generated theme files and mixed settings/state files unless they were reviewed and explicitly wanted
- Machine-specific or sensitive local overrides
- This repository’s documentation files into the home directory

A private GitHub repository is not a safe place for plaintext secrets.

For an explicitly requested live-system import, review and add individual live
files instead of applying stale source files over them. Preserve the DMS symlink
layout. Never recursively add Orca's Electron profile or either agent's home
directory. Global skill instructions, licenses, scripts, references, and UI assets
are intentional imports, not permission to import plugin installations or caches.

## Fish, Fisher, and SDKMAN

- Keep the CachyOS Fish config. Layer custom files on top of it.
- Fisher plugins are listed and pinned in `dot_config/fish/fish_plugins`.
- Plugin payloads install into `~/.local/share/fisher` via `conf.d/00-fisher-path.fish`. That directory is not part of this repository.
- Install or update plugins **explicitly** with `fisher update`. Do not run Fisher on every shell launch.
- SDKMAN is installed at `~/.sdkman` and used through `reitzig/sdkman-for-fish`. Do not source SDKMAN’s Bash init scripts from Fish.

## Validation

Before applying risky changes or publishing:

- `fish -n` on every edited Fish file
- `chezmoi managed`, `chezmoi diff`, and `chezmoi apply --dry-run --verbose`
- Confirm a second apply produces no unexpected churn
- Search the staged source for secrets, tokens, private keys, and credential filenames
- Confirm no plugin payloads or nested `.git` directories were added

## Commits and pushes

Do not create commits, add remotes, or push unless the user explicitly asks.
`origin` is already configured. Applying chezmoi is not permission to publish.
