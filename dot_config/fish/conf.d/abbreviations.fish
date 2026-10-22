# Visible expansions. CachyOS eza aliases stay in the distro config.
if not status is-interactive
    exit
end

# Git inspection
abbr -a g git
abbr -a gs git status
abbr -a gd git diff
abbr -a gds git diff --staged
abbr -a gl git log --oneline --graph --decorate -n 20

# Git changes
abbr -a ga git add
abbr -a gap git add --patch
abbr -a gc git commit
abbr -a gcm git commit -m

# Branches
abbr -a gb git branch
abbr -a gsw git switch
abbr -a gsc git switch --create

# Remotes
abbr -a gf git fetch
abbr -a gpl git pull --ff-only
abbr -a gp git push

# Navigation
abbr -a .. cd ..
abbr -a ... cd ../..
abbr -a md mkdir -p

# Development
abbr -a v nvim
if command -q lazygit
    abbr -a lg lazygit
end

# Chezmoi
abbr -a cm chezmoi
abbr -a cme chezmoi edit
abbr -a cmd chezmoi diff
abbr -a cma chezmoi apply
