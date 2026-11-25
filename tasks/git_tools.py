from shlex import quote

from pyinfra import host
from pyinfra.facts.files import Directory
from pyinfra.operations import files, git, server

from data import KALI_USER, OPT_REPOS


TOOLS_DIR = "/opt/tools"


def apply():
    files.directory(
        name="git_tools: restore system ownership of /opt",
        path="/opt",
        user="root",
        group="root",
        mode="0755",
        _sudo=True,
    )
    files.directory(
        name="git_tools: make /opt/tools writable by the desktop user",
        path=TOOLS_DIR,
        user=KALI_USER,
        group=KALI_USER,
        mode="0755",
        _sudo=True,
    )

    for name, url in OPT_REPOS:
        legacy = f"/opt/{name}"
        dest = f"{TOOLS_DIR}/{name}"
        # Pyinfra plans clone/pull using pre-deploy facts. Move existing
        # checkouts on this run and let the next run handle normal updates.
        if host.get_fact(Directory, path=f"{legacy}/.git"):
            server.shell(
                name=f"git_tools: migrate {name} to {TOOLS_DIR}",
                commands=[f"""
set -eu
legacy={quote(legacy)}
dest={quote(dest)}
if [ -L "$legacy" ] || [ -e "$dest" ] || [ -L "$dest" ]; then
    echo "Cannot safely move $legacy to $dest; check both paths." >&2
    exit 1
fi
origin=$(runuser -u {quote(KALI_USER)} -- git -C "$legacy" config --get remote.origin.url)
if [ "$origin" != {quote(url)} ]; then
    echo "Unexpected Git origin for $legacy; leaving the checkout in place." >&2
    exit 1
fi
mv --no-target-directory --no-clobber -- "$legacy" "$dest"
test ! -e "$legacy"
"""],
                _sudo=True,
            )
        else:
            git.repo(
                name=f"git_tools: clone/update {name}",
                src=url,
                dest=dest,
                pull=True,
                _sudo=False,
            )
