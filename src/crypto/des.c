/*
 * des.c — Implementación DES-CBC en C
 *
 * La clave se conserva en DES_CTX.key para coincidir con el diseño Python
 * donde self.KEY vive en la instancia y puede asignarse una vez y reutilizarse.
 */

#define _GNU_SOURCE   /* necesario para getrandom() en Linux */

#include "des.h"
#include "des_tables.h"

#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <errno.h>

/* ─── Generación segura de bytes aleatorios ─────────────────────────────────
 * Orden de preferencia:
 *   1. BCryptGenRandom  (Windows)
 *   2. getrandom()      (Linux ≥ 3.17, glibc ≥ 2.25)
 *   3. /dev/urandom     (fallback POSIX universal)
 * ─────────────────────────────────────────────────────────────────────────── */
#ifdef _WIN32
#  include <windows.h>
#  include <bcrypt.h>
static int secure_random(void *buf, size_t n)
{
    return BCryptGenRandom(NULL, (PUCHAR)buf, (ULONG)n,
                           BCRYPT_USE_SYSTEM_PREFERRED_RNG) == 0 ? 0 : -1;
}
#elif defined(__linux__)
#  include <sys/syscall.h>
#  include <unistd.h>
static int secure_random(void *buf, size_t n)
{
    /* Intentar getrandom via syscall directo (evita problemas de declaración) */
    long r = syscall(SYS_getrandom, buf, n, 0);
    if (r == (long)n) return 0;
    /* Fallback: /dev/urandom */
    FILE *f = fopen("/dev/urandom", "rb");
    if (!f) return -1;
    size_t rd = fread(buf, 1, n, f);
    fclose(f);
    return rd == n ? 0 : -1;
}
#else
/* macOS / BSD / otros POSIX */
static int secure_random(void *buf, size_t n)
{
    FILE *f = fopen("/dev/urandom", "rb");
    if (!f) return -1;
    size_t rd = fread(buf, 1, n, f);
    fclose(f);
    return rd == n ? 0 : -1;
}
#endif

#define SECURE_RANDOM(buf, n) secure_random((buf), (n))

/* ═══════════════════════════════════════════════════════════════════════════
 * Primitivas internas
 * ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Permuta `block` (de `bits` bits) según `table`.
 * Equivalente Python: __permute()
 */
static uint64_t permute(uint64_t block, const uint8_t *table, int n, int bits)
{
    uint64_t result = 0;
    for (int i = 0; i < n; i++) {
        result = (result << 1) | ((block >> (bits - table[i])) & 1ULL);
    }
    return result;
}

/**
 * Rotación izquierda de `val` con `size` bits efectivos.
 * Equivalente Python: __leftRotate()
 */
static uint32_t left_rotate28(uint32_t val, int shift)
{
    return ((val << shift) & 0x0FFFFFFFU) | (val >> (28 - shift));
}

/**
 * Sustitución S-Box sobre los 48 bits de entrada.
 * Equivalente Python: __sboxSustitution()
 */
static uint32_t sbox_substitution(uint64_t block)
{
    uint32_t result = 0;
    for (int i = 0; i < 8; i++) {
        uint8_t chunk = (block >> (42 - 6 * i)) & 0x3F;
        result = (result << 4) | DES_SBOX_TABLES[i][chunk];
    }
    return result;
}

/* ═══════════════════════════════════════════════════════════════════════════
 * Generación de subclaves
 * ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Deriva las 16 subclaves a partir de key_bytes[8].
 * Equivalente Python: __generateKeys()
 */
static void generate_keys(const uint8_t key_bytes[DES_KEY_SIZE],
                           uint64_t subkeys[DES_NUM_KEYS])
{
    /* Convertir key a entero de 64 bits big-endian */
    uint64_t key = 0;
    for (int i = 0; i < 8; i++)
        key = (key << 8) | key_bytes[i];

    key = permute(key, DES_PC1, 56, 64);

    uint32_t left  = (key >> 28) & 0x0FFFFFFFU;
    uint32_t right =  key        & 0x0FFFFFFFU;

    for (int r = 0; r < DES_NUM_KEYS; r++) {
        left  = left_rotate28(left,  DES_KEY_SHIFT[r]);
        right = left_rotate28(right, DES_KEY_SHIFT[r]);
        uint64_t combined = ((uint64_t)left << 28) | right;
        subkeys[r] = permute(combined, DES_PC2, 48, 56);
    }
}

/* ═══════════════════════════════════════════════════════════════════════════
 * Bloque DES (Feistel, 16 rondas)
 * ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Cifra o descifra un bloque de 64 bits.
 * Para descifrar, pasa las subclaves en orden inverso.
 * Equivalente Python: __des_block()
 */
