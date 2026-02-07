# tasks/vscode_extensions.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import server
from data import VSCODE_EXTENSIONS

def apply():
    home = host.get_fact(Home)

    # Pick the binary that exists (Microsoft VS Code usually "code", OSS build may differ)
    # We avoid failing hard here and give a clearer error.
    detect_bin = "command -v code >/dev/null 2>&1 && echo code || (command -v code-oss >/dev/null 2>&1 && echo code-oss || echo '')"

    commands = [
        f'VSCODE_BIN="$({detect_bin})"; test -n "$VSCODE_BIN" || (echo "VS Code CLI not found (code/code-oss)"; exit 1)',
        # Ensure VS Code uses the right HOME (important if you set global sudo elsewhere)
        f'export HOME="{home}"',
    ]

    for ext in VSCODE_EXTENSIONS:
        commands.append(
            # Install only if missing:
            f'VSCODE_BIN="$({detect_bin})"; '
            f'"$VSCODE_BIN" --list-extensions | grep -qx "{ext}" || "$VSCODE_BIN" --install-extension "{ext}"'
        )

    server.shell(
        name="vscode: install extensions",
        commands=commands,
        _sudo=False,
    )
