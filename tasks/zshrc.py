# tasks/zshrc.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import files


def apply():
    home = host.get_fact(Home)
    dest = f"{home}/.zshrc"

    files.put(
        name="zshrc: install managed .zshrc",
        src="files/zsh/zshrc",
        dest=dest,
        _sudo=False,
    )
