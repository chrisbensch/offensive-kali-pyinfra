# tasks/xfce_restore.py
from pyinfra import host
from pyinfra.facts.server import Home
from pyinfra.operations import files, server


def apply(archive_path="captures/xfce/xfce-panel-capture.tar.gz"):
    """
    Restores:
      - ~/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
      - ~/.config/xfce4/panel/ (launcher-* etc)

    archive_path should point at the tar.gz you created.
    """

    home = host.get_fact(Home)

    xfconf_xml_dir = f"{home}/.config/xfce4/xfconf/xfce-perchannel-xml"
    xfconf_xml_file = f"{xfconf_xml_dir}/xfce4-panel.xml"
    panel_dir = f"{home}/.config/xfce4/panel"

    files.directory(
        name="xfce_restore: ensure xfconf xml dir exists",
        path=xfconf_xml_dir,
        present=True,
        _sudo=False,
    )

    files.directory(
        name="xfce_restore: ensure panel dir exists",
        path=panel_dir,
        present=True,
        _sudo=False,
    )

    server.shell(
        name="xfce_restore: restore panel + launchers from capture",
        commands=[
            # Safety checks
            f'test -f "{archive_path}" || (echo "Missing archive: {archive_path}" && exit 1)',

            # Extract somewhere safe
            'RESTORE_TMP="$(mktemp -d)"',
            f'tar -xzf "{archive_path}" -C "$RESTORE_TMP"',
            'test -f "$RESTORE_TMP/xfce/xfce4-panel.xml" || (echo "Archive missing xfce/xfce4-panel.xml" && exit 1)',
            'test -d "$RESTORE_TMP/xfce/panel" || (echo "Archive missing xfce/panel/" && exit 1)',

            # Backup existing (non-fatal if missing)
            'STAMP="$(date -u +%Y%m%d-%H%M%SZ)"',
            f'[ -f "{xfconf_xml_file}" ] && cp -a "{xfconf_xml_file}" "{xfconf_xml_file}.bak-$STAMP" || true',
            f'[ -d "{panel_dir}" ] && cp -a "{panel_dir}" "{panel_dir}.bak-$STAMP" || true',

            # Restore the captured files
            f'cp -a "$RESTORE_TMP/xfce/xfce4-panel.xml" "{xfconf_xml_file}"',
            # Replace panel directory contents to match capture
            f'rm -rf "{panel_dir}"',
            f'cp -a "$RESTORE_TMP/xfce/panel" "{panel_dir}"',

            # Cleanup
            'rm -rf "$RESTORE_TMP"',

            # Try to reload if we are in an XFCE session (ignore failures)
            'pkill -u "$USER" xfconfd 2>/dev/null || true',
            'xfce4-panel -r 2>/dev/null || true',
        ],
        _sudo=False,
    )
