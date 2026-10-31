source /usr/share/cachyos-fish-config/cachyos-config.fish

# OpenCode's Ctrl+X, then E prompt editor workflow.
set -gx EDITOR nvim
set -gx VISUAL nvim
set -gx LIBRARY_PATH ~/Documents/Books/

# Override CachyOS's Fastfetch greeting without changing its other defaults.
function fish_greeting
end

if status is-interactive
    zoxide init fish | source
    if command -q direnv
        direnv hook fish | source
    end
end
