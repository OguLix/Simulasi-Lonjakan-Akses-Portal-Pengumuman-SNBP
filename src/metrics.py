"""Metrik throughput, speedup, dan efisiensi."""


def throughput(n: int, t_total: float) -> float:
    """Jumlah request per detik."""
    return n / t_total if t_total > 0 else 0.0


def speedup(t_seq: float, t_hybrid: float) -> float:
    """T_sekuensial / T_hybrid pada jumlah data yang sama."""
    return t_seq / t_hybrid if t_hybrid > 0 else 0.0


def efisiensi(speedup_val: float, processes: int) -> float:
    """Speedup / jumlah proses x 100 (kolom utama laporan)."""
    return speedup_val / processes * 100.0 if processes > 0 else 0.0


def efisiensi_total_worker(speedup_val: float, threads: int, processes: int) -> float:
    """Speedup / (thread + proses) x 100 (kolom tambahan)."""
    total = threads + processes
    return speedup_val / total * 100.0 if total > 0 else 0.0
