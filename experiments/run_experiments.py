"""Jalankan 10 konfigurasi + baseline sekuensial, tulis results.csv.

Contoh:
    python experiments/run_experiments.py --quick   # uji cepat plumbing
    python experiments/run_experiments.py          # run penuh (~30-45 mnt)
"""

import argparse
import csv
import json
import multiprocessing
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import config, metrics
from src.pipeline import run_hybrid, run_sequential

ROOT = Path(__file__).resolve().parent.parent
HASIL_CSV = ROOT / "results" / "results.csv"
DIR_RAW = ROOT / "results" / "raw"

KONFIGURASI = [
    (1, 1, 1, 1510),
    (2, 2, 1, 1510),
    (3, 3, 1, 1510),
    (4, 5, 1, 1510),
    (5, 8, 1, 1510),
    (6, 5, 2, 1510),
    (7, 5, 3, 1510),
    (8, 5, 4, 1510),
    (9, 5, 3, 500),
    (10, 5, 3, 1000),
]


def _jalan_sekali(no: int, threads: int, processes: int, n: int, rep: int,
                  sekuensial: bool, time_scale: float, cpu_work: int,
                  bootstrap_n: int) -> dict:
    """Satu run, simpan JSON mentah, kembalikan ringkasannya."""
    if sekuensial:
        run = run_sequential(n=n, time_scale=time_scale, seed=config.SEED,
                             cpu_work=cpu_work, bootstrap_n=bootstrap_n)
    else:
        run = run_hybrid(n=n, threads=threads, processes=processes,
                         time_scale=time_scale, seed=config.SEED,
                         cpu_work=cpu_work, bootstrap_n=bootstrap_n)
    a = run["hasil"]
    ringkas = {
        "no": no, "threads": threads, "processes": processes, "data": n,
        "waktu_s": round(run["t_total"], 3),
        "t_io_s": round(run["t_io"], 3),
        "t_cpu_s": round(run["t_cpu"], 3),
        "throughput": round(metrics.throughput(n, run["t_total"]), 3),
        "success_rate": round(a["success_rate"], 4),
        "fallback_pct": round(a["fallback_pct"], 3),
        "mean_ms": round(a["mean_ms"], 2),
        "status_200": a["status_200"],
        "status_502": a["status_502"],
        "status_504": a["status_504"],
    }
    nama = f"cfg{no}_n{n}_rep{rep}.json" if not sekuensial else f"seq_n{n}_rep{rep}.json"
    with open(DIR_RAW / nama, "w") as f:
        json.dump(ringkas, f, indent=1)
    return ringkas


def _median_rep(hasil_rep: list[dict]) -> dict:
    """Pilih run dengan waktu median (konsisten antar kolom)."""
    waktu = sorted(r["waktu_s"] for r in hasil_rep)
    med = statistics.median(waktu)
    return min(hasil_rep, key=lambda r: abs(r["waktu_s"] - med))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true",
                        help="uji cepat: 2 konfigurasi x 1 ulangan, data kecil")
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--time-scale", type=float, default=config.TIME_SCALE)
    parser.add_argument("--cpu-work", type=int, default=config.CPU_WORK)
    parser.add_argument("--bootstrap-n", type=int, default=config.BOOTSTRAP_N)
    args = parser.parse_args()

    DIR_RAW.mkdir(parents=True, exist_ok=True)
    reps = 1 if args.quick else args.reps
    konfig = [(1, 1, 1, 50), (7, 5, 3, 50)] if args.quick else KONFIGURASI
    ukuran_base = [50] if args.quick else [500, 1000, 1510]
    out_csv = ROOT / "results" / ("results_quick.csv" if args.quick else "results.csv")

    print(f"Baseline sekuensial untuk data {ukuran_base}, {reps}x ulangan", flush=True)
    base = {}
    for n in ukuran_base:
        hasil_rep = []
        for rep in range(1, reps + 1):
            t0 = time.perf_counter()
            r = _jalan_sekali(0, 1, 1, n, rep, True, args.time_scale,
                              args.cpu_work, args.bootstrap_n)
            hasil_rep.append(r)
            print(f"  seq n={n} rep={rep}: {r['waktu_s']} s "
                  f"(elapsed {time.perf_counter() - t0:.0f} s)", flush=True)
        base[n] = _median_rep(hasil_rep)["waktu_s"]

    print(f"Konfigurasi hybrid: {len(konfig)} x {reps} ulangan", flush=True)
    baris = []
    for no, th, pr, n in konfig:
        hasil_rep = []
        for rep in range(1, reps + 1):
            t0 = time.perf_counter()
            r = _jalan_sekali(no, th, pr, n, rep, False, args.time_scale,
                              args.cpu_work, args.bootstrap_n)
            hasil_rep.append(r)
            print(f"  cfg{no} t={th} p={pr} n={n} rep={rep}: {r['waktu_s']} s "
                  f"(elapsed {time.perf_counter() - t0:.0f} s)", flush=True)
        med = _median_rep(hasil_rep)
        sp = metrics.speedup(base[n], med["waktu_s"])
        med["speedup"] = round(sp, 3)
        med["efisiensi_pct"] = round(metrics.efisiensi(sp, pr), 2)
        med["efisiensi_total_worker_pct"] = round(
            metrics.efisiensi_total_worker(sp, th, pr), 2)
        baris.append(med)

    kolom = ["no", "threads", "processes", "data", "waktu_s", "t_io_s",
             "t_cpu_s", "throughput", "speedup", "efisiensi_pct",
             "efisiensi_total_worker_pct", "success_rate", "fallback_pct"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kolom, extrasaction="ignore")
        w.writeheader()
        w.writerows(baris)
    print(f"Selesai -> {out_csv}", flush=True)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
