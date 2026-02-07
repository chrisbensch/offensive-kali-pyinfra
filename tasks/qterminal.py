# tasks/qterminal.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import files

def apply():
    home = host.get_fact(Home)
    dest_dir = f"{home}/.config/qterminal.org"
    dest_file = f"{dest_dir}/qterminal.ini"

    # IMPORTANT: ensure this runs as the desktop user, not root
    files.directory(
        name="qterminal: ensure config dir exists",
        path=dest_dir,
        present=True,
        _sudo=False,
    )

    files.put(
        name="qterminal: install qterminal.ini",
        src="files/qterminal/qterminal.ini",
        dest=dest_file,
        _sudo=False,
    )
