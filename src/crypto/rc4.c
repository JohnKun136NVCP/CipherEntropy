// rc4.c
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "rc4.h"

#define RC4_STATE_SIZE 256

typedef struct {
    uint8_t S[RC4_STATE_SIZE];
    uint8_t i, j;
} RC4_CTX;

//  KSA
void rc4_init(RC4_CTX *ctx, const uint8_t *key, int keylen) {
    for (int i = 0; i < RC4_STATE_SIZE; i++)
        ctx->S[i] = (uint8_t)i;

    ctx->i = ctx->j = 0;

    uint8_t j = 0;
    for (int i = 0; i < RC4_STATE_SIZE; i++) {
        j = j + ctx->S[i] + key[i % keylen];

        // swap
        uint8_t tmp = ctx->S[i];
        ctx->S[i] = ctx->S[j];
        ctx->S[j] = tmp;
    }
}

// PRGA 
static inline void rc4_crypt(RC4_CTX *ctx, uint8_t *data, size_t len) {
    uint8_t i = ctx->i;
    uint8_t j = ctx->j;
    uint8_t *S = ctx->S;

    for (size_t k = 0; k < len; k++) {
        i++;
        j += S[i];

        uint8_t tmp = S[i];
        S[i] = S[j];
        S[j] = tmp;

        uint8_t rnd = S[(S[i] + S[j]) & 0xFF];
        data[k] ^= rnd;
    }

    ctx->i = i;
    ctx->j = j;
}
int rc4_process_file(const char *infile, const char *outfile,
                     const uint8_t *key, int keylen) {

    FILE *in = fopen(infile, "rb");
    FILE *out = fopen(outfile, "wb");

    if (!in || !out) return -1;

    RC4_CTX ctx;
    rc4_init(&ctx, key, keylen);

    uint8_t buffer[4096];

    size_t n;
    while ((n = fread(buffer, 1, sizeof(buffer), in)) > 0) {
        rc4_crypt(&ctx, buffer, n);
        fwrite(buffer, 1, n, out);
    }

    fclose(in);
    fclose(out);

    return 0;
}
EXPORT int rc4_file(const char *infile, const char *outfile,
                    const uint8_t *key, int keylen) {
    return rc4_process_file(infile, outfile, key, keylen);
}