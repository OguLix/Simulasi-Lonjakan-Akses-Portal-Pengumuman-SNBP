"""CLI simulator: python -m src.main [--mode hybrid|sequential|compare]."""

import argparse
import multiprocessing

from . import config, metrics
from .pipeline import run_hybrid, run_sequential


def _cetak(hasil: dict, t_total: float, n: int, threads: int, processes: int,
           t_seq: float | None = None) -> None:
    """Cetak ringkasan run sesuai format wajib soal."""
    tp = metrics.throughput(n, t_total)
    a = hasil
    print(f"Hybrid Project by: {config.NAMA} ({config.NPM})")
    print(f"Threads: {threads} | Processes: {processes} | Data: {n}")
    if t_seq is None:
        print(f"Total Time: {t_total:.2f} s | Throughput: {tp:.1f} req/s | "
              "Speedup: - | Efficiency: -%")
    else:
        sp = metrics.speedup(t_seq, t_total)
        ef = metrics.efisiensi(sp, threads, processes)
        print(f"Total Time: {t_total:.2f} s | Throughput: {tp:.1f} req/s | "
              f"Speedup: {sp:.1f} | Efficiency: {ef:.1f}%")
    print("--- Contoh hasil analisis ---")
    print(f"Success rate: {a['success_rate'] * 100:.1f}% | "
          f"Fallback ke mirror: {a['fallback_pct']:.1f}%")
    print(f"Response time (ms): mean={a['mean_ms']:.1f} p95={a['p95_ms']:.1f} "
          f"p99={a['p99_ms']:.1f} | Outlier: {a['outlier_n']}")
    print(f"Status: 200={a['status_200']} 502={a['status_502']} 504={a['status_504']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Hybrid Parallel Load Simulator")
    parser.add_argument("--threads", type=int, default=config.THREADS)
    parser.add_argument("--processes", type=int, default=config.PROCESSES)
    parser.add_argument("--data", type=int, default=config.N_DATA)
    parser.add_argument("--mirrors", type=int, default=config.MIRRORS)
    parser.add_argument("--time-scale", type=float, default=config.TIME_SCALE)
    parser.add_argument("--seed", type=int, default=config.SEED)
    parser.add_argument("--mode", choices=("hybrid", "sequential", "compare"),
                        default="compare")
    args = parser.parse_args()

    if args.mode == "sequential":
        run = run_sequential(n=args.data, time_scale=args.time_scale,
                             seed=args.seed, mirrors=args.mirrors)
        _cetak(run["hasil"], run["t_total"], args.data,
               args.threads, args.processes)
    elif args.mode == "compare":
        seq = run_sequential(n=args.data, time_scale=args.time_scale,
                             seed=args.seed, mirrors=args.mirrors)
        hyb = run_hybrid(n=args.data, threads=args.threads,
                         processes=args.processes, time_scale=args.time_scale,
                         seed=args.seed, mirrors=args.mirrors)
        _cetak(hyb["hasil"], hyb["t_total"], args.data,
               args.threads, args.processes, t_seq=seq["t_total"])
    else:
        hyb = run_hybrid(n=args.data, threads=args.threads,
                         processes=args.processes, time_scale=args.time_scale,
                         seed=args.seed, mirrors=args.mirrors)
        _cetak(hyb["hasil"], hyb["t_total"], args.data,
               args.threads, args.processes)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
