import pandas as pd
import numpy as np
from scipy.stats import ttest_rel


# =========================
# LOAD DATA
# =========================
df = pd.read_csv("data/global.csv")


# =========================
# BASIC STATS
# =========================
print("\n📊 ENTROPY STATS")
print("------------------")

print("Raw entropy mean:", df["entropy_raw"].mean())
print("Encrypted entropy mean:", df["entropy_encrypted"].mean())
print("Delta mean:", df["entropy_delta"].mean())


# =========================
# HYPOTHESIS TEST
# =========================
print("\n📈 T-TEST (paired)")
print("------------------")

t_stat, p_value = ttest_rel(
    df["entropy_raw"],
    df["entropy_encrypted"]
)

print("t-stat:", t_stat)
print("p-value:", p_value)


# =========================
# EFFECT SIZE (COHEN'S D)
# =========================
def cohens_d(x, y):
    diff = y - x
    return diff.mean() / diff.std()


d = cohens_d(df["entropy_raw"], df["entropy_encrypted"])

print("\n📌 Cohen's d:", d)


# =========================
# TIME ANALYSIS
# =========================
print("\n⏱️ PERFORMANCE")
print("------------------")

print("Encrypt avg (ms):", df["encrypt_time_ms"].mean())
print("Decrypt avg (ms):", df["decrypt_time_ms"].mean())


# =========================
# SIZE CORRELATION
# =========================
print("\n📦 SIZE vs ENTROPY DELTA")
print("------------------")

corr = np.corrcoef(df["size_bytes"], df["entropy_delta"])[0, 1]
print("Correlation:", corr)