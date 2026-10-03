"""Nama: Muhammad Fadhlan Aminullah
NPM: 247006111151
Kelas: G
"""


def throughput(n: int, t_total: float) -> float:
    return n / t_total if t_total > 0 else 0.0


def speedup(t_seq: float, t_hybrid: float) -> float:
    return t_seq / t_hybrid if t_hybrid > 0 else 0.0


def efisiensi(speedup_val: float, threads: int, processes: int) -> float:
    total = threads + processes
    return speedup_val / total * 100.0 if total > 0 else 0.0


def efisiensi_per_proses(speedup_val: float, processes: int) -> float:
    return speedup_val / processes * 100.0 if processes > 0 else 0.0
