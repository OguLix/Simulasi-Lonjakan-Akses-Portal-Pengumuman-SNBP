# STATUS.md — catatan progres agent

## Selesai
- [x] Tahap 1: struktur folder, `.gitignore`, `requirements.txt`, `README.md` awal.
- [x] Tahap 5: `metrics.py`, `pipeline.py`, `main.py` (CLI compare/hybrid/sequential, format soal OK).

## Berjalan
- [ ] Tahap 6: `experiments/run_experiments.py` + `results.csv` nyata.

## Belum
- [ ] Tahap 6: `experiments/run_experiments.py` + `results.csv` nyata.
- [ ] Tahap 7: `experiments/plot_results.py` + 3 grafik.
- [ ] Tahap 8: `docs/architecture.md`, `docs/hardware.md`.
- [ ] Tahap 9: rapikan `README.md`.

## Masalah
- Belum ada.

## Keputusan
- `results/raw/*.json` di-ignore via `.gitignore` (mentah per-run tidak wajib di-commit).
- Nama lengkap untuk output CLI memakai konstanta `NAMA` di `config.py`: "Muhammad Fadhlan Aminullah".
- `.gitignore` mengecualikan `AGENT.md` (tidak di-commit ke repo).
