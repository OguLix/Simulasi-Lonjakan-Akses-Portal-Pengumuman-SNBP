"""Buat 3 grafik wajib dari results.csv ke results/figures/.

Contoh: python experiments/plot_results.py [results/results_quick.csv]
"""

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent


def _baca(csv_path: Path) -> list[dict]:
    with open(csv_path, newline="") as f:
        return [{k: (float(v) if k not in ("no",) else int(v))
                 for k, v in r.items()
                 if k in ("no", "threads", "processes", "data", "waktu_s",
                          "speedup")}
                for r in csv.DictReader(f)]


def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "results.csv"
    baris = _baca(csv_path)
    per_no = {int(r["no"]): r for r in baris}
    fig_dir = ROOT / "results" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. Waktu vs jumlah thread (no 1-5, proses tetap 1).
    sub = [per_no[i] for i in (1, 2, 3, 4, 5) if i in per_no]
    plt.figure()
    plt.plot([r["threads"] for r in sub], [r["waktu_s"] for r in sub], marker="o")
    plt.title("Waktu vs Jumlah Thread (1 proses, 1510 data)")
    plt.xlabel("Jumlah thread")
    plt.ylabel("Waktu (detik)")
    plt.savefig(fig_dir / "waktu_vs_thread.png")
    plt.close()

    # 2. Waktu vs jumlah proses (no 4, 6, 7, 8, thread tetap 5).
    sub = [per_no[i] for i in (4, 6, 7, 8) if i in per_no]
    plt.figure()
    plt.plot([r["processes"] for r in sub], [r["waktu_s"] for r in sub], marker="o")
    plt.title("Waktu vs Jumlah Proses (5 thread, 1510 data)")
    plt.xlabel("Jumlah proses")
    plt.ylabel("Waktu (detik)")
    plt.savefig(fig_dir / "waktu_vs_proses.png")
    plt.close()

    # 3. Speedup vs konfigurasi (semua).
    sub = sorted(baris, key=lambda r: r["no"])
    plt.figure()
    plt.bar([str(int(r["no"])) for r in sub], [r["speedup"] for r in sub])
    plt.title("Speedup vs Konfigurasi")
    plt.xlabel("Nomor konfigurasi")
    plt.ylabel("Speedup")
    plt.savefig(fig_dir / "speedup_vs_konfigurasi.png")
    plt.close()

    print(f"Grafik tersimpan di {fig_dir}", flush=True)


if __name__ == "__main__":
    main()
