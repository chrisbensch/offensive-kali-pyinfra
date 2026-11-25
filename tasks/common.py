# tasks/common.py
from pyinfra.operations import apt
from data import APT_COMMON

def apply():
    apt.update(
        name="common: apt update",
        cache_time=3600,
        _sudo=True,
    )

    apt.upgrade(
        name="common: apt upgrade",
        _sudo=True,
    )

    apt.packages(
        name="common: install base packages",
        packages=APT_COMMON,
        _sudo=True,
    )
