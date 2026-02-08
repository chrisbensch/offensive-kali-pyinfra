# tasks/zsh_plugins.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import server, files, git


def apply():
    home = host.get_fact(Home)
    plugins_dir = f"{home}/.oh-my-zsh/custom/plugins"
    zshrc = f"{home}/.zshrc"

    git.repo(
        name="zsh_plugins: clone zsh-autosuggestions if missing",
        src="https://github.com/zsh-users/zsh-autosuggestions.git",
        dest=f"{plugins_dir}/zsh-autosuggestions",
        pull=False,
    )

    git.repo(
        name="zsh_plugins: clone zsh-syntax-highlighting if missing",
        src="https://github.com/zsh-users/zsh-syntax-highlighting.git",
        dest=f"{plugins_dir}/zsh-syntax-highlighting",
        pull=False,
    )

    server.shell(
        name="zsh_plugins: merge plugins into .zshrc",
        commands=[
            f"""
set -euo pipefail
ZSHRC="{zshrc}"
export ZSHRC
python3 - <<'PY'
import os
import re

zshrc = os.environ["ZSHRC"]
desired = ["zsh-autosuggestions", "zsh-syntax-highlighting"]

def parse_plugins(line: str):
    m = re.match(r"^plugins=\\((.*)\\)\\s*$", line)
    if not m:
        return []
    body = m.group(1)
    # Keep only printable, non-empty tokens (avoid control chars).
    tokens = re.findall(r"[A-Za-z0-9_.+-]+", body)
    return tokens

if not os.path.exists(zshrc):
    with open(zshrc, "a", encoding="utf-8") as f:
        f.write("plugins=(git zsh-autosuggestions zsh-syntax-highlighting)\\n")
    raise SystemExit(0)

with open(zshrc, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

idx = None
current = []
for i, line in enumerate(lines):
    if line.startswith("plugins="):
        idx = i
        current = parse_plugins(line)
        break

# Preserve existing order; append desired if missing.
seen = set()
merged = []
for p in current:
    if p not in seen:
        merged.append(p)
        seen.add(p)
for p in desired:
    if p not in seen:
        merged.append(p)
        seen.add(p)

newline = "plugins=(" + " ".join(merged) + ")\\n"
if idx is None:
    lines.append(newline)
else:
    lines[idx] = newline

with open(zshrc, "w", encoding="utf-8") as f:
    f.writelines(lines)
PY
""".strip(),
        ],
        _sudo=False,
    )
