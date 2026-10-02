"""Buat 3 grafik wajib dari results.csv ke results/figures/.

Contoh: python experiments/plot_results.py [results/results.csv]
"""

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

ROOT = Path(__file__).resolve().parent.parent


def _kode(r: dict) -> str:
    """Kode konfigurasi, mis. T5-P3-D1510 (thread-proses-data)."""
    return f"T{int(r['threads'])}-P{int(r['processes'])}-D{int(r['data'])}"


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
    _, ax = plt.subplots()
    ax.plot([r["threads"] for r in sub], [r["waktu_s"] for r in sub], marker="o")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim(bottom=0)
    ax.set_title("Waktu vs Jumlah Thread (1 proses, 1510 data)")
    ax.set_xlabel("Jumlah thread")
    ax.set_ylabel("Waktu (detik)")
    plt.savefig(fig_dir / "waktu_vs_thread.png")
    plt.close()

    # 2. Waktu vs jumlah proses (no 4, 6, 7, 8, thread tetap 5).
    sub = [per_no[i] for i in (4, 6, 7, 8) if i in per_no]
    _, ax = plt.subplots()
    ax.plot([r["processes"] for r in sub], [r["waktu_s"] for r in sub], marker="o")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylim(bottom=0)
    ax.set_title("Waktu vs Jumlah Proses (5 thread, 1510 data)")
    ax.set_xlabel("Jumlah proses")
    ax.set_ylabel("Waktu (detik)")
    plt.savefig(fig_dir / "waktu_vs_proses.png")
    plt.close()

    # 3. Speedup vs konfigurasi (semua).
    sub = sorted(baris, key=lambda r: r["no"])
    _, ax = plt.subplots()
    batang = ax.bar([_kode(r) for r in sub], [r["speedup"] for r in sub])
    for b, r in zip(batang, sub):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                f"{r['speedup']:.2f}", ha="center", va="bottom", fontsize=7)
    plt.xticks(rotation=45, ha="right")
    ax.set_ylim(bottom=0)
    ax.set_title("Speedup vs Konfigurasi")
    ax.set_xlabel("Konfigurasi (thread-proses-data)")
    ax.set_ylabel("Speedup")
    plt.tight_layout()
    plt.savefig(fig_dir / "speedup_vs_konfigurasi.png", bbox_inches="tight")
    plt.close()

    print(f"Grafik tersimpan di {fig_dir}", flush=True)


if __name__ == "__main__":
    main()
