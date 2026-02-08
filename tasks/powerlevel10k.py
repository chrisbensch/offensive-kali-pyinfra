# tasks/powerlevel10k.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import server, files, git


def apply():
    home = host.get_fact(Home)
    theme_dir = f"{home}/.oh-my-zsh/custom/themes/powerlevel10k"
    p10k_dst = f"{home}/.p10k.zsh"
    zshrc = f"{home}/.zshrc"

    # Install theme if missing (non-interactive).
    git.repo(
        name="powerlevel10k: clone theme if missing",
        src="https://github.com/romkatv/powerlevel10k.git",
        dest=theme_dir,
        pull=False,
    )

    files.put(
        name="powerlevel10k: install .p10k.zsh",
        src="files/powerlevel10k/p10k.zsh",
        dest=p10k_dst,
        _sudo=False,
    )

    files.replace(
        name="powerlevel10k: set ZSH_THEME",
        path=zshrc,
        text=r"^ZSH_THEME=.*$",
        replace='ZSH_THEME="powerlevel10k/powerlevel10k"',
    )

    files.line(
        name="powerlevel10k: ensure ZSH_THEME is set if missing",
        path=zshrc,
        line='ZSH_THEME="powerlevel10k/powerlevel10k"',
        _sudo=False,
    )

    files.line(
        name="powerlevel10k: source .p10k.zsh from .zshrc",
        path=zshrc,
        line="[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh",
        _sudo=False,
    )
