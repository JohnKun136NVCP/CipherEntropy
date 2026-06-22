"""
des_wrapper.py — Interfaz Python para la biblioteca DES en C.

La clave se conserva en la instancia (self.KEY) exactamente igual que en
la versión original; internamente se delega en la biblioteca compartida C
(libdes.so / des.dll) compilada a partir de des.c + des_tables.c.

Compilar la biblioteca compartida (Linux / macOS):
    gcc -O2 -shared -fPIC -o libdes.so des.c des_tables.c

Windows (MinGW):
    gcc -O2 -shared -o des.dll des.c des_tables.c

Uso:
    from des_wrapper import DES
    des = DES()
    des.randKey()
    des.cifrar_archivo("documento.txt")
    des.descifrar_archivo("documento.txt.enc")
"""

import ctypes
import ctypes.util
from pathlib import Path


# ─── Carga de la biblioteca compartida ────────────────────────────────────────

def _load_lib() -> ctypes.CDLL:
    base = Path(__file__).parent
    candidates = [
        base / "libdes.so",
        base / "libdes.dylib",
        base / "des.dll",
    ]
    for path in candidates:
        if path.exists():
            return ctypes.CDLL(str(path))
    raise FileNotFoundError(
        "No se encontró libdes.so / libdes.dylib / des.dll.\n"
        "Compila con:  gcc -O2 -shared -fPIC -o libdes.so des.c des_tables.c"
    )


_lib = _load_lib()

# ─── Estructura DES_CTX (debe coincidir con des.h) ────────────────────────────

class _DES_CTX(ctypes.Structure):
    _fields_ = [
        ("key",     ctypes.c_uint8 * 8),
        ("key_set", ctypes.c_int),
        ("subkeys", ctypes.c_uint64 * 16),
    ]


# ─── Prototipos C ─────────────────────────────────────────────────────────────

_lib.des_init.argtypes     = [ctypes.POINTER(_DES_CTX)]
_lib.des_init.restype      = None

_lib.des_set_key.argtypes  = [ctypes.POINTER(_DES_CTX), ctypes.c_uint8 * 8]
_lib.des_set_key.restype   = None

_lib.des_encrypt_cbc.argtypes = [
    ctypes.POINTER(_DES_CTX),
    ctypes.c_char_p, ctypes.c_size_t,
    ctypes.c_uint8 * 8,
    ctypes.POINTER(ctypes.c_size_t),
]
_lib.des_encrypt_cbc.restype = ctypes.c_void_p

_lib.des_decrypt_cbc.argtypes = _lib.des_encrypt_cbc.argtypes
_lib.des_decrypt_cbc.restype  = ctypes.c_void_p

_lib.des_encrypt_file.argtypes = [ctypes.POINTER(_DES_CTX), ctypes.c_char_p]
_lib.des_encrypt_file.restype  = ctypes.c_int

_lib.des_decrypt_file.argtypes = [ctypes.POINTER(_DES_CTX), ctypes.c_char_p]
_lib.des_decrypt_file.restype  = ctypes.c_int

_libc = ctypes.CDLL(ctypes.util.find_library("c"))


# ─── Clase pública ────────────────────────────────────────────────────────────

