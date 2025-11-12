"""
app/plotter.py
Modul untuk membuat grafik EAR dan menyimpannya sebagai PNG.
Kompatibel dengan GUI dan EarLogger terbaru.
"""

import matplotlib
matplotlib.use("Agg")  # NON-GUI backend
import matplotlib.pyplot as plt
import pandas as pd
import os

class Plotter:
    def __init__(self, ear_logger, out_path="ear_plot.png"):
        self.ear_logger = ear_logger
        self.out_path = out_path

    def generate_plot(self):
        """Generate grafik EAR dan simpan sebagai PNG."""
        try:
            df = self.ear_logger.read_all()

            # Jika tidak ada data → tampilkan placeholder
            if df is None or df.empty:
                fig, ax = plt.subplots(figsize=(8, 3))
                ax.text(0.5, 0.5, "BELUM ADA DATA EAR",
                        fontsize=16, ha="center", va="center")
                ax.set_axis_off()
                fig.savefig(self.out_path, bbox_inches="tight")
                plt.close()
                return

            # BACKWARD COMPATIBILITY:
            # Kalau file lama masih pakai ear_value → rename
            if "ear" not in df.columns:
                if "ear_value" in df.columns:
                    df.rename(columns={"ear_value": "ear"}, inplace=True)
                else:
                    raise KeyError("Kolom 'ear' tidak ditemukan dan tidak ada 'ear_value'.")

            # Plot grafik EAR
            fig, ax = plt.subplots(figsize=(8, 3))
            ax.plot(df["ear"].values, label="EAR", linewidth=1.6)

            # Threshold 0.21
            ax.axhline(0.21, color="red", linestyle="--", linewidth=1.3, label="Threshold 0.21")

            ax.set_title("Grafik EAR (Eye Aspect Ratio)", fontsize=12)
            ax.set_xlabel("Index Sampel")
            ax.set_ylabel("EAR")

            ax.grid(True, linestyle="--", alpha=0.6)
            ax.legend()

            fig.tight_layout()
            fig.savefig(self.out_path, dpi=120)
            plt.close()

        except Exception as e:
            print("Error generating plot:", e)
