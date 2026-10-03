"""Nama: Muhammad Fadhlan Aminullah
NPM: 247006111151
Kelas: G
"""

import unittest

from src import config, generator


class TestGenerator(unittest.TestCase):
    def test_seed_sama_hasil_sama(self):
        a = generator.buat_rencana(100, seed=config.SEED)
        b = generator.buat_rencana(100, seed=config.SEED)
        self.assertEqual(a, b)

    def test_seed_beda_hasil_beda(self):
        a = generator.buat_rencana(100, seed=config.SEED)
        b = generator.buat_rencana(100, seed=config.SEED + 1)
        self.assertNotEqual(a, b)

    def test_lonjakan_lebih_banyak_gagal(self):
        rencana = generator.buat_rencana(1510, seed=config.SEED)
        tengah = [r for r in rencana if 0.3 <= r.index_antrean / 1510 < 0.7]
        luar = [r for r in rencana if not (0.3 <= r.index_antrean / 1510 < 0.7)]
        gagal_tengah = sum(1 for r in tengah if r.status_utama != 200) / len(tengah)
        gagal_luar = sum(1 for r in luar if r.status_utama != 200) / len(luar)
        self.assertGreater(gagal_tengah, gagal_luar)


class TestCpuSetara(unittest.TestCase):
    def test_paralel_setara_sekuensial(self):
        from src import cpu_phase
        from src.server_sim import HasilRequest
        rencana = generator.buat_rencana(120, seed=config.SEED)
        log = [HasilRequest(r.id, "utama", r.status_utama,
                            r.service_time_utama, False) for r in rencana]
        seq, _ = cpu_phase.fase_cpu_sekuensial(log, cpu_work=5, bootstrap_n=10)
        par, _ = cpu_phase.fase_cpu_paralel(log, processes=3, cpu_work=5,
                                            bootstrap_n=10)
        for kunci in ("n", "mean_ms", "median_ms", "p95_ms", "p99_ms",
                      "success_rate", "status_200", "status_502", "status_504",
                      "fallback_pct", "outlier_n", "checksum",
                      "ci_low", "ci_high"):
            self.assertEqual(seq[kunci], par[kunci], kunci)


class TestFallbackKumulatif(unittest.TestCase):
    def test_fallback_lebih_lama_dari_mirror_saja(self):
        from src.server_sim import kirim_request, proses_satu
        rencana = generator.buat_rencana(200, seed=config.SEED)
        gagal = [r for r in rencana if r.status_utama != 200]
        self.assertTrue(gagal)
        for r in gagal[:5]:
            gab = proses_satu(r, time_scale=0.01)
            sendiri = kirim_request(r, ke_mirror=True, time_scale=0.01)
            self.assertTrue(gab.fallback)
            self.assertEqual(gab.status, r.status_mirror)
            self.assertGreater(gab.response_time_ms, sendiri.response_time_ms)


if __name__ == "__main__":
    unittest.main()
