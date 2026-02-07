# tasks/xfce_restore.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import server


def apply(archive_path="captures/xfce/xfce-panel-capture.tar.gz"):
    home = host.get_fact(Home)

    xfconf_xml_dir = f"{home}/.config/xfce4/xfconf/xfce-perchannel-xml"
    xfconf_xml_file = f"{xfconf_xml_dir}/xfce4-panel.xml"
    panel_dir = f"{home}/.config/xfce4/panel"

    server.shell(
        name="xfce_restore: restore panel + launchers from capture",
        commands=[
            rf"""
set -e

ARCHIVE="{archive_path}"
test -f "$ARCHIVE" || {{ echo "Missing archive: $ARCHIVE"; exit 1; }}

RESTORE_TMP="$(mktemp -d)"
cleanup() {{ rm -rf "$RESTORE_TMP"; }}
trap cleanup EXIT

tar -xzf "$ARCHIVE" -C "$RESTORE_TMP"

test -f "$RESTORE_TMP/xfce/xfce4-panel.xml" || {{ echo "Archive missing xfce/xfce4-panel.xml"; exit 1; }}
test -d "$RESTORE_TMP/xfce/panel" || {{ echo "Archive missing xfce/panel/"; exit 1; }}

mkdir -p "{xfconf_xml_dir}"
mkdir -p "{panel_dir}"

STAMP="$(date -u +%Y%m%d-%H%M%SZ)"
[ -f "{xfconf_xml_file}" ] && cp -a "{xfconf_xml_file}" "{xfconf_xml_file}.bak-$STAMP" || true
[ -d "{panel_dir}" ] && cp -a "{panel_dir}" "{panel_dir}.bak-$STAMP" || true

cp -a "$RESTORE_TMP/xfce/xfce4-panel.xml" "{xfconf_xml_file}"
rm -rf "{panel_dir}"
cp -a "$RESTORE_TMP/xfce/panel" "{panel_dir}"

# Best-effort reload (won't work if no GUI session)
pkill -u "$USER" xfconfd 2>/dev/null || true
xfce4-panel -r 2>/dev/null || true
"""
        ],
        _sudo=False,  # important: restore into the current user’s HOME
    )
