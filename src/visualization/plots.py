from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from statannotations.Annotator import Annotator
from scipy.stats import wilcoxon
from scipy.stats import mannwhitneyu
from itertools import combinations
from scipy.stats import kruskal
import numpy as np

sns.set_theme(style="whitegrid")

class PlotGenerator:

    def __init__(self, csv_file, output_dir):

        self.csv_file = Path(csv_file)
        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.df = pd.read_csv(self.csv_file)


        self.pdf = self.df.copy()
       
    def entropy_histogram(self):
        plt.figure(figsize=(10, 6))
        ax = sns.histplot(
            self.pdf["entropy_raw"],
            color="#2c7bb6",      # steelblue-like from colorblind palette
            kde=True,
            label="Original",
            alpha=0.6,
            stat="density"
        )
        sns.histplot(
            self.pdf["entropy_encrypted"],
            color="#d7191c",      # crimson-like
            kde=True,
            label="Encrypted",
            alpha=0.6,
            stat="density"
        )
        plt.axvline(8.0, color='black', linestyle='--', linewidth=1.2,
                    label='Theoretical max (8 bits)')
        # Add mean lines
        mean_enc = self.pdf["entropy_encrypted"].mean()
        plt.axvline(mean_enc, color='#d7191c', linestyle=':', linewidth=1.5,
                    label=f'Mean encrypted = {mean_enc:.3f}')
    
        plt.title("Entropy Distribution: Original vs Encrypted Data")
        plt.xlabel("Shannon Entropy (bits per byte)")
        plt.ylabel("Probability Density")
        plt.legend(frameon=True, loc='upper left')
        plt.tight_layout()
        plt.savefig(self.output_dir / "entropy_histogram.png", dpi=300)
        plt.savefig(self.output_dir / "entropy_histogram.pdf")
        plt.close()
    def entropy_delta(self):

        plt.figure(figsize=(10, 6))

        sns.histplot(
            data=self.pdf,
            x="entropy_delta",
            kde=True,
            bins=30
        )

        plt.title("Entropy Gain")

        plt.tight_layout()

        plt.savefig(
            self.output_dir /
            "entropy_delta.png",
            dpi=300
        )

        plt.close()
    def encryption_times(self):

        plt.figure(figsize=(8, 6))

        sns.boxplot(
            data=self.pdf,
            x="algorithm",
            y="encrypt_time_ms"
        )

        plt.title(
            "Encryption Time Comparison"
        )

        plt.tight_layout()

        plt.savefig(
            self.output_dir /
            "encryption_time.png",
            dpi=300
        )

        plt.close()
    def decryption_times(self):

        plt.figure(figsize=(8, 6))

        sns.boxplot(
            data=self.pdf,
            x="algorithm",
            y="decrypt_time_ms"
        )

        plt.title(
            "Decryption Time Comparison"
        )

        plt.tight_layout()

        plt.savefig(
            self.output_dir /
            "decryption_time.png",
            dpi=300
        )

        plt.close()
    def entropy_scatter(self):

        plt.figure(figsize=(10, 6))

        sns.scatterplot(
            data=self.pdf,
            x="entropy_raw",
            y="entropy_encrypted",

        )

        plt.title(
            "Original vs Encrypted Entropy"
        )

        plt.tight_layout()

        plt.savefig(
            self.output_dir /
            "entropy_scatter.png",
            dpi=300
        )

        plt.close()
    def descriptive_statistics(self):

        stats = (
            self.df
            .groupby("algorithm")
            .agg(
                mean_raw=("entropy_raw", "mean"),
                mean_encrypted=("entropy_encrypted", "mean"),
                std_encrypted=("entropy_encrypted", "std"),
                mean_encrypt_ms=("encrypt_time_ms", "mean"),
                mean_decrypt_ms=("decrypt_time_ms", "mean")
            )
            .reset_index()
        )

        stats.to_csv(
            self.output_dir /
            "descriptive_statistics.csv",
            index=False
        )

        return stats

    def wilcoxon_test(self):

        stat, pvalue = wilcoxon(
            self.pdf["entropy_raw"],
            self.pdf["entropy_encrypted"]
        )

        with open(
            self.output_dir /
            "wilcoxon.txt",
            "w"
        ) as f:

            f.write(
                f"Statistic: {stat}\n"
            )

            f.write(
                f"P-value: {pvalue}\n"
            )

            if pvalue < 0.05:

                f.write(
                    "\nResult:\n"
                    "Reject H0.\n"
                    "Entropy changed significantly."
                )

            else:

                f.write(
                    "\nResult:\n"
                    "Fail to reject H0."
                )

        return stat, pvalue
    def theoretical_vs_experimental(self):

        df = self.pdf.copy()

        df["theoretical_entropy"] = 8.0

        plt.figure(figsize=(10, 6))

        sns.lineplot(
            data=df,
            x="run_id",
            y="entropy_encrypted",
            label="Experimental"
        )

        plt.axhline(
            8.0,
            color="black",
            linestyle="--",
            label="Theoretical (Ideal Cipher)"
        )

        plt.title("Theoretical vs Experimental Entropy")
        plt.legend()

        plt.tight_layout()

        plt.savefig(
            self.output_dir / "theory_vs_experiment.png",
            dpi=300
        )

        plt.close()
    def entropy_error(self):

        df = self.pdf.copy()

        df["error"] = 8.0 - df["entropy_encrypted"]

        plt.figure(figsize=(10, 6))

        sns.boxplot(
            data=df,
            x="algorithm",
            y="error"
        )

        plt.title("Deviation from Theoretical Entropy (8 bits)")

        plt.tight_layout()

        plt.savefig(
            self.output_dir / "entropy_error.png",
            dpi=300
        )

        plt.close()
    def closeness_histogram(self):

        df = self.pdf.copy()

        df["closeness"] = df["entropy_encrypted"] / 8.0

        plt.figure(figsize=(10, 6))

        sns.histplot(
            data=df,
            x="closeness",
            kde=True
        )

        plt.title("Closeness to Ideal Entropy (1.0 = perfect)")

        plt.tight_layout()

        plt.savefig(
            self.output_dir / "closeness_hist.png",
            dpi=300
        )

        plt.close()
    def scatter_theory(self):

        df = self.pdf.copy()

        df["theoretical"] = 8.0

        plt.figure(figsize=(8, 6))

        sns.scatterplot(
            data=df,
            x="entropy_encrypted",
            y="theoretical",
        )

        plt.axvline(8.0, linestyle="--", color="black")

        plt.title("Experimental vs Theoretical Entropy")

        plt.tight_layout()

        plt.savefig(
            self.output_dir / "scatter_theory.png",
            dpi=300
        )

        plt.close()
    def mean_error_by_algorithm(self):

        df = self.pdf.copy()

        
        df["error"] = 8.0 - df["entropy_encrypted"]

        plt.figure(figsize=(8, 6))

        sns.barplot(
            data=df,
            x="algorithm",
            y="error",
            estimator="mean",
            errorbar="sd"   
        )

        plt.title("Mean Deviation from Theoretical Entropy (8 bits)")
        plt.ylabel("Entropy Error (bits)")
        plt.xlabel("Algorithm")

        plt.tight_layout()

        plt.savefig(
            self.output_dir / "mean_error.png",
            dpi=300
        )

        plt.close()
   

    def entropy_boxplot(self):
        """Boxplot with automatic pairwise comparisons."""
        plt.figure(figsize=(8, 6))
        
        # Fix: Assign x to hue and set legend=False
        ax = sns.boxplot(
            data=self.pdf, 
            x="algorithm", 
            y="entropy_encrypted",
            color="black",        # Add this
            palette="colorblind",
            legend=False            # Add this
        )
        
        # Add stripplot for individual data points
        sns.stripplot(
            data=self.pdf, 
            x="algorithm", 
            y="entropy_encrypted",        # Add this
            palette="colorblind",
            legend=False,           # Add this
            color="black",          # Remove this - conflicts with hue
            size=3, 
            alpha=0.3,
            dodge=False             # Add this to align with boxplot
        )
        
        # Automatically generate all possible pairs from data
        from itertools import combinations
        algorithms = sorted(self.pdf["algorithm"].unique())
        pairs = list(combinations(algorithms, 2))
        
        try:
            from statannotations.Annotator import Annotator
            annotator = Annotator(
                ax, pairs, data=self.pdf, 
                x="algorithm", y="entropy_encrypted"
            )
            annotator.configure(
                test="Mann-Whitney", 
                text_format="star", 
                loc="inside",
                comparisons_correction="bonferroni"
            )
            annotator.apply_and_annotate()
        except ImportError:
            print("statannotations not available. Skipping significance annotations.")
    
        plt.title("Encrypted Entropy by Algorithm with Pairwise Significance")
        plt.ylabel("Entropy (bits per byte)")
        plt.tight_layout()
        plt.savefig(self.output_dir / "entropy_boxplot.png", dpi=300)
        plt.savefig(self.output_dir / "entropy_boxplot.pdf")
        plt.close()
    def entropy_ecdf(self):
        """Empirical cumulative distribution of encrypted entropy."""
        plt.figure(figsize=(8, 6))
        sns.ecdfplot(data=self.pdf, x="entropy_encrypted")
        plt.axvline(8.0, color='black', linestyle='--', linewidth=1.2,
                    label='Ideal cipher (8 bits)')
        plt.title("ECDF of Encrypted Entropy by Algorithm")
        plt.xlabel("Entropy (bits per byte)")
        plt.ylabel("Cumulative Probability")
        plt.legend(title="Algorithm")
        plt.tight_layout()
        plt.savefig(self.output_dir / "entropy_ecdf.png", dpi=300)
        plt.savefig(self.output_dir / "entropy_ecdf.pdf")
        plt.close()
    def entropy_violin_advanced(self):
        plt.figure(figsize=(8, 6))
        sns.violinplot(
            data=self.pdf, x="algorithm", y="entropy_encrypted",
            inner="box", palette="colorblind", linewidth=1.2
        )
        plt.title("Entropy Density by Algorithm (with quartiles)")
        plt.xlabel("Algorithm")
        plt.ylabel("Entropy (bits per byte)")
        plt.tight_layout()
        plt.savefig(self.output_dir / "entropy_violin_adv.png", dpi=300)
        plt.savefig(self.output_dir / "entropy_violin_adv.pdf")
        plt.close()

    def pairwise_entropy_heatmap(self):
        """Heatmap of Mann-Whitney p-values between algorithms for encrypted entropy."""
        algorithms = self.pdf["algorithm"].unique()
        n = len(algorithms)
        p_matrix = np.zeros((n, n))
        for i, alg1 in enumerate(algorithms):
            for j, alg2 in enumerate(algorithms):
                if i == j:
                    p_matrix[i, j] = 1.0
                else:
                    data1 = self.pdf[self.pdf["algorithm"] == alg1]["entropy_encrypted"]
                    data2 = self.pdf[self.pdf["algorithm"] == alg2]["entropy_encrypted"]
                    _, p = mannwhitneyu(data1, data2, alternative="two-sided")
                    p_matrix[i, j] = p
        # Apply Bonferroni correction only to off-diagonal
        mask = ~np.eye(n, dtype=bool)
        p_matrix[mask] = np.minimum(p_matrix[mask] * (n*(n-1)/2), 1.0)
        
        plt.figure(figsize=(7, 6))
        sns.heatmap(
            p_matrix, annot=True, fmt=".1e", xticklabels=algorithms,
            yticklabels=algorithms, cmap="mako_r", vmin=0, vmax=0.05,
            linewidths=0.5, cbar_kws={"label": "Corrected p-value"}
        )
        plt.title("Pairwise Comparison of Encrypted Entropy (Bonferroni corrected)")
        plt.tight_layout()
        plt.savefig(self.output_dir / "pairwise_entropy_heatmap.png", dpi=300)
        plt.savefig(self.output_dir / "pairwise_entropy_heatmap.pdf")
        plt.close()
    def time_vs_entropy_scatter(self):
        """Show relationship between encryption time and achieved entropy."""
        plt.figure(figsize=(8, 6))
        # Compute mean per algorithm for clearer visualization
        summary = self.pdf.groupby("algorithm").agg(
            mean_entropy=("entropy_encrypted", "mean"),
            mean_time=("encrypt_time_ms", "mean")
        ).reset_index()
        sns.scatterplot(
            data=summary, x="mean_time", y="mean_entropy",
             style="algorithm", s=100
        )
        plt.axhline(8.0, color='gray', linestyle='--', label='Theoretical maximum')
        plt.title("Encryption Time vs Mean Entropy per Algorithm")
        plt.xlabel("Mean Encryption Time (ms)")
        plt.ylabel("Mean Encrypted Entropy (bits)")
        plt.legend(title="Algorithm")
        plt.tight_layout()
        plt.savefig(self.output_dir / "time_vs_entropy.png", dpi=300)
        plt.savefig(self.output_dir / "time_vs_entropy.pdf")
        plt.close()
    def combined_dashboard(self):
        """Four-panel summary figure."""
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        # Histogram
        sns.histplot(self.pdf["entropy_raw"], kde=True, color="#2c7bb6", label="Original", ax=axes[0,0], alpha=0.5)
        sns.histplot(self.pdf["entropy_encrypted"], kde=True, color="#d7191c", label="Encrypted", ax=axes[0,0], alpha=0.5)
        axes[0,0].axvline(8, ls='--', color='black')
        axes[0,0].set_title("Entropy Distribution")
        axes[0,0].legend()
        # Boxplot
        sns.boxplot(data=self.pdf, x="algorithm", y="entropy_encrypted", ax=axes[0,1])
        axes[0,1].set_title("Encrypted Entropy by Algorithm")
        # ECDF
        sns.ecdfplot(data=self.pdf, x="entropy_encrypted", ax=axes[1,0])
        axes[1,0].axvline(8, ls='--', color='black')
        axes[1,0].set_title("Cumulative Distribution (ECDF)")
        # Error barplot
        df_err = self.pdf.copy()
        df_err["error"] = 8.0 - df_err["entropy_encrypted"]
        sns.barplot(data=df_err, x="algorithm", y="error", estimator="mean", errorbar="sd", ax=axes[1,1])
        axes[1,1].set_title("Mean Deviation from 8 bits (error bars = SD)")
        axes[1,1].set_ylabel("Error (bits)")
        
        plt.suptitle("Entropy Analysis Summary", fontsize=16, y=1.02)
        plt.tight_layout()
        plt.savefig(self.output_dir / "entropy_dashboard.png", dpi=300)
        plt.savefig(self.output_dir / "entropy_dashboard.pdf")
        plt.close()
    def wilcoxon_per_algorithm(self):
        """Paired Wilcoxon test for each algorithm and effect size."""
        algorithms = self.pdf["algorithm"].unique()
        results = []
        for alg in algorithms:
            subset = self.pdf[self.pdf["algorithm"] == alg]
            stat, p = wilcoxon(subset["entropy_raw"], subset["entropy_encrypted"])
            # Effect size: rank-biserial correlation
            diff = subset["entropy_encrypted"] - subset["entropy_raw"]
            r = stat / np.sum(np.abs(diff)) if np.sum(np.abs(diff)) != 0 else np.nan
            results.append({
                "algorithm": alg,
                "wilcoxon_stat": stat,
                "p_value": p,
                "effect_size_r": r
            })
        results_df = pd.DataFrame(results)
        # Bonferroni correction
        results_df["p_corrected"] = results_df["p_value"] * len(results_df)
        results_df["p_corrected"] = results_df["p_corrected"].clip(upper=1.0)
        # Save
        results_df.to_csv(self.output_dir / "wilcoxon_by_algorithm.csv", index=False)
        # Write a summary text file
        with open(self.output_dir / "wilcoxon_report.txt", "w") as f:
            f.write("Wilcoxon Signed-Rank Test: Raw vs Encrypted Entropy per Algorithm\n\n")
            f.write(results_df.to_string(index=False))
            f.write("\n\nInterpretation: p_corrected < 0.05 indicates significant shift in entropy.\n")
        return results_df
    def kruskal_wallis_test(self):
        """Kruskal-Wallis test for encrypted entropy across algorithms."""
        
        groups = [group["entropy_encrypted"].values for name, group in self.pdf.groupby("algorithm")]
        H, p = kruskal(*groups)
        with open(self.output_dir / "kruskal_wallis.txt", "w") as f:
            f.write(f"Kruskal-Wallis H-statistic: {H:.4f}\n")
            f.write(f"P-value: {p:.6f}\n")
            if p < 0.05:
                f.write("Significant difference detected among algorithms (p<0.05).\n")
            else:
                f.write("No significant difference among algorithms.\n")
        return H, p
    def generate_all(self):
        self.entropy_histogram()
        self.entropy_boxplot()            # now with significance bars
        self.entropy_violin_advanced()
        self.entropy_delta()
        self.encryption_times()
        self.decryption_times()
        self.entropy_scatter()
        self.entropy_ecdf()
        self.time_vs_entropy_scatter()
        self.pairwise_entropy_heatmap()
        self.combined_dashboard()
        self.mean_error_by_algorithm()
        # statistics
        self.descriptive_statistics()
        self.wilcoxon_per_algorithm()
        self.kruskal_wallis_test()
        # original overall Wilcoxon can be kept or removed
        self.wilcoxon_test()
        print("All professional-grade plots and statistics generated successfully.")