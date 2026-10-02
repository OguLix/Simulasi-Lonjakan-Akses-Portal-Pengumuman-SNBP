"""Orkestrasi run sekuensial (baseline) dan hybrid (thread + proses)."""

import time

from . import config
from .cpu_phase import fase_cpu_paralel, fase_cpu_sekuensial
from .generator import buat_rencana
from .io_phase import fase_io
from .server_sim import kirim_request


def run_sequential(n: int = config.N_DATA, time_scale: float = config.TIME_SCALE,
                   seed: int = config.SEED, mirrors: int = config.MIRRORS,
                   cpu_work: int = config.CPU_WORK,
                   bootstrap_n: int = config.BOOTSTRAP_N) -> dict:
    """Tanpa pool: loop I/O biasa lalu analisis satu proses."""
    rencana = buat_rencana(n, seed=seed, mirrors=mirrors)
    mulai = time.perf_counter()
    log = []
    for req in rencana:
        hasil = kirim_request(req, ke_mirror=False, time_scale=time_scale)
        if hasil.status != 200:
            hasil = kirim_request(req, ke_mirror=True, time_scale=time_scale)
        log.append(hasil)
    log.sort(key=lambda h: h.id)
    t_io = time.perf_counter() - mulai
    hasil, t_cpu = fase_cpu_sekuensial(log, cpu_work=cpu_work,
                                       bootstrap_n=bootstrap_n, seed=seed)
    return {"hasil": hasil, "t_total": time.perf_counter() - mulai,
            "t_io": t_io, "t_cpu": t_cpu, "n": n}


def run_hybrid(n: int = config.N_DATA, threads: int = config.THREADS,
               processes: int = config.PROCESSES,
               time_scale: float = config.TIME_SCALE, seed: int = config.SEED,
               mirrors: int = config.MIRRORS, cpu_work: int = config.CPU_WORK,
               bootstrap_n: int = config.BOOTSTRAP_N) -> dict:
    """Fase I/O dengan thread, lalu fase CPU dengan proses."""
    rencana = buat_rencana(n, seed=seed, mirrors=mirrors)
    mulai = time.perf_counter()
    log, _ = fase_io(rencana, max_workers=threads, time_scale=time_scale)
    t_io = time.perf_counter() - mulai
    hasil, _ = fase_cpu_paralel(log, processes=processes, cpu_work=cpu_work,
                                bootstrap_n=bootstrap_n, seed=seed)
    t_cpu = time.perf_counter() - mulai - t_io
    return {"hasil": hasil, "t_total": time.perf_counter() - mulai,
            "t_io": t_io, "t_cpu": t_cpu, "n": n,
            "threads": threads, "processes": processes}
