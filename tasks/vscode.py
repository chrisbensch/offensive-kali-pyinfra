# tasks/vscode.py
from pyinfra.operations import server

def apply():
    server.shell(
        name="vscode: add Microsoft repo key + repo",
        commands=[
            "apt-get update",
            "DEBIAN_FRONTEND=noninteractive apt-get install -y wget gpg",

            "wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /tmp/packages.microsoft.gpg",
            "install -o root -g root -m 644 /tmp/packages.microsoft.gpg /etc/apt/trusted.gpg.d/packages.microsoft.gpg",
            "rm -f /tmp/packages.microsoft.gpg",

            # Multi-arch selector (explicit) [[6]]
            r"""sh -c 'echo "deb [arch=amd64,arm64 signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/vscode/ stable main" > /etc/apt/sources.list.d/vscode.list'""",
        ],
        _sudo=True,
    )

    server.shell(
        name="vscode: apt update + install",
        commands=[
            "apt-get update",
            "DEBIAN_FRONTEND=noninteractive apt-get install -y code",
        ],
        _sudo=True,
    )
