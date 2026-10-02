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
- [x] Revisi 1: efisiensi utama = speedup/(thread+proses); rumus lama jadi kolom `efisiensi_per_proses_pct`.
- [x] Revisi 2: response time fallback kumulatif (utama+mirror) via `proses_satu` bersama; tes baru lulus (5 tes total).
- [x] Revisi 3: grafik sumbu bulat, y dari 0, label T-P + nilai speedup per batang.
- [x] Revisi 4: rerun penuh nyata pasca-revisi (10 cfg + 3 baseline, 3x median, tanpa gagal) -> `results.csv` baru + 3 PNG + README sinkron.

## Berjalan
- (kosong)

## Belum
- (kosong — semua tahap selesai)

## Masalah
- Rerun revisi 4: tidak ada run yang gagal (39/39 rep sukses).
- Total run masih didominasi fase I/O (~42 dtk dari ~45 dtk cfg default).

## Keputusan
- `results/raw/*.json` di-ignore via `.gitignore` (mentah per-run tidak wajib di-commit).
- Nama lengkap untuk output CLI memakai konstanta `NAMA` di `config.py`: "Muhammad Fadhlan Aminullah".
- `.gitignore` mengecualikan `AGENT.md` (tidak di-commit ke repo).
- Bootstrap memakai seed per-resample agar hasil paralel identik persis dengan sekuensial (uji kesetaraan exact, bukan aproksimasi).
- Default `python -m src.main` memakai `--mode compare` agar speedup yang tampil selalu riil.
- Revisi efisiensi menyimpang dari contoh rumus soal (AGENT.md 5.6) secara sadar; dijelaskan di `docs/architecture.md`.
- Response time terukur sudah dikali TIME_SCALE (0.25): "waktu simulasi terskala".
