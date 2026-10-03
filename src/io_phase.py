"""Nama: Muhammad Fadhlan Aminullah
NPM: 247006111151
Kelas: G
"""

import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from . import config
from .generator import RencanaRequest
from .server_sim import HasilRequest, proses_satu


def fase_io(rencana: list[RencanaRequest], max_workers: int = config.THREADS,
            time_scale: float = config.TIME_SCALE) -> tuple[list[HasilRequest], float]:
    mulai = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        hasil = list(pool.map(partial(proses_satu, time_scale=time_scale), rencana))
    t_io = time.perf_counter() - mulai
    hasil.sort(key=lambda h: h.id)
    return hasil, t_io
