#ifndef DES_TABLES_H
#define DES_TABLES_H

#include <stdint.h>

/* ─────────────────────────────────────────────────────────────────────────────
 * Standard DES permutation tables (declared extern; defined in des_tables.c)
 * ───────────────────────────────────────────────────────────────────────────── */

extern const uint8_t DES_IP[64];      /* Initial permutation           */
extern const uint8_t DES_FP[64];      /* Final permutation (IP^-1)     */
extern const uint8_t DES_E[48];       /* Expansion 32→48 bits          */
extern const uint8_t DES_P[32];       /* Permutation P (post S-box)    */
extern const uint8_t DES_PC1[56];     /* Permuted Choice 1 (64→56)     */
extern const uint8_t DES_PC2[48];     /* Permuted Choice 2 (56→48)     */
extern const uint8_t DES_KEY_SHIFT[16]; /* Round rotations              */

/* Original S-boxes [8 boxes][4 rows][16 columns] */
extern const uint8_t DES_SBOXES[8][4][16];

/* Precomputed S-box tables [8 boxes][64 entries] — index = 6 bits */
extern const uint8_t DES_SBOX_TABLES[8][64];

#endif /* DES_TABLES_H */