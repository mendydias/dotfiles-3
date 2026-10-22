# Intentional environment. Keep this out of fish_variables.

if not test -d ~/.local/bin
    mkdir -p ~/.local/bin
end

# --path updates $PATH directly; --global avoids writing universal variables.
fish_add_path --global --path ~/.local/bin
fish_add_path --global --path ~/.opencode/bin

set -gx EDITOR nvim
set -gx VISUAL nvim
set -gx SDKMAN_DIR $HOME/.sdkman
