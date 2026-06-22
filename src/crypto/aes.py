from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


def aes_encrypt_file(infile, outfile, key,iv):

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    with open(infile, "rb") as f:
        data = f.read()

    padder = padding.PKCS7(128).padder()
    padded = padder.update(data) + padder.finalize()

    enc = encryptor.update(padded) + encryptor.finalize()

    with open(outfile, "wb") as f:
        f.write(iv + enc)
def aes_decrypt_file(infile, outfile, key,iv):
    with open(infile, "rb") as f:
        data = f.read()

    ciphertext = data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()

    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()

    with open(outfile, "wb") as f:
        f.write(plaintext)

"""file = "hola.txt"
out = "hola.txt.aes"
iv = os.urandom(16)
key = generateTokenCiphers("AES")
print(key.hex())
print(iv.hex())
aes_encrypt_file(file,outfile=out,key=key,iv=iv)
with open("hola.txt.aes", "rb") as f:
    encrypted_data = f.read()

print(encrypted_data.hex())"""