import secrets_store as _secrets_store

#ssh_user = "kali"
#ssh_password = _secrets_store.kali_password("Kali SSH password: ")

#ssh_allow_agent = False
#ssh_look_for_keys = False

# Add this (use same password if SSH & sudo are the same on your VM):
sudo_password = _secrets_store.kali_password("Kali sudo password: ")

del _secrets_store