static uint64_t des_block(uint64_t block, const uint64_t keys[DES_NUM_KEYS])
{
    block = permute(block, DES_IP, 64, 64);

    uint32_t left  = (block >> 32) & 0xFFFFFFFFU;
    uint32_t right =  block        & 0xFFFFFFFFU;

    for (int r = 0; r < DES_NUM_KEYS; r++) {
        uint32_t tmp = right;
        uint64_t expanded = permute((uint64_t)right, DES_E, 48, 32);
        expanded ^= keys[r];
        uint32_t substituted = sbox_substitution(expanded);
        uint32_t permuted    = (uint32_t)permute((uint64_t)substituted, DES_P, 32, 32);
        right = permuted ^ left;
        left  = tmp;
    }

    uint64_t combined = ((uint64_t)right << 32) | left;
    return permute(combined, DES_FP, 64, 64);
}

/* ═══════════════════════════════════════════════════════════════════════════
 * PKCS#7 para bloques de 8 bytes
 * ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Rellena `data` con PKCS#7 hasta múltiplo de 8.
 * Devuelve nuevo buffer (malloc); escribe tamaño en *out_len.
 */
static uint8_t *pkcs7_pad(const uint8_t *data, size_t len, size_t *out_len)
{
    size_t pad_len = 8 - (len % 8);   /* 1–8 */
    *out_len = len + pad_len;
    uint8_t *buf = malloc(*out_len);
    if (!buf) return NULL;
    memcpy(buf, data, len);
    memset(buf + len, (uint8_t)pad_len, pad_len);
    return buf;
}

/**
 * Elimina relleno PKCS#7.
 * Escribe tamaño real en *out_len. Retorna 0 si OK, -1 si padding inválido.
 */
static int pkcs7_unpad(const uint8_t *data, size_t len, size_t *out_len)
{
    if (len == 0 || len % 8 != 0) return -1;
    uint8_t pad_len = data[len - 1];
    if (pad_len < 1 || pad_len > 8) return -1;
    for (size_t i = len - pad_len; i < len; i++)
        if (data[i] != pad_len) return -1;
    *out_len = len - pad_len;
    return 0;
}

/* ═══════════════════════════════════════════════════════════════════════════
 * API pública
 * ═══════════════════════════════════════════════════════════════════════════ */

void des_init(DES_CTX *ctx)
{
    memset(ctx, 0, sizeof(*ctx));
}

void des_set_key(DES_CTX *ctx, const uint8_t key[DES_KEY_SIZE])
{
    memcpy(ctx->key, key, DES_KEY_SIZE);
    ctx->key_set = 1;
    generate_keys(ctx->key, ctx->subkeys);
}

/*
 * des_rand_key — genera clave segura.
 *
 * Estrategia para conservar la clave del módulo Python 'randomness':
 *   1. Se intenta llamar: python3 -c "from randomness import generateTokenCiphers;
 *      import sys; sys.stdout.buffer.write(generateTokenCiphers('DES'))"
 *   2. Si falla (Python no disponible o módulo no instalado), se recurre a
 *      getrandom() / BCryptGenRandom() como fallback seguro.
 */
int des_rand_key(DES_CTX *ctx, uint8_t out_key[DES_KEY_SIZE])
{
    uint8_t key[DES_KEY_SIZE];
    int ok = 0;

    /* ── Intento 1: módulo Python randomness ── */
    FILE *fp = popen(
        "python3 -c \""
        "from randomness import generateTokenCiphers; "
        "import sys; sys.stdout.buffer.write(generateTokenCiphers('DES'))\"",
        "r");
    if (fp) {
        size_t n = fread(key, 1, DES_KEY_SIZE, fp);
        int rc = pclose(fp);
        if (n == DES_KEY_SIZE && rc == 0)
            ok = 1;
    }

    /* ── Fallback: CSPRNG del sistema ── */
    if (!ok) {
        if (SECURE_RANDOM(key, DES_KEY_SIZE) < 0) {
            perror("des_rand_key: SECURE_RANDOM");
            return -1;
        }
    }

    des_set_key(ctx, key);
    if (out_key) memcpy(out_key, key, DES_KEY_SIZE);
    return 0;
}

/* ─── Cifrado CBC ─────────────────────────────────────────────────────────── */

