# tasks/display_resolution.py
from pyinfra.operations import server


def apply():
    server.shell(
        name="display: set resolution once (if DISPLAY is available)",
        commands=[
            r'''
set -euo pipefail

RESOLUTION="1600x900"

if [ -z "${DISPLAY:-}" ]; then
  echo "DISPLAY is not set; skipping resolution change."
  exit 0
fi

primary_output="$(xrandr --query | awk '/ connected primary/{print $1; exit}')"
if [ -z "${primary_output}" ]; then
  primary_output="$(xrandr --query | awk '/ connected/{print $1; exit}')"
fi

if [ -z "${primary_output}" ]; then
  echo "No connected display found."
  exit 0
fi

xrandr --output "$primary_output" --mode "$RESOLUTION"
'''.strip()
        ],
        _sudo=False,
    )
