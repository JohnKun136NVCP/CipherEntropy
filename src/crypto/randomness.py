import secrets
import string
import os
def generateTokenCiphers(cipher:str):
    if cipher == "DES":
        string_size = 8
        alf = string.ascii_letters + string.digits
        chain = ''.join(secrets.choice(alf) for _ in range(string_size))
        return chain.encode()
    elif cipher == "RC4":
        return secrets.token_bytes(16)
    elif cipher == "AES":
        return secrets.token_bytes(32)
    else:
        return 0
def generate_iv(cipher:str) -> bytes:
    if cipher == "DES":
        return os.urandom(8)
    else:
        return os.urandom(16)
