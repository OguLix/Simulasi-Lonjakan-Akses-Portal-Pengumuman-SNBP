# STATUS.md — catatan progres agent

## Selesai
- [x] Tahap 1: struktur folder, `.gitignore`, `requirements.txt`, `README.md` awal.

## Berjalan
- [ ] Tahap 2: `config.py` dan `generator.py` (+ tes determinisme).

## Belum
- [ ] Tahap 3: `server_sim.py` dan `io_phase.py`.
- [ ] Tahap 4: `cpu_phase.py` + kalibrasi `CPU_WORK`/`BOOTSTRAP_N`.
- [ ] Tahap 5: `metrics.py`, `pipeline.py`, `main.py`.
- [ ] Tahap 6: `experiments/run_experiments.py` + `results.csv` nyata.
- [ ] Tahap 7: `experiments/plot_results.py` + 3 grafik.
- [ ] Tahap 8: `docs/architecture.md`, `docs/hardware.md`.
- [ ] Tahap 9: rapikan `README.md`.

## Masalah
- Belum ada.

## Keputusan
- `results/raw/*.json` di-ignore via `.gitignore` (mentah per-run tidak wajib di-commit).
- Nama lengkap untuk output CLI memakai konstanta `NAMA` di `config.py`: "Fadhlan" (lengkap menyusul konfirmasi pemilik).