class DES:
    """
    Clase DES compatible con la versión Python original.

    self.KEY es un atributo normal (no property); asignarlo NO llama
    automáticamente a des_set_key en C. Para sincronizar clave+contexto
    usa randKey() o set_key(). Si asignas KEY a mano, llama set_key() después.
    """

    CHUNK_SIZE = 8 * 1024

    def __init__(self):
        self._ctx = _DES_CTX()
        _lib.des_init(ctypes.byref(self._ctx))
        self.KEY: bytes = b""          # atributo normal, sin property

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _sync_key(self, key_bytes: bytes) -> None:
        """Escribe key_bytes en self.KEY y en el contexto C. Sin recursión."""
        if len(key_bytes) != 8:
            raise ValueError(f"DES key must have  8 bytes (you're key's size is {len(key_bytes)}).")
        self.KEY = key_bytes                          # asignación directa normal
        arr = (ctypes.c_uint8 * 8)(*key_bytes)
        _lib.des_set_key(ctypes.byref(self._ctx), arr)

    def _require_key(self) -> None:
        if not self.KEY:
            raise ValueError("Key is not configured. Plese call to randkey() or set_key.")
        # Re-sincronizar por si KEY fue asignado a mano sin llamar set_key()
        arr = (ctypes.c_uint8 * 8)(*self.KEY)
        _lib.des_set_key(ctypes.byref(self._ctx), arr)

    # ── API de clave ──────────────────────────────────────────────────────────

    def randKey(self,key) -> bytes:
        """Genera clave con generateTokenCiphers() y la almacena."""
        key_bytes: bytes = key
        self._sync_key(key_bytes)
        return self.KEY

    def set_key(self, key_bytes: bytes) -> None:
        """
        Equivalente a des.KEY = ... pero también actualiza el contexto C.
        Úsalo cuando asignes la clave manualmente:
            des.set_key(bytes.fromhex("4a6f3135514a6257"))
        """
        self._sync_key(key_bytes)

    # ── CBC en memoria ─────────────────────────────────────────────────────────

    def desEncryptCBC(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        self._sync_key(key)
        iv_arr = (ctypes.c_uint8 * 8)(*iv)
        out_len = ctypes.c_size_t(0)
        ptr = _lib.des_encrypt_cbc(
            ctypes.byref(self._ctx),
            data, len(data),
            iv_arr,
            ctypes.byref(out_len),
        )
        if not ptr:
            raise MemoryError("des_encrypt_cbc devolvió NULL")
        result = bytes((ctypes.c_uint8 * out_len.value).from_address(ptr))
        _libc.free(ctypes.c_void_p(ptr))
        return result

    def desDecryptCBC(self, data: bytes, key: bytes, iv: bytes) -> bytes:
        self._sync_key(key)
        iv_arr = (ctypes.c_uint8 * 8)(*iv)
        out_len = ctypes.c_size_t(0)
        ptr = _lib.des_decrypt_cbc(
            ctypes.byref(self._ctx),
            data, len(data),
            iv_arr,
            ctypes.byref(out_len),
        )
        if not ptr:
            raise ValueError("des_decrypt_cbc devolvió NULL (padding inválido?)")
        result = bytes((ctypes.c_uint8 * out_len.value).from_address(ptr))
        _libc.free(ctypes.c_void_p(ptr))
        return result

    # ── Archivos ───────────────────────────────────────────────────────────────

    def encrypt_file(self, path: str) -> None:
        self._require_key()
        rc = _lib.des_encrypt_file(ctypes.byref(self._ctx), path.encode())
        if rc != 0:
            raise OSError(f"des_encrypt_file falló para '{path}'")

    def decrypt_file(self, path: str) -> None:
        self._require_key()
        rc = _lib.des_decrypt_file(ctypes.byref(self._ctx), path.encode())
        if rc != 0:
            raise OSError(f"des_decrypt_file falló para '{path}'")
    def read_iv_file(self, path: str) -> bytes:
        """Extrae el IV de un archivo .enc sin descifrarlo."""
        with open(path, "rb") as f:
            iv = f.read(8)
        if len(iv) != 8:
            raise ValueError(f"Archivo demasiado pequeño o no es .enc: '{path}'")
        return iv

    def read_iv(path: str) -> bytes:
        """Read IV of file with DES Cipher (8 bytes)"""
        with open(path, "rb") as f:
            return f.read(8)


# ─── Fast Demo ──────────────────────────────────────────────────────────────

#if __name__ == "__main__":
    #des = DES()

    # Asignar clave manualmente (igual que el comentario original)
    #des.set_key(bytes.fromhex("4a6f3135514a6257"))
    #print(f"Clave  : {des.KEY.hex()}")

    # Round-trip CBC
    #iv      = os.urandom(8)
    #mensaje = b"Hola, mundo DES en C!"
    #cifrado = des.desEncryptCBC(mensaje, des.KEY, iv)
    #claro   = des.desDecryptCBC(cifrado, des.KEY, iv)
    #assert claro == mensaje, "Fallo en round-trip CBC"
    #print(f"IV: {iv.hex()}")
    #print(f"Cifrado: {cifrado.hex()}")
    #print(f"Claro  : {claro.decode()}")
    #print("Round-trip CBC: OK")

    # Prueba de archivos (descomenta si tienes 'hola.txt')
    #des.encrypt_file("steam.dmg")
    # Uso
    #iv = des.reaad_iv_file("steam.dmg.enc")
    #iv_hex = iv.hex()   # guardas esto en tu BD: "a3f1c2d4e5f6a7b8"
    #des.set_key(bytes.fromhex("4a6f3135514a6257"))

    # Recuperas el iv_hex de tu BD y lo conviertes de nuevo a bytes
    #iv = bytes.fromhex(iv_hex)   # "a3f1c2d4e5f6a7b8" → b'\xa3\xf1...'

    #des.descifrar_archivo("documento.txt.enc")
    # El IV ya está dentro del .enc, descifrar_archivo lo lee solo
    #print(iv.hex())
    #des.decrypt_file("steam.dmg.enc")