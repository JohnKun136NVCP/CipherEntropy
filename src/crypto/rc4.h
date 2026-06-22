#ifndef RC4_H
#define RC4_H

#include <stdint.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

EXPORT int rc4_file(const char *infile, const char *outfile,
                     const uint8_t *key, int keylen);

#endif