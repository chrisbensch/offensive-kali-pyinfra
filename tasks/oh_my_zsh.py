# tasks/oh_my_zsh.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import server, files
from data import KALI_USER


def apply():
    home = host.get_fact(Home)
    oh_my_zsh_dir = f"{home}/.oh-my-zsh"
    zshrc = f"{home}/.zshrc"

    # Install oh-my-zsh only if it's missing. Avoid changing shell or launching zsh.
    server.shell(
        name="oh-my-zsh: install if missing (non-interactive)",
        commands=[
            f'test -d "{oh_my_zsh_dir}" && exit 0',
            r'RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
        ],
        _sudo=False,
    )

    # Ensure a .zshrc exists to avoid later tooling failures.
    files.file(
        name="oh-my-zsh: ensure .zshrc exists",
        path=zshrc,
        present=True,
        _sudo=False,
    )
