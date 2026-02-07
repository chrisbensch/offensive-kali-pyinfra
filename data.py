# data.py
KALI_USER = "kali"

APT_COMMON = [
    "git", "curl", "wget",
    "xfconf",  # for xfconf-query
    "build-essential", "python3-dev", "rustc", # at minimum for netexec
]

APT_CUSTOM_TOOLS = [
    # add your apt-installed tools here
]

OPT_REPOS = [
    ("linpeas", "https://github.com/peass-ng/PEASS-ng.git"),
    ("pspy", "https://github.com/DominicBreuker/pspy.git"),
]

UV_TOOLS = [
    # examples; replace with what you want
    "ruff",
    "httpie",
    "updog",
]

UV_GIT_TOOLS = [
    # You can pin a tag/branch/commit like pip:
    # "git+https://github.com/org/project.git@v1.2.3",
    # "git+https://github.com/org/project.git@main",
    #"git+https://github.com/projectname/project.git",
]

UV_PIP_PACKAGES = [
    "ipython",
    "requests",
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

# XFCE tuning you want to enforce
XFCE = {
    # launcher ordering: list of .desktop files (we'll apply to a chosen launcher plugin)
    "launcher_items": [
        "xfce4-terminal.desktop",
        "firefox-esr.desktop",
        # add more; order here is the order on the panel
    ],

    # Power/screensaver/lock intent (we’ll set keys explicitly, but you should confirm key names with -lv once)
    "disable_power_manager": True,
    "disable_screensaver": True,
    "disable_screen_lock": True,

    # If you want to “pin” the launcher plugin id (simple + deterministic):
    # find it once with: xfconf-query -c xfce4-panel -lv | less
    "panel_launcher_plugin_id": 3,
}
