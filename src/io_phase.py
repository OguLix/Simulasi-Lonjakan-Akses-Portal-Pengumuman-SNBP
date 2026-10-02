"""Fase I/O: ThreadPoolExecutor untuk simulasi request paralel."""

import time
from concurrent.futures import ThreadPoolExecutor

from . import config
from .generator import RencanaRequest
from .server_sim import HasilRequest, kirim_request


def _proses_satu(req: RencanaRequest, time_scale: float) -> HasilRequest:
    """Kirim ke utama, sekali fallback ke mirror jika gagal."""
    hasil = kirim_request(req, ke_mirror=False, time_scale=time_scale)
    if hasil.status != 200:
        hasil = kirim_request(req, ke_mirror=True, time_scale=time_scale)
    return hasil


def fase_io(rencana: list[RencanaRequest], max_workers: int = config.THREADS,
            time_scale: float = config.TIME_SCALE) -> tuple[list[HasilRequest], float]:
    """Jalankan seluruh rencana via ThreadPool, kembalikan (hasil urut id, t_io)."""
    mulai = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        hasil = list(pool.map(lambda r: _proses_satu(r, time_scale), rencana))
    t_io = time.perf_counter() - mulai
    hasil.sort(key=lambda h: h.id)
    return hasil, t_io
