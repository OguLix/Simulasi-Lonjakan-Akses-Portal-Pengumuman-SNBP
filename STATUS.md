# STATUS.md — catatan progres agent

## Selesai
- [x] Tahap 1: struktur folder, `.gitignore`, `requirements.txt`, `README.md` awal.
- [x] Tahap 2: `config.py` dan `generator.py` (+ tes determinisme lulus).
- [x] Tahap 3: `server_sim.py` dan `io_phase.py` (fallback mirror jalan).
- [x] Tahap 4: `cpu_phase.py` + kalibrasi (`CPU_WORK=4000`, `BOOTSTRAP_N=300`) + tes kesetaraan paralel vs sekuensial lulus.
- [x] Tahap 5: `metrics.py`, `pipeline.py`, `main.py` (CLI compare/hybrid/sequential).
- [x] Tahap 6: run penuh nyata — 10 konfigurasi + 3 baseline, 3x ulangan median -> `results/results.csv` (total ~55 mnt).
- [x] Tahap 7: `plot_results.py` + 3 PNG di `results/figures/`.
- [x] Tahap 8: `docs/architecture.md`, `docs/hardware.md`.
- [x] Tahap 9: `README.md` final.

## Berjalan
- (kosong)

## Belum
- (kosong — semua tahap selesai)

## Masalah
- Kalibrasi CPU berisik di mesin uji: run dingin pertama ~2x lebih lambat dari run hangat. Nilai final `CPU_WORK=4000` memberi ~11 dtk steady-state (target 10-20 dtk).
- Total run didominasi fase I/O (~42 dtk dari ~47 dtk), sehingga skala proses hanya memangkas t_cpu. Dicatat apa adanya.
- Efisiensi kolom utama (speedup/proses) >100% untuk konfigurasi 1 proses — artefak rumus soal, kolom `efisiensi_total_worker_pct` sebagai pembanding intuitif.

## Keputusan
- `results/raw/*.json` di-ignore via `.gitignore` (mentah per-run tidak wajib di-commit).
- Nama lengkap untuk output CLI memakai konstanta `NAMA` di `config.py`: "Muhammad Fadhlan Aminullah".
- `.gitignore` mengecualikan `AGENT.md` (tidak di-commit ke repo).
- Bootstrap memakai seed per-resample agar hasil paralel identik persis dengan sekuensial (uji kesetaraan exact, bukan aproksimasi).
- Default `python -m src.main` memakai `--mode compare` agar speedup yang tampil selalu riil.
