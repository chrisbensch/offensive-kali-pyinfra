# tasks/oh_my_zsh.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import server, files, git, apt
from data import KALI_USER


def apply():
    home = host.get_fact(Home)
    oh_my_zsh_dir = f"{home}/.oh-my-zsh"
    zshrc = f"{home}/.zshrc"

    apt.packages(
        name="oh-my-zsh: install zsh",
        packages=["zsh"],
        _sudo=True,
    )

    # Install oh-my-zsh by cloning the repo (avoids curl/installer side effects).
    git.repo(
        name="oh-my-zsh: clone repo if missing",
        src="https://github.com/ohmyzsh/ohmyzsh.git",
        dest=oh_my_zsh_dir,
        pull=False,
    )

    # Ensure a .zshrc exists to avoid later tooling failures.
    files.file(
        name="oh-my-zsh: ensure .zshrc exists",
        path=zshrc,
        present=True,
        _sudo=False,
    )

    # If .zshrc was just created (or empty), seed it from the template.
    server.shell(
        name="oh-my-zsh: seed .zshrc from template if empty",
        commands=[
            f'[ -s "{zshrc}" ] && exit 0',
            f'cp -n "{oh_my_zsh_dir}/templates/zshrc.zsh-template" "{zshrc}"',
        ],
        _sudo=False,
    )

    # Ensure .zshrc actually loads oh-my-zsh, even if customized.
    files.line(
        name="oh-my-zsh: ensure ZSH path",
        path=zshrc,
        line='export ZSH="$HOME/.oh-my-zsh"',
        _sudo=False,
    )

    files.line(
        name="oh-my-zsh: ensure oh-my-zsh is sourced",
        path=zshrc,
        line='source "$ZSH/oh-my-zsh.sh"',
        _sudo=False,
    )

    # Make zsh the login shell for the user if not already.
    server.shell(
        name="oh-my-zsh: set default shell to zsh",
        commands=[
            f'getent passwd "{KALI_USER}" | cut -d: -f7 | grep -qx "/usr/bin/zsh" && exit 0',
            f'chsh -s /usr/bin/zsh "{KALI_USER}"',
        ],
        _sudo=True,
    )
