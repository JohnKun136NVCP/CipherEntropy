from pathlib import Path
import csv


class Dataset:

    columns_experiment = [
        "experiment_id",
        "loop_id",
        "run_id",
        "algorithm",
        "file_name",
        "size_bytes",
        "entropy_raw",
        "entropy_encrypted",
        "entropy_delta",
        "encrypt_time_ms",
        "decrypt_time_ms",
        "sha256_raw",
        "sha256_encrypted"
    ]

    columns_keys = [
        "experiment_id",
        "algorithm",
        "key",
        "iv"
    ]

    def __init__(self):
        script_dir = Path(__file__).resolve().parent
        self.base_dir = script_dir.parent.parent

        self.global_csv = self.base_dir / "data/csv/global.csv"
        self.keys_csv = self.base_dir / "data/csv/keys.csv"

        self.global_csv.parent.mkdir(parents=True, exist_ok=True)

    def init_files(self):

        if not self.global_csv.exists():
            with open(self.global_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.columns_experiment)

        if not self.keys_csv.exists():
            with open(self.keys_csv, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.columns_keys)

    def append_experiment(self, row):

        with open(self.global_csv, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

    def append_key(self, row):

        with open(self.keys_csv, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)
