# Interactive bindings only. Do not autoload the fzf package's
# fzf_key_bindings — that vendor file installs competing widgets when sourced.
if not status is-interactive
    exit
end

fish_vi_key_bindings insert

if functions -q fzf_configure_bindings
    fzf_configure_bindings --history=ctrl-r
end