uint8_t *des_encrypt_cbc(DES_CTX *ctx,
                          const uint8_t *plain, size_t len,
                          const uint8_t iv[DES_BLOCK_SIZE],
                          size_t *out_len)
{
    /* Rellenar */
    size_t padded_len;
    uint8_t *padded = pkcs7_pad(plain, len, &padded_len);
    if (!padded) return NULL;

    uint8_t *result = malloc(padded_len);
    if (!result) { free(padded); return NULL; }

    uint8_t previous[DES_BLOCK_SIZE];
    memcpy(previous, iv, DES_BLOCK_SIZE);

    for (size_t i = 0; i < padded_len; i += 8) {
        /* XOR con bloque anterior (CBC) */
        uint64_t block_int = 0;
        for (int b = 0; b < 8; b++)
            block_int = (block_int << 8) | padded[i + b];

        uint64_t prev_int = 0;
        for (int b = 0; b < 8; b++)
            prev_int = (prev_int << 8) | previous[b];

        block_int ^= prev_int;
        uint64_t enc = des_block(block_int, ctx->subkeys);

        for (int b = 7; b >= 0; b--) {
            result[i + b] = enc & 0xFF;
            previous[b]   = enc & 0xFF;
            enc >>= 8;
        }
    }

    free(padded);
    *out_len = padded_len;
    return result;
}

/* ─── Descifrado CBC ──────────────────────────────────────────────────────── */

uint8_t *des_decrypt_cbc(DES_CTX *ctx,
                          const uint8_t *cipher, size_t len,
                          const uint8_t iv[DES_BLOCK_SIZE],
                          size_t *out_len)
{
    if (len == 0 || len % 8 != 0) return NULL;

    /* Subclaves inversas para descifrar */
    uint64_t rev_keys[DES_NUM_KEYS];
    for (int i = 0; i < DES_NUM_KEYS; i++)
        rev_keys[i] = ctx->subkeys[DES_NUM_KEYS - 1 - i];

    uint8_t *result = malloc(len);
    if (!result) return NULL;

    uint8_t previous[DES_BLOCK_SIZE];
    memcpy(previous, iv, DES_BLOCK_SIZE);

    for (size_t i = 0; i < len; i += 8) {
        uint64_t block_int = 0;
        for (int b = 0; b < 8; b++)
            block_int = (block_int << 8) | cipher[i + b];

        uint64_t dec = des_block(block_int, rev_keys);

        uint64_t prev_int = 0;
        for (int b = 0; b < 8; b++)
            prev_int = (prev_int << 8) | previous[b];

        uint64_t plain_int = dec ^ prev_int;

        for (int b = 7; b >= 0; b--) {
            result[i + b] = plain_int & 0xFF;
            plain_int >>= 8;
        }
        memcpy(previous, cipher + i, 8);
    }

    size_t real_len;
    if (pkcs7_unpad(result, len, &real_len) != 0) {
        free(result);
        return NULL;
    }
    *out_len = real_len;
    return result;   /* llamador debe hacer realloc o simplemente usar real_len */
}

/* ─── Cifrado de archivos ─────────────────────────────────────────────────── */

int des_encrypt_file(DES_CTX *ctx, const char *path)
{
    if (!ctx->key_set) {
        fprintf(stderr, "des_encrypt_file: clave no asignada. Llame des_set_key() o des_rand_key().\n");
        return -1;
    }

    /* Ruta de salida: path + ".enc" */
    size_t plen = strlen(path);
    char *out_path = malloc(plen + 5);
    if (!out_path) return -1;
    sprintf(out_path, "%s.enc", path);

    FILE *f_in  = fopen(path,     "rb");
    FILE *f_out = fopen(out_path, "wb");
    if (!f_in || !f_out) {
        perror("des_encrypt_file: fopen");
        if (f_in)  fclose(f_in);
        if (f_out) fclose(f_out);
        free(out_path);
        return -1;
    }

    /* IV aleatorio */
    uint8_t iv[DES_BLOCK_SIZE];
    if (SECURE_RANDOM(iv, DES_BLOCK_SIZE) < 0) {
        perror("des_encrypt_file: IV");
        fclose(f_in); fclose(f_out); free(out_path);
        return -1;
    }
    fwrite(iv, 1, DES_BLOCK_SIZE, f_out);

    /* Tamaño del archivo para saber cuándo es el último chunk */
    fseek(f_in, 0, SEEK_END);
    long file_size = ftell(f_in);
    rewind(f_in);

    uint8_t previous[DES_BLOCK_SIZE];
    memcpy(previous, iv, DES_BLOCK_SIZE);

    uint8_t chunk[DES_CHUNK_SIZE];
    long bytes_read = 0;
    int  ret = 0;

    while (1) {
        size_t n = fread(chunk, 1, DES_CHUNK_SIZE, f_in);
        if (n == 0) break;
        bytes_read += (long)n;
        int is_last = (bytes_read == file_size);

        /* PKCS#7 solo en el último chunk */
        size_t proc_len = n;
        uint8_t *proc = chunk;
        uint8_t *padded = NULL;
        if (is_last) {
            size_t padded_len;
            padded = pkcs7_pad(chunk, n, &padded_len);
            if (!padded) { ret = -1; break; }
            proc     = padded;
            proc_len = padded_len;
        }

        for (size_t i = 0; i < proc_len; i += 8) {
            uint64_t block_int = 0;
            for (int b = 0; b < 8; b++)
                block_int = (block_int << 8) | proc[i + b];

            uint64_t prev_int = 0;
            for (int b = 0; b < 8; b++)
                prev_int = (prev_int << 8) | previous[b];

            block_int ^= prev_int;
            uint64_t enc = des_block(block_int, ctx->subkeys);

            uint8_t enc_bytes[8];
            for (int b = 7; b >= 0; b--) {
                enc_bytes[b] = enc & 0xFF;
                enc >>= 8;
            }
            fwrite(enc_bytes, 1, 8, f_out);
            memcpy(previous, enc_bytes, 8);
        }
        free(padded);
    }

    fclose(f_in);
    fclose(f_out);

    if (ret == 0)
        remove(path);
    else
        remove(out_path);

    free(out_path);
    return ret;
}

