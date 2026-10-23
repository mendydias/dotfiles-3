source /usr/share/cachyos-fish-config/cachyos-config.fish

# OpenCode's Ctrl+X, then E prompt editor workflow.
set -gx EDITOR nvim
set -gx VISUAL nvim

# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end

if status is-interactive
    zoxide init fish | source
end
