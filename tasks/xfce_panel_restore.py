# tasks/xfce_restore.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import server


def apply(archive_path="captures/xfce/xfce-panel-capture.tar.gz", start_panel=True):
    """
    Restores XFCE panel snapshot from a tar.gz created from:
      - ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
      - ~/.config/xfce4/panel/

    start_panel:
      - True: attempt to start panel (without xfce4-panel -r / DBus restart)
      - False: just restore files; user can log out/in or start panel manually
    """
    home = host.get_fact(Home)

    xfconf_xml_dir = f"{home}/.config/xfce4/xfconf/xfce-perchannel-xml"
    xfconf_xml_file = f"{xfconf_xml_dir}/xfce4-panel.xml"
    panel_dir = f"{home}/.config/xfce4/panel"

    start_panel_sh = "1" if start_panel else "0"

    server.shell(
        name="xfce_restore: restore panel + launchers from capture",
        _sudo=False,  # must run as the desktop user
        commands=[
            rf"""
set -euo pipefail

ARCHIVE="{archive_path}"
test -f "$ARCHIVE" || {{ echo "Missing archive: $ARCHIVE"; exit 1; }}

# Stop panel & xfconf daemon to avoid them rewriting config mid-restore
# (Common troubleshooting flow is quit panel, kill xfconfd, then start panel again.) [[6]]
pkill -u "$USER" xfce4-panel 2>/dev/null || true
pkill -u "$USER" xfconfd 2>/dev/null || true

RESTORE_TMP="$(mktemp -d)"
cleanup() {{ rm -rf "$RESTORE_TMP"; }}
trap cleanup EXIT

tar -xzf "$ARCHIVE" -C "$RESTORE_TMP"

test -f "$RESTORE_TMP/xfce/xfce4-panel.xml" || {{ echo "Archive missing: xfce/xfce4-panel.xml"; exit 1; }}
test -d "$RESTORE_TMP/xfce/panel" || {{ echo "Archive missing: xfce/panel/"; exit 1; }}

mkdir -p "{xfconf_xml_dir}"

STAMP="$(date -u +%Y%m%d-%H%M%SZ)"
[ -f "{xfconf_xml_file}" ] && cp -a "{xfconf_xml_file}" "{xfconf_xml_file}.bak-$STAMP" || true
[ -d "{panel_dir}" ] && cp -a "{panel_dir}" "{panel_dir}.bak-$STAMP" || true

cp -a "$RESTORE_TMP/xfce/xfce4-panel.xml" "{xfconf_xml_file}"
rm -rf "{panel_dir}"
cp -a "$RESTORE_TMP/xfce/panel" "{panel_dir}"

# Validate: no empty launcher directories (blank icon symptom)
EMPTY=0
for d in "{panel_dir}"/launcher-*; do
  [ -d "$d" ] || continue
  if ! ls "$d"/*.desktop >/dev/null 2>&1; then
    echo "EMPTY launcher dir (no .desktop): $d"
    EMPTY=$((EMPTY+1))
  fi
done
if [ "$EMPTY" -ne 0 ]; then
  echo "Restore completed, but one or more launcher dirs are empty."
  exit 1
fi

# IMPORTANT: avoid `xfce4-panel -r` (can crash / trigger restart errors). [[2]]
# Many systems will auto-restart the panel after it is killed. [[2]]
if [ "{start_panel_sh}" = "1" ] && [ -n "${{DISPLAY:-}}" ]; then
  # Start a new panel process directly (no DBus restart); don't fail deploy if it can't start here.
  nohup xfce4-panel >/dev/null 2>&1 &
fi

echo "XFCE panel restore complete."
"""
        ],
    )
