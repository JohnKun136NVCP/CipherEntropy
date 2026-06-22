# Modules
from cli import main

if __name__ == "__main__":
    main()












"""from pathlib import Path
from collections import Counter
from math import log2

import pandas as pd
import matplotlib.pyplot as plt

# ============================================

# CONFIGURACIÓN

# ============================================

ORIGINAL_DIR = "data/original"

ALGORITHMS = [
"AES256",
"DES",
"RC4"
]

ENCRYPTED_DIR = "data/encrypted"
DECRYPTED_DIR = "data/decrypted"

DATABASE_DIR = "database"
GRAPH_DIR = "graphs"

EXPERIMENTS_CSV = f"{DATABASE_DIR}/experiments.csv"
GLOBAL_STATS_CSV = f"{DATABASE_DIR}/global_statistics.csv"

# ============================================

# ENTROPÍA

# ============================================

def shannon_entropy(data: bytes):


if len(data) == 0:
    return 0

freq = Counter(data)

total = len(data)

entropy = 0

for count in freq.values():

    p = count / total

    entropy -= p * log2(p)

return entropy


# ============================================

# LECTURA DE ARCHIVOS

# ============================================

def read_file(path):


with open(path, "rb") as f:

    return f.read()


def size_mb(path):


return Path(path).stat().st_size / (1024 * 1024)


# ============================================

# EXPERIMENTOS

# ============================================

def generate_experiments():


rows = []

experiment_id = 1

originals = Path(
    ORIGINAL_DIR
)

for algorithm in ALGORITHMS:

    encrypted_folder = Path(
        ENCRYPTED_DIR
    ) / algorithm

    decrypted_folder = Path(
        DECRYPTED_DIR
    ) / algorithm

    for round_number, file in enumerate(
        originals.iterdir(),
        start=1
    ):

        if not file.is_file():
            continue

        original_file = file

        encrypted_file = (
            encrypted_folder /
            file.name
        )

        decrypted_file = (
            decrypted_folder /
            file.name
        )

        if (
            not encrypted_file.exists()
            or
            not decrypted_file.exists()
        ):
            continue

        original_data = read_file(
            original_file
        )

        encrypted_data = read_file(
            encrypted_file
        )

        decrypted_data = read_file(
            decrypted_file
        )

        rows.append({

            "id":
                experiment_id,

            "algorithm":
                algorithm,

            "round":
                round_number,

            "file_name":
                file.name,

            "size_mb":
                size_mb(
                    original_file
                ),

            "entropy_original":
                shannon_entropy(
                    original_data
                ),

            "entropy_encrypted":
                shannon_entropy(
                    encrypted_data
                ),

            "entropy_decrypted":
                shannon_entropy(
                    decrypted_data
                )
        })

        experiment_id += 1

df = pd.DataFrame(rows)

df.to_csv(
    EXPERIMENTS_CSV,
    index=False
)

return df
```

# ============================================

# ESTADÍSTICAS

# ============================================

def generate_statistics(df):

```
statistics = []

for algorithm in df[
    "algorithm"
].unique():

    subset = df[
        df["algorithm"] == algorithm
    ]

    statistics.append({

        "algorithm":
            algorithm,

        "tests":
            len(subset),

        "avg_original":
            subset[
                "entropy_original"
            ].mean(),

        "avg_encrypted":
            subset[
                "entropy_encrypted"
            ].mean(),

        "avg_decrypted":
            subset[
                "entropy_decrypted"
            ].mean(),

        "min_entropy":
            subset[
                "entropy_encrypted"
            ].min(),

        "max_entropy":
            subset[
                "entropy_encrypted"
            ].max(),

        "std_entropy":
            subset[
                "entropy_encrypted"
            ].std()
    })

    subset.to_csv(

        f"{DATABASE_DIR}/"
        f"{algorithm}_full.csv",

        index=False
    )

stats_df = pd.DataFrame(
    statistics
)

stats_df.to_csv(
    GLOBAL_STATS_CSV,
    index=False
)

return stats_df
```

# ============================================

# GRÁFICAS

# ============================================

def graph_comparison(stats_df):

```
plt.figure(
    figsize=(10, 6)
)

plt.bar(
    stats_df["algorithm"],
    stats_df["avg_encrypted"]
)

plt.title(
    "Entropía Promedio"
)

plt.ylabel(
    "Entropía"
)

plt.savefig(
    f"{GRAPH_DIR}/entropy_comparison.png"
)

plt.close()
```

def graph_boxplot(df):

```
groups = []

labels = []

for algorithm in df[
    "algorithm"
].unique():

    groups.append(

        df[
            df["algorithm"]
            ==
            algorithm
        ][
            "entropy_encrypted"
        ]
    )

    labels.append(
        algorithm
    )

plt.figure(
    figsize=(10, 6)
)

plt.boxplot(
    groups,
    labels=labels
)

plt.title(
    "Distribución Entropía"
)

plt.savefig(
    f"{GRAPH_DIR}/boxplot_algorithms.png"
)

plt.close()
```

# ============================================

# MAIN

# ============================================

def main():

```
Path(
    DATABASE_DIR
).mkdir(
    exist_ok=True
)

Path(
    GRAPH_DIR
).mkdir(
    exist_ok=True
)

experiments = (
    generate_experiments()
)

statistics = (
    generate_statistics(
        experiments
    )
)

graph_comparison(
    statistics
)

graph_boxplot(
    experiments
)

print(
    "Proceso completado."
)
```

if **name** == "**main**":

```
main()
```
"""