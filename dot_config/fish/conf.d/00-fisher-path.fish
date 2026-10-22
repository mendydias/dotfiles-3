# Keep Fisher payloads out of ~/.config/fish so this repo can track only
# fish_plugins and human-maintained files.
set -g fisher_path $HOME/.local/share/fisher

if not test -d $fisher_path
    mkdir -p $fisher_path/{functions,completions,conf.d,themes}
end

set fish_function_path $fish_function_path[1] $fisher_path/functions $fish_function_path[2..]
set fish_complete_path $fish_complete_path[1] $fisher_path/completions $fish_complete_path[2..]

if test -d $fisher_path/conf.d
    for file in $fisher_path/conf.d/*.fish
        if test -f $file
            source $file
        end
    end
end
