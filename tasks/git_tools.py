# tasks/git_tools.py
from pyinfra.operations import files, git
from data import KALI_USER, OPT_REPOS

def apply():
    files.directory(
        name="git_tools: create /opt/tools",
        path="/opt/tools",
        present=True,
        _sudo=True,
    )

    files.directory(
        name="git_tools: ensure /opt/tools owned by kali",
        path="/opt",
        user=KALI_USER,
        group=KALI_USER,
        mode="0775",
        _sudo=True,
    )

    for name, url in OPT_REPOS:
        git.repo(
            name=f"git_tools: clone/update {name}",
            src=url,
            dest=f"/opt/{name}",
            pull=True,
        )
