from tasks import (
    common,
    fonts,
    git_tools,
    oh_my_zsh,
    powerlevel10k,
    qterminal,
    sudo_policy,
    uv_tools,
    vscode_extensions,
    vscode_repo,
    xfce,
    xfce_launchers,
    xrdp,
    zsh_plugins,
    zshrc,
)


sudo_policy.apply()
vscode_repo.apply()
zshrc.apply()
oh_my_zsh.apply()
powerlevel10k.apply()
zsh_plugins.apply()
fonts.apply()
common.apply()
xrdp.apply()
git_tools.apply()
uv_tools.apply()

vscode_extensions.apply()
qterminal.apply()
xfce.apply()
xfce_launchers.apply()
