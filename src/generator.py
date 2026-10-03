"""Nama: Muhammad Fadhlan Aminullah
NPM: 247006111151
Kelas: G
"""

from dataclasses import dataclass

from . import config


@dataclass
class RencanaRequest:
    id: int
    index_antrean: int
    service_time_utama: float
    status_utama: int
    service_time_mirror: float
    status_mirror: int
    mirror_dipilih: int


def buat_rencana(n: int = config.N_DATA, seed: int = config.SEED,
                 mirrors: int = config.MIRRORS) -> list[RencanaRequest]:
    import random

    rng = random.Random(seed)
    rencana = []
    for i in range(n):
        fraksi = i / n if n else 0.0
        lonjakan = config.SURGE_START_FRAC <= fraksi < config.SURGE_END_FRAC
        p502 = config.P_502_SURGE if lonjakan else config.P_502_BASE
        p504 = config.P_504_SURGE if lonjakan else config.P_504_BASE

        r = rng.random()
        if r < p502:
            status_utama = 502
        elif r < p502 + p504:
            status_utama = 504
        else:
            status_utama = 200

        if status_utama == 504:
            service_utama = float(config.TIMEOUT_MS)
        else:
            service_utama = float(rng.lognormvariate(config.MU_UTAMA, config.SIGMA_UTAMA))

        mirror = rng.randrange(mirrors) if mirrors > 0 else 0
        if rng.random() < config.P_MIRROR_FAIL:
            status_mirror = 502 if rng.random() < 0.5 else 504
        else:
            status_mirror = 200
        if status_mirror == 504:
            service_mirror = float(config.TIMEOUT_MS)
        else:
            service_mirror = float(rng.lognormvariate(config.MU_MIRROR, config.SIGMA_MIRROR))

        rencana.append(RencanaRequest(
            id=i,
            index_antrean=i,
            service_time_utama=service_utama,
            status_utama=status_utama,
            service_time_mirror=service_mirror,
            status_mirror=status_mirror,
            mirror_dipilih=mirror,
        ))
    return rencana
