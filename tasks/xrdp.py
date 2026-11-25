from pyinfra.operations import apt, server


def apply():
    apt.packages(
        name="xrdp: install XRDP and its Xorg backend",
        packages=["xrdp", "xorgxrdp"],
        _sudo=True,
    )

    server.shell(
        name="xrdp: grant TLS key access and enable the service",
        commands=[r"""
set -eu

ssl_group=$(getent group ssl-cert | cut -d: -f3)
test -n "$ssl_group"
case " $(id -G xrdp) " in
    *" $ssl_group "*) ;;
    *) adduser xrdp ssl-cert ;;
esac

pid=$(systemctl show --property=MainPID --value xrdp.service)
# A running daemon needs a restart if it started before the group was added.
if [ "${pid:-0}" -ne 0 ] && ! awk -v group="$ssl_group" '
    /^Groups:/ {
        for (i = 2; i <= NF; i++)
            if ($i == group)
                found = 1
    }
    END { exit !found }
' "/proc/$pid/status"; then
    systemctl restart xrdp.service
fi

systemctl enable --now xrdp.service
"""],
        _sudo=True,
    )
