# tasks/uv_tools.py
from pyinfra.operations import files, server
from data import KALI_USER, UV_TOOL_SPECS

def apply():
    home = f"/home/{KALI_USER}"
    uv = f"{home}/.local/bin/uv"

    server.shell(
        name="uv_tools: install uv (user-local)",
        commands=[
            r'command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh',
            f"{uv} --version",
        ],
        _sudo=False,
    )

    # Ensure ~/.local/bin is on PATH for interactive shells
    for rc in (f"{home}/.zshrc", f"{home}/.bashrc"):
        files.line(
            name=f"uv_tools: ensure ~/.local/bin in PATH ({rc})",
            path=rc,
            line='export PATH="$HOME/.local/bin:$PATH"',
        )

    commands = []
    for tool in UV_TOOL_SPECS:
        spec = tool["spec"]
        with_deps = tool.get("with", [])
        if with_deps:
            commands.append(f'{uv} tool install --with {",".join(with_deps)} "{spec}"')
        else:
            commands.append(f'{uv} tool install "{spec}"')

    server.shell(
        name="uv_tools: install uv tools",
        commands=commands,
        _sudo=False,
    )