/* ─── Descifrado de archivos ──────────────────────────────────────────────── */

int des_decrypt_file(DES_CTX *ctx, const char *path)
{
    if (!ctx->key_set) {
        fprintf(stderr, "des_decrypt_file: clave no asignada.\n");
        return -1;
    }

    /* Ruta de salida: quitar ".enc" */
    size_t plen = strlen(path);
    char *out_path;
    if (plen > 4 && strcmp(path + plen - 4, ".enc") == 0) {
        out_path = malloc(plen - 3);
        if (!out_path) return -1;
        memcpy(out_path, path, plen - 4);
        out_path[plen - 4] = '\0';
    } else {
        out_path = malloc(plen + 5);
        if (!out_path) return -1;
        sprintf(out_path, "%s.dec", path);
    }

    FILE *f_in  = fopen(path,     "rb");
    FILE *f_out = fopen(out_path, "wb");
    if (!f_in || !f_out) {
        perror("des_decrypt_file: fopen");
        if (f_in)  fclose(f_in);
        if (f_out) fclose(f_out);
        free(out_path);
        return -1;
    }

    /* Leer IV */
    uint8_t iv[DES_BLOCK_SIZE];
    if (fread(iv, 1, DES_BLOCK_SIZE, f_in) != DES_BLOCK_SIZE) {
        fprintf(stderr, "des_decrypt_file: archivo demasiado pequeño\n");
        fclose(f_in); fclose(f_out); free(out_path);
        return -1;
    }

    /* Leer todo el cifrado en memoria */
    fseek(f_in, 0, SEEK_END);
    long total = ftell(f_in);
    fseek(f_in, DES_BLOCK_SIZE, SEEK_SET);
    long cipher_len = total - DES_BLOCK_SIZE;

    if (cipher_len <= 0 || cipher_len % 8 != 0) {
        fprintf(stderr, "des_decrypt_file: longitud de cifrado inválida\n");
        fclose(f_in); fclose(f_out); free(out_path);
        return -1;
    }

    uint8_t *cipher_data = malloc((size_t)cipher_len);
    if (!cipher_data) { fclose(f_in); fclose(f_out); free(out_path); return -1; }
    fread(cipher_data, 1, (size_t)cipher_len, f_in);
    fclose(f_in);

    /* Subclaves inversas */
    uint64_t rev_keys[DES_NUM_KEYS];
    for (int i = 0; i < DES_NUM_KEYS; i++)
        rev_keys[i] = ctx->subkeys[DES_NUM_KEYS - 1 - i];

    uint8_t *plaintext = malloc((size_t)cipher_len);
    if (!plaintext) {
        free(cipher_data); fclose(f_out); free(out_path);
        return -1;
    }

    uint8_t previous[DES_BLOCK_SIZE];
    memcpy(previous, iv, DES_BLOCK_SIZE);

    for (long i = 0; i < cipher_len; i += 8) {
        uint64_t block_int = 0;
        for (int b = 0; b < 8; b++)
            block_int = (block_int << 8) | cipher_data[i + b];

        uint64_t dec = des_block(block_int, rev_keys);

        uint64_t prev_int = 0;
        for (int b = 0; b < 8; b++)
            prev_int = (prev_int << 8) | previous[b];

        uint64_t plain_int = dec ^ prev_int;
        for (int b = 7; b >= 0; b--) {
            plaintext[i + b] = plain_int & 0xFF;
            plain_int >>= 8;
        }
        memcpy(previous, cipher_data + i, 8);
    }
    free(cipher_data);

    size_t real_len;
    int ret = pkcs7_unpad(plaintext, (size_t)cipher_len, &real_len);
    if (ret != 0) {
        fprintf(stderr, "des_decrypt_file: padding inválido\n");
        free(plaintext); fclose(f_out); free(out_path);
        return -1;
    }

    fwrite(plaintext, 1, real_len, f_out);
    free(plaintext);
    fclose(f_out);

    remove(path);
    free(out_path);
    return 0;
}