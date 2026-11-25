from pyinfra.operations import server


def apply():
    server.shell(
        name="sudo: retire the legacy passwordless rule",
        commands=[r"""
set -eu

rule=/etc/sudoers.d/010-kali-nopasswd
[ -e "$rule" ] || [ -L "$rule" ] || exit 0
if [ -L "$rule" ] || ! printf '%s\n' 'kali ALL=(ALL:ALL) NOPASSWD: ALL' | cmp -s - "$rule"; then
    echo "Leaving customized sudo policy at $rule in place." >&2
    exit 0
fi

backup_dir=$(mktemp -d /etc/sudoers.d/.pyinfra-sudo.XXXXXX)
backup="$backup_dir/010-kali-nopasswd"
restore_rule() {
    if [ -f "$backup" ]; then
        mv -- "$backup" "$rule"
    fi
    rmdir -- "$backup_dir"
}
trap restore_rule EXIT
trap 'exit 1' HUP INT TERM
mv -- "$rule" "$backup"

# Check the remaining policy as root before committing the migration.
if ! visudo -c -q || ! sudo -l -U kali -u root -- /bin/sh -c true >/dev/null; then
    echo "Remaining sudo policy does not authorize the deployment for kali; restoring $rule." >&2
    exit 1
fi
trap - EXIT HUP INT TERM
echo "Retired the legacy sudo rule; inactive backup at $backup."
"""],
        _sudo=True,
    )
