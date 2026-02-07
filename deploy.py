# deploy.py
from pyinfra import config
#config.SUDO = True  # makes sudo global default for operations

from tasks import bootstrap_sudo, common, git_tools, uv_tools, vscode, xfce


# 1) First run: you’ll need to satisfy sudo prompting somehow for bootstrap_sudo.
bootstrap_sudo.apply()

# 2) After that, everything else can assume passwordless sudo.
common.apply()
vscode.apply(flavor="microsoft")  # or flavor="oss"
git_tools.apply()
uv_tools.apply()
xfce.apply()
