"""Reconcile the quick-launch section of the desktop user's first XFCE panel."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from urllib.parse import unquote


CHANNEL = ["xfconf-query", "-c", "xfce4-panel"]
PREFIX = "pyinfra-"
PLUGIN_PATH = "/plugins/plugin-{}"


def query(*args):
    return subprocess.check_output([*CHANNEL, *args], text=True).strip()


def values(path, properties):
    if path not in properties:
        return []
    lines = query("-p", path).splitlines()
    if lines and " is an array with " in lines[0]:
        return [line for line in lines[1:] if line]
    return lines


def set_values(path, kind, desired, properties, *, array=False):
    if values(path, properties) == desired:
        return

    args = ["-p", path]
    if path not in properties:
        args.append("--create")
    if array:
        args.append("--force-array")
    for value in desired:
        args.extend(["--type", kind, "--set", value])
    query(*args)
    properties.add(path)
    if values(path, properties) != desired:
        raise RuntimeError(f"XFCE did not save {path}")


def application_entries(layout):
    home = Path.home()
    data_dirs = [
        Path(os.environ.get("XDG_DATA_HOME") or home / ".local/share"),
        *map(Path, (os.environ.get("XDG_DATA_DIRS") or
                    "/usr/local/share:/usr/share").split(":")),
    ]
    entries = {}
    for row in layout:
        for alternatives in row:
            candidates = [directory / "applications" / name
                          for directory in data_dirs for name in alternatives]
            source = next((candidate for candidate in candidates if candidate.is_file()), None)
            if source is None:
                raise RuntimeError(f"Missing desktop entry: {' or '.join(alternatives)}")
            entries[tuple(alternatives)] = source.read_bytes()
    return entries


def source_name(path):
    if path.name.startswith(PREFIX):
        return path.name.removeprefix(PREFIX)
    match = re.search(r"^X-XFCE-Source=(.*)$", path.read_text(errors="replace"), re.M)
    if match:
        return Path(unquote(match[1])).name
    return path.name


def launcher_locations(layout, panel_dir, panel_ids, other_ids, properties):
    plugin_types = {
        match[1]: values(path, properties)
        for path in sorted(properties)
        if (match := re.fullmatch(r"/plugins/plugin-(\d+)", path))
    }
    used_ids = set(plugin_types) | set(panel_ids) | other_ids
    candidates = {}
    for plugin_id in panel_ids + sorted(set(plugin_types) - set(panel_ids) - other_ids, key=int):
        if plugin_types.get(plugin_id) != ["launcher"]:
            continue
        directory = panel_dir / f"launcher-{plugin_id}"
        items = values(PLUGIN_PATH.format(plugin_id) + "/items", properties)
        files = list(directory.glob("*.desktop"))
        owned = any(file.name.startswith(PREFIX) for file in files)
        if plugin_id not in panel_ids and not owned:
            continue
        if items and not owned:
            files = [directory / item for item in items if (directory / item).is_file()]
        candidates[plugin_id] = (owned, {source_name(file) for file in files})

    selected = []
    for row in layout:
        primary = set(row[0])
        # Prefer a launcher created by this task over one copied by XFCE.
        matches = [plugin_id for plugin_id, (_, names) in candidates.items()
                   if plugin_id not in selected and names & primary]
        if matches:
            selected.append(max(matches, key=lambda plugin_id: candidates[plugin_id][0]))
            continue

        plugin_id = 1
        while str(plugin_id) in used_ids or (panel_dir / f"launcher-{plugin_id}").exists():
            plugin_id += 1
        selected.append(str(plugin_id))
        used_ids.add(str(plugin_id))

    managed = {plugin_id for plugin_id, (owned, _) in candidates.items() if owned}
    primary_names = {name for row in layout for name in row[0]}
    managed.update(plugin_id for plugin_id, (_, names) in candidates.items() if names & primary_names)
    remaining = [plugin_id for plugin_id in panel_ids if plugin_id not in managed]
    insert_at = 0
    if remaining and plugin_types.get(remaining[0]) in (
        ["whiskermenu"], ["applicationsmenu"],
    ):
        insert_at = 1
        if len(remaining) > 1 and plugin_types.get(remaining[1]) == ["separator"]:
            insert_at = 2
    return selected, remaining[:insert_at] + selected + remaining[insert_at:]


def panel_running():
    reply = subprocess.check_output([
        "gdbus", "call", "--session",
        "--dest", "org.freedesktop.DBus", "--object-path", "/org/freedesktop/DBus",
        "--method", "org.freedesktop.DBus.NameHasOwner", "org.xfce.Panel",
    ], text=True, timeout=5)
    return reply.strip() == "(true,)"


def write_entry(path, content):
    if path.is_file() and path.read_bytes() == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
        temporary = Path(temp.name)
        try:
            temp.write(content)
            temp.close()
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def configure(layout):
    entries = application_entries(layout)
    os.environ["LC_ALL"] = "C"
    bus = Path(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}") / "bus"
    if "DBUS_SESSION_BUS_ADDRESS" not in os.environ and bus.is_socket():
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = f"unix:path={bus}"
    if "DBUS_SESSION_BUS_ADDRESS" not in os.environ:
        raise RuntimeError("Run the deployment from the XFCE desktop user's session.")

    config_home = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    panel_dir = config_home / "xfce4/panel"
    properties = set(query("-l").splitlines())
    panels = values("/panels", properties)
    if not panels:
        raise RuntimeError("Start the XFCE desktop once to initialize its panel.")
    order_path = f"/panels/panel-{panels[0]}/plugin-ids"
    panel_ids = values(order_path, properties)
    other_ids = {plugin_id for panel in panels[1:]
                 for plugin_id in values(f"/panels/panel-{panel}/plugin-ids", properties)}

    selected, order = launcher_locations(layout, panel_dir, panel_ids, other_ids, properties)
    launchers = {
        plugin_id: {PREFIX + entry[0]: entries[tuple(entry)] for entry in row}
        for plugin_id, row in zip(selected, layout)
    }
    changed = order != panel_ids
    for plugin_id, files in launchers.items():
        base = PLUGIN_PATH.format(plugin_id)
        directory = panel_dir / f"launcher-{plugin_id}"
        if values(base + "/items", properties) != list(files):
            changed = True
        if any(not (directory / name).is_file() or (directory / name).read_bytes() != content
               for name, content in files.items()):
            changed = True
    if not changed:
        return

    restart = panel_running()
    if restart:
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            raise RuntimeError("Run the deployment from an XFCE terminal to reload the active panel.")
        subprocess.run(["xfce4-panel", "--quit"], check=True, timeout=15)

    try:
        if restart:
            deadline = time.monotonic() + 10
            while panel_running():
                if time.monotonic() >= deadline:
                    raise RuntimeError("XFCE panel did not exit before the launcher update.")
                time.sleep(0.1)

        for plugin_id, files in launchers.items():
            base = PLUGIN_PATH.format(plugin_id)
            directory = panel_dir / f"launcher-{plugin_id}"
            for name, content in files.items():
                write_entry(directory / name, content)
            set_values(base, "string", ["launcher"], properties)
            set_values(base + "/items", "string", list(files), properties, array=True)
        set_values(order_path, "int", order, properties, array=True)
    finally:
        if restart and not panel_running():
            subprocess.Popen(["xfce4-panel"], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             start_new_session=True)


if __name__ == "__main__":
    try:
        configure(json.loads(sys.argv[1]))
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        sys.exit(f"XFCE launcher configuration failed: {error}")
