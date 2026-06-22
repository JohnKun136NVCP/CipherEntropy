import ctypes
import os


# Upload library
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(BASE_DIR, "librc4.so")
lib = ctypes.CDLL(lib_path)

# Types of C
lib.rc4_file.argtypes = [
    ctypes.c_char_p,
    ctypes.c_char_p,
    ctypes.POINTER(ctypes.c_ubyte),
    ctypes.c_int
]

lib.rc4_file.restype = ctypes.c_int


def rc4_file(infile: str, outfile: str, key: bytes):
    #convertr key to array C
    key_array = (ctypes.c_ubyte * len(key))(*key)

    result = lib.rc4_file(
        infile.encode('utf-8'),
        outfile.encode('utf-8'),
        key_array,
        len(key)
    )

    if result != 0:
        raise RuntimeError("Error al procesar RC4")

"""
key = generateTokenCiphers("RC4")
print(key.hex())

rc4_file("steam.dmg", "Steam.enc", key)
rc4_file("Steam.enc", "Steam_r.dmg", key)


with open("hola.enc", "rb") as f:
    encrypted_data = f.read()

print(encrypted_data.hex())
"""