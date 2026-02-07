# tasks/xfce.py
from pyinfra.operations import server
from data import KALI_USER, XFCE

def apply():
    launcher_id = XFCE["panel_launcher_plugin_id"]
    launcher_items = XFCE["launcher_items"]

    # Set launcher item ordering (string array)
    # NOTE: The exact property path is typically under xfce4-panel channel plugin config.
    # You should confirm on your box with:
    #   xfconf-query -c xfce4-panel -lv | grep -i launcher -n
    items_prop = f"/plugins/plugin-{launcher_id}/items"

    # Build xfconf-query command that (re)creates the property as a string array
    # We do: -n (create) -t string repeated -s repeated.
    cmd = ["xfconf-query", "-c", "xfce4-panel", "-p", items_prop, "-n"]
    for item in launcher_items:
        cmd += ["-t", "string", "-s", item]

    server.shell(
        name="xfce: set panel launcher item order",
        commands=[" ".join(cmd)],
        _sudo=True,
        #_sudo_user=KALI_USER,
    )

    # Disable power management features (verify exact keys on your system with -lv)
    if XFCE.get("disable_power_manager", False):
        server.shell(
            name="xfce: disable xfce4-power-manager features (verify keys with -lv)",
            commands=[
                # List existing keys for troubleshooting/adjustment:
                r"xfconf-query -c xfce4-power-manager -lv || true",
                # Common toggles (may vary by version; adjust to match what -lv shows):
                r'xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/dpms-enabled -n -t bool -s false || true',
                r'xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-ac -n -t int -s 0 || true',
                r'xfconf-query -c xfce4-power-manager -p /xfce4-power-manager/blank-on-battery -n -t int -s 0 || true',
            ],
            _sudo=True,
            #_sudo_user=KALI_USER,
        )

    # Disable screensaver + lock (depends on xfce4-screensaver vs xscreensaver)
    if XFCE.get("disable_screensaver", False) or XFCE.get("disable_screen_lock", False):
        server.shell(
            name="xfce: disable screensaver/lock (verify channels present)",
            commands=[
                # If xfce4-screensaver is in use:
                r"xfconf-query -c xfce4-screensaver -lv || true",
                r'xfconf-query -c xfce4-screensaver -p /saver/enabled -n -t bool -s false || true',
                r'xfconf-query -c xfce4-screensaver -p /lock/enabled -n -t bool -s false || true',

                # If xscreensaver is used instead, you may prefer removing/disable its autostart:
                # (leave this commented unless you confirm you use xscreensaver)
                # r"rm -f ~/.config/autostart/xscreensaver.desktop || true",
            ],
            _sudo=True,
            #_sudo_user=KALI_USER,
        )
