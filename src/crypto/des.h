#ifndef DES_H
#define DES_H

#include <stdint.h>
#include <stddef.h>

/* ─── Sizes ──────────────────────────────────────────────────────────────── */
#define DES_KEY_SIZE   8          /* bytes */
#define DES_BLOCK_SIZE 8          /* bytes */
#define DES_NUM_KEYS   16         /* Feistel subkeys */
#define DES_CHUNK_SIZE (8 * 1024) /* bytes for file encryption */

/* ─── Main context ───────────────────────────────────────────────────────── */
typedef struct {
    uint8_t  key[DES_KEY_SIZE];   /* stored key (from the randomness module) */
    int      key_set;             /* 1 if assigned, 0 otherwise */
    uint64_t subkeys[DES_NUM_KEYS];
} DES_CTX;

/* ─── Initialization ─────────────────────────────────────────────────────── */

/**
 * Initializes the DES context.
 * The key is assigned later with des_set_key() or des_rand_key().
 */
void des_init(DES_CTX *ctx);

/**
 * Manually assigns an 8-byte key to the context.
 * Derives the 16 subkeys immediately.
 */
void des_set_key(DES_CTX *ctx, const uint8_t key[DES_KEY_SIZE]);

/**
 * Generates a random key using the 'randomness' module (generateTokenCiphers).
 * Writes the key to ctx->key and also returns it in out_key (which may be NULL).
 * Returns 0 on success, -1 on error.
 */
int des_rand_key(DES_CTX *ctx, uint8_t out_key[DES_KEY_SIZE]);

/* ─── Buffer encryption / decryption (CBC) ───────────────────────────────── */

/**
 * Encrypts `len` bytes from `plain` in CBC mode with PKCS#7.
 *   iv       : 8-byte initialization vector.
 *   out_len  : receives the encrypted buffer size (multiple of 8).
 * Returns a buffer allocated with malloc(); the caller must free it.
 * Returns NULL on error.
 */
uint8_t *des_encrypt_cbc(DES_CTX *ctx,
                          const uint8_t *plain, size_t len,
                          const uint8_t iv[DES_BLOCK_SIZE],
                          size_t *out_len);

/**
 * Decrypts `len` bytes from `cipher` in CBC mode with PKCS#7.
 *   iv       : same IV used for encryption.
 *   out_len  : receives the resulting plaintext size.
 * Returns a buffer allocated with malloc(); the caller must free it.
 * Returns NULL on error.
 */
uint8_t *des_decrypt_cbc(DES_CTX *ctx,
                          const uint8_t *cipher, size_t len,
                          const uint8_t iv[DES_BLOCK_SIZE],
                          size_t *out_len);

/* ─── File encryption / decryption ───────────────────────────────────────── */

/**
 * Encrypts the file at `path` and writes `path.enc`.
 * The random IV is written to the first 8 bytes of the output file.
 * The original file is removed when finished.
 * Requires ctx->key_set == 1.
 * Returns 0 on success, -1 on error.
 */
int des_encrypt_file(DES_CTX *ctx, const char *path);

/**
 * Decrypts the file at `path` (it must end in ".enc") and restores the original.
 * The encrypted file is removed when finished.
 * Requires ctx->key_set == 1.
 * Returns 0 on success, -1 on error.
 */
int des_decrypt_file(DES_CTX *ctx, const char *path);

#endif /* DES_H */