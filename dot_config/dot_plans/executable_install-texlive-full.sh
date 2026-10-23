#!/usr/bin/env bash
set -Eeuo pipefail

# Full TeX Live, PDF tools, and fonts for Arch/CachyOS. Run as the user who
# owns the desktop session; pacman prompts for sudo and paru must not run as root.
if [[ $EUID -eq 0 ]]; then
	printf 'Run as your normal desktop user; this script invokes sudo for pacman.\n' >&2
	exit 1
fi
command -v sudo >/dev/null || { printf 'sudo is required.\n' >&2; exit 1; }
command -v paru >/dev/null || { printf 'Install paru first (Sioyek is installed from the AUR).\n' >&2; exit 1; }
sudo -v

mapfile -t tex_languages < <(pacman -Sgq texlive-lang | sort -u)
mapfile -t nerd_fonts < <(pacman -Sgq nerd-fonts | sort -u)
[[ ${#tex_languages[@]} -gt 0 ]] || { printf 'Could not resolve texlive-lang group.\n' >&2; exit 1; }
[[ ${#nerd_fonts[@]} -gt 0 ]] || { printf 'Could not resolve nerd-fonts group.\n' >&2; exit 1; }

packages=(
	texlive-meta texlive-doc biber ghostscript perl-yaml-tiny perl-file-homedir
	texlab zathura zathura-pdf-mupdf tree-sitter-cli lazygit
	"${tex_languages[@]}" "${nerd_fonts[@]}"
)

# Fail before the transaction if a repository/group entry is stale or invalid.
for package in "${packages[@]}"; do
	pacman -Si "$package" >/dev/null 2>&1 || {
		printf 'Package is not available from configured repositories: %s\n' "$package" >&2
		exit 1
	}
done

printf 'Pacman will install %d explicitly requested packages, including all TeX language collections and %d Nerd Font packages.\n' \
	"${#packages[@]}" "${#nerd_fonts[@]}"
printf 'texlive-doc and texlive-meta are very large; review pacman\x27s download and installed-size summary before confirming.\n'
sudo pacman -Syu --needed "${packages[@]}"

# Keep the AUR build and PKGBUILD review in the unprivileged user context.
paru -S --needed sioyek

cat <<'EOF'

Installation finished. Test with:
  pdflatex --version; xelatex --version; lualatex --version
  latexmk -v; biber --version; latexindent --version
  zathura --version; sioyek --version
  fc-match 'Iosevka Nerd Font'

Use pacman for future TeX Live updates; do not run sudo tlmgr to overwrite
distribution-managed TeX files. Run compilation as your normal user.
EOF
