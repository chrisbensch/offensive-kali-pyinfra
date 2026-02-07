# tasks/bootstrap_sudo.py
from pyinfra.operations import files, server
from data import KALI_USER

def apply():
    tmp_path = f"/tmp/010-{KALI_USER}-nopasswd"
    dest_path = f"/etc/sudoers.d/010-{KALI_USER}-nopasswd"

    # Upload as kali (no sudo needed)
    files.put(
        name="bootstrap_sudo: upload sudoers file to /tmp",
        src=f"files/sudoers/010-{KALI_USER}-nopasswd",
        dest=tmp_path,
        mode="0644",
    )

    # Install as root via pyinfra sudo handling
    server.shell(
        name="bootstrap_sudo: install sudoers drop-in",
        commands=[
            f"install -m 0440 {tmp_path} {dest_path}",
            "visudo -c",
            f"rm -f {tmp_path}",
        ],
        _sudo=True,
    )
