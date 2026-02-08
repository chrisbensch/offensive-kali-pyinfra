# deploy.py
from pyinfra import config
#config.SUDO = True  # makes sudo global default for operations

from tasks import bootstrap_sudo, common, git_tools, uv_tools, vscode_repo, qterminal, vscode_extensions, xfce, xfce_panel_restore, oh_my_zsh, powerlevel10k, zsh_plugins, fonts, zshrc


# 1) First run: you’ll need to satisfy sudo prompting somehow for bootstrap_sudo.
bootstrap_sudo.apply()

# 2) After that, everything else can assume passwordless sudo.
vscode_repo.apply()
zshrc.apply()
oh_my_zsh.apply()
powerlevel10k.apply()
zsh_plugins.apply()
fonts.apply()
common.apply()
git_tools.apply()
uv_tools.apply()

vscode_extensions.apply()
qterminal.apply()
xfce.apply()
xfce_panel_restore.apply()
