# Change back to the directory Yazi was in when it exits.
if command -q yazi
    function y --wraps yazi --description 'Open Yazi and change the shell directory on exit'
        set -l cwd_file (command mktemp -t yazi-cwd.XXXXXX)
        or return

        command yazi $argv --cwd-file="$cwd_file"
        set -l yazi_status $status

        if test -r "$cwd_file"
            set -l cwd (command cat -- "$cwd_file")
            if test -n "$cwd"; and test "$cwd" != "$PWD"
                cd -- "$cwd"
            end
        end

        command rm -f -- "$cwd_file"
        return $yazi_status
    end
end
