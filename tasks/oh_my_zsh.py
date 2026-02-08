# tasks/oh_my_zsh.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import server, files, git


def apply():
    home = host.get_fact(Home)
    oh_my_zsh_dir = f"{home}/.oh-my-zsh"
    zshrc = f"{home}/.zshrc"

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
