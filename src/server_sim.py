"""Nama: Muhammad Fadhlan Aminullah
NPM: 247006111151
Kelas: G
"""

import time
from dataclasses import dataclass

from . import config
from .generator import RencanaRequest


@dataclass
class HasilRequest:
    id: int
    server: str
    status: int
    response_time_ms: float
    fallback: bool


def kirim_request(req: RencanaRequest, ke_mirror: bool = False,
                  time_scale: float = config.TIME_SCALE) -> HasilRequest:
    if ke_mirror:
        latensi_ms = req.service_time_mirror
        status = req.status_mirror
        server = f"mirror-{req.mirror_dipilih + 1}"
    else:
        latensi_ms = req.service_time_utama
        status = req.status_utama
        server = "utama"

    mulai = time.perf_counter()
    time.sleep(latensi_ms / 1000.0 * time_scale)
    selesai = time.perf_counter()
    return HasilRequest(
        id=req.id,
        server=server,
        status=status,
        response_time_ms=(selesai - mulai) * 1000.0,
        fallback=ke_mirror,
    )


def proses_satu(req: RencanaRequest,
                time_scale: float = config.TIME_SCALE) -> HasilRequest:
    pertama = kirim_request(req, ke_mirror=False, time_scale=time_scale)
    if pertama.status == 200:
        return pertama
    kedua = kirim_request(req, ke_mirror=True, time_scale=time_scale)
    kedua.response_time_ms = pertama.response_time_ms + kedua.response_time_ms
    return kedua
