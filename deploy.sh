#!/usr/bin/env zsh
set -euo pipefail

REPO_DIR="${0:A:h}"

# Ensure uv is usable in *this* run (installer typically places it in ~/.local/bin)
export PATH="$HOME/.local/bin:$PATH"

print "[*] Installing uv (if needed)..."
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Re-assert PATH in case the installer just created ~/.local/bin/uv
export PATH="$HOME/.local/bin:$PATH"

print "[*] Installing pyinfra with uv (if needed)..."
if ! command -v pyinfra >/dev/null 2>&1; then
  uv tool install pyinfra
fi

print "[*] Updating zsh PATH via uv..."
# According to uv guidance, this can set PATH for uv in ~/.zshenv [[1]]
uv tool update-shell

print "[*] pyinfra version:"
pyinfra --version

print "[*] Running pyinfra locally..."
cd "$REPO_DIR"
pyinfra inventory.py deploy.py --dry
