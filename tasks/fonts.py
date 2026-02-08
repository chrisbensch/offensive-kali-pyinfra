# tasks/fonts.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import files, server


FONT_URLS = [
    (
        "https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Regular.ttf",
        "MesloLGS NF Regular.ttf",
    ),
    (
        "https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Bold.ttf",
        "MesloLGS NF Bold.ttf",
    ),
    (
        "https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Italic.ttf",
        "MesloLGS NF Italic.ttf",
    ),
    (
        "https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Bold%20Italic.ttf",
        "MesloLGS NF Bold Italic.ttf",
    ),
]


def apply():
    home = host.get_fact(Home)
    fonts_dir = f"{home}/.fonts"

    files.directory(
        name="fonts: ensure ~/.fonts exists",
        path=fonts_dir,
        present=True,
        _sudo=False,
    )

    commands = []
    for url, filename in FONT_URLS:
        dest = f"{fonts_dir}/{filename}"
        commands.append(f'test -f "{dest}" || curl -fsSL "{url}" -o "{dest}"')

    server.shell(
        name="fonts: install MesloLGS Nerd Font files",
        commands=commands,
        _sudo=False,
    )

    server.shell(
        name="fonts: refresh font cache",
        commands=["fc-cache -f"],
        _sudo=False,
    )
