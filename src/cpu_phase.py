"""Fase CPU-bound: analisis log paralel dengan ProcessPoolExecutor."""

import hashlib
import random
import statistics
import time
from concurrent.futures import ProcessPoolExecutor

from . import config
from .server_sim import HasilRequest


def checksum_chunk(chunk: list[HasilRequest], cpu_work: int) -> dict:
    """Checksum SHA-256 berulang tiap record (fungsi top-level, bisa di-pickle)."""
    cek_xor = 0
    for r in chunk:
        h = hashlib.sha256(
            f"{r.id}|{r.server}|{r.status}|{r.response_time_ms:.3f}".encode()
        ).digest()
        for _ in range(cpu_work):
            h = hashlib.sha256(h).digest()
        cek_xor ^= int.from_bytes(h, "big")
    return {
        "n": len(chunk),
        "checksum_xor": cek_xor,
        "rt": [r.response_time_ms for r in chunk],
        "status": [r.status for r in chunk],
        "fallback": [1 if r.fallback else 0 for r in chunk],
    }


def bootstrap_parsial(rt: list[float], seed: int, awal: int, akhir: int) -> list[float]:
    """Rata-rata resample ke-`awal`..`akhir` (seed per resample, partisi-bebas)."""
    n = len(rt)
    rata = []
    for i in range(awal, akhir):
        rng = random.Random(seed + i)
        rata.append(statistics.fmean(rng.choices(rt, k=n)))
    return rata


def _bagi_chunk(data: list, jumlah: int) -> list[list]:
    """Bagi data menjadi `jumlah` potongan berukuran hampir sama."""
    jumlah = max(1, min(jumlah, len(data)) if data else 1)
    ukuran, sisa = divmod(len(data), jumlah)
    hasil, awal = [], 0
    for i in range(jumlah):
        akhir = awal + ukuran + (1 if i < sisa else 0)
        hasil.append(data[awal:akhir])
        awal = akhir
    return [c for c in hasil if c]


def _bagi_rentang(total: int, jumlah: int) -> list[tuple[int, int]]:
    """Bagi rentang resample 0..total menjadi `jumlah` bagian."""
    jumlah = max(1, jumlah)
    ukuran, sisa = divmod(total, jumlah)
    hasil, awal = [], 0
    for i in range(jumlah):
        akhir = awal + ukuran + (1 if i < sisa else 0)
        if akhir > awal:
            hasil.append((awal, akhir))
        awal = akhir
    return hasil


def _agregat(hsl_chunk: list[dict], semua_mean: list[float]) -> dict:
    """Gabung hasil chunk + bootstrap menjadi statistik akhir (deterministik)."""
    rt = sorted(v for b in hsl_chunk for v in b["rt"])
    status = [s for b in hsl_chunk for s in b["status"]]
    fallback = [f for b in hsl_chunk for f in b["fallback"]]
    n = len(rt)

    rerata = statistics.fmean(rt)
    tengah = statistics.median(rt)
    potong = statistics.quantiles(rt, n=100) if n >= 100 else None
    if potong is not None:
        p95, p99 = potong[94], potong[98]
    else:
        p95 = tengah
        p99 = max(rt)

    dist = {200: 0, 502: 0, 504: 0}
    for s in status:
        dist[s] = dist.get(s, 0) + 1

    if n >= 2:
        sd = statistics.stdev(rt)
        outlier = sum(1 for v in rt if sd > 0 and abs(v - rerata) / sd > 3.0)
    else:
        outlier = 0

    mean_urut = sorted(semua_mean)
    if mean_urut:
        ci_low = mean_urut[int(0.025 * (len(mean_urut) - 1))]
        ci_high = mean_urut[int(0.975 * (len(mean_urut) - 1))]
    else:
        ci_low = ci_high = rerata

    cek = 0
    for b in hsl_chunk:
        cek ^= b["checksum_xor"]

    return {
        "n": n,
        "mean_ms": rerata,
        "median_ms": tengah,
        "p95_ms": p95,
        "p99_ms": p99,
        "min_ms": min(rt),
        "max_ms": max(rt),
        "success_rate": dist.get(200, 0) / n,
        "status_200": dist.get(200, 0),
        "status_502": dist.get(502, 0),
        "status_504": dist.get(504, 0),
        "fallback_pct": sum(fallback) / n * 100.0,
        "outlier_n": outlier,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "checksum": hex(cek),
    }


def fase_cpu_sekuensial(log: list[HasilRequest], cpu_work: int = config.CPU_WORK,
                        bootstrap_n: int = config.BOOTSTRAP_N,
                        seed: int = config.SEED) -> tuple[dict, float]:
    """Analisis satu proses (baseline pembanding hasil paralel)."""
    mulai = time.perf_counter()
    bagian = [checksum_chunk(log, cpu_work)]
    rt = bagian[0]["rt"]
    means = bootstrap_parsial(rt, seed, 0, bootstrap_n)
    return _agregat(bagian, means), time.perf_counter() - mulai


def fase_cpu_paralel(log: list[HasilRequest], processes: int = config.PROCESSES,
                     cpu_work: int = config.CPU_WORK,
                     bootstrap_n: int = config.BOOTSTRAP_N,
                     seed: int = config.SEED) -> tuple[dict, float]:
    """Analisis dengan ProcessPoolExecutor, hasil gabungan setara sekuensial."""
    potongan = _bagi_chunk(log, processes)
    rentang = _bagi_rentang(bootstrap_n, processes)
    mulai = time.perf_counter()
    with ProcessPoolExecutor(max_workers=processes) as pool:
        tugas_cek = [pool.submit(checksum_chunk, c, cpu_work) for c in potongan]
        bagian = [t.result() for t in tugas_cek]
        rt_penuh = [v for b in bagian for v in b["rt"]]
        tugas_boot = [pool.submit(bootstrap_parsial, rt_penuh, seed, a, b)
                      for a, b in rentang]
        means = [m for t in tugas_boot for m in t.result()]
    return _agregat(bagian, means), time.perf_counter() - mulai
