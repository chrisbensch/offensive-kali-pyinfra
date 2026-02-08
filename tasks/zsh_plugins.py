# tasks/zsh_plugins.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import server, files


def apply():
    home = host.get_fact(Home)
    plugins_dir = f"{home}/.oh-my-zsh/custom/plugins"
    zshrc = f"{home}/.zshrc"

    server.shell(
        name="zsh_plugins: install zsh-autosuggestions",
        commands=[
            f'test -d "{plugins_dir}/zsh-autosuggestions" && exit 0',
            f'git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions "{plugins_dir}/zsh-autosuggestions"',
        ],
        _sudo=False,
    )

    server.shell(
        name="zsh_plugins: install zsh-syntax-highlighting",
        commands=[
            f'test -d "{plugins_dir}/zsh-syntax-highlighting" && exit 0',
            f'git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting "{plugins_dir}/zsh-syntax-highlighting"',
        ],
        _sudo=False,
    )

    server.shell(
        name="zsh_plugins: merge plugins into .zshrc",
        commands=[
            f"""
set -euo pipefail
ZSHRC="{zshrc}"
DESIRED="zsh-autosuggestions zsh-syntax-highlighting"

if [ ! -f "$ZSHRC" ]; then
  echo "plugins=(git zsh-autosuggestions zsh-syntax-highlighting)" >> "$ZSHRC"
  exit 0
fi

if grep -q '^plugins=' "$ZSHRC"; then
  LINE="$(grep -m1 '^plugins=' "$ZSHRC")"
  CURRENT="$(printf "%s" "$LINE" | sed -n 's/^plugins=(\(.*\))$/\1/p')"
  NEW="$CURRENT"
  for p in $DESIRED; do
    printf "%s\n" $NEW | tr ' ' '\n' | grep -qx "$p" || NEW="$NEW $p"
  done
  NEW="$(printf "%s" "$NEW" | awk '{$1=$1; print}')"
  sed -i "0,/^plugins=/{s|^plugins=.*$|plugins=($NEW)|}" "$ZSHRC"
else
  echo "plugins=(git zsh-autosuggestions zsh-syntax-highlighting)" >> "$ZSHRC"
fi
""".strip(),
        ],
        _sudo=False,
    )
