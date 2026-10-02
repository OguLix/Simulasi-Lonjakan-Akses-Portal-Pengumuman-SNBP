"""Tes dasar: determinisme generator."""

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


if __name__ == "__main__":
    unittest.main()
