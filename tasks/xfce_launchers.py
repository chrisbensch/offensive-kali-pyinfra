import json
import shlex

from pyinfra.operations import server

from data import PANEL_LAUNCHERS


def apply():
    server.shell(
        name="xfce: configure panel launchers",
        commands=[shlex.join([
            "python3", "files/xfce/configure_launchers.py", json.dumps(PANEL_LAUNCHERS),
        ])],
        _sudo=False,
    )
