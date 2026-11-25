# data.py
KALI_USER = "kali"

APT_COMMON = [
    "git", "curl", "wget",
    "xfconf",  # for xfconf-query
    "build-essential", "python3-dev", "rustc", # minimum for netexec
    "code",
    "obsidian",
    "nmap",
    "xsltproc",
]

OPT_REPOS = [
    ("linpeas", "https://github.com/peass-ng/PEASS-ng.git"),
    ("pspy", "https://github.com/DominicBreuker/pspy.git"),
]

VSCODE_EXTENSIONS = [
    "ms-python.python",
    "ms-azuretools.vscode-docker",
    "redhat.vscode-yaml",
    "eamodio.gitlens",
]

UV_TOOL_SPECS = [
    # Simple PyPI tools:
    {"spec": "ruff"},
    {"spec": "httpie"},

    # GitHub tool + extra deps injected via --with:
    {
        "spec": "git+https://github.com/Pennyw0rth/NetExec",
        "with": ["arc4", "aardwolf", "setuptools"],
    },
]

# Each row is one panel icon. Multiple entries make a dropdown.
# Within an entry, list alternative desktop filenames in preference order.
PANEL_LAUNCHERS = [
    [("firefox-esr.desktop",)],
    [("obsidian.desktop",)],
    [("com.microsoft.VSCode.desktop", "code.desktop")],
    [("org.xfce.mousepad.desktop", "xfce-text-editor.desktop")],
    [("xfce4-terminal-emulator.desktop",), ("root-terminal.desktop",)],
]

XFCE = {
    "disable_power_manager": True,
    "disable_screensaver": True,
    "disable_screen_lock": True,
}
