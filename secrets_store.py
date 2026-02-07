# secrets_store.py
import os
import getpass
from functools import lru_cache

@lru_cache(maxsize=1)
def kali_password(prompt="Kali SSH password: "):
    # Optional override for CI; otherwise prompt
    return os.getenv("KALI_PASS") or getpass.getpass(prompt)
