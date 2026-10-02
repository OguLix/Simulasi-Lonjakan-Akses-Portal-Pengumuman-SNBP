# Hybrid Parallel Load Simulator

Simulasi lonjakan akses portal pengumuman SNBP: server utama kapasitas terbatas
(gagal 502/504 saat lonjakan) + 3 server mirror sebagai fallback. Fase I/O
paralel via ThreadPool, fase analisis via ProcessPool.

Mata kuliah Komputasi Paralel dan Terdistribusi, Informatika, Universitas Siliwangi.

## Instalasi (Windows)

```powershell
pip install -r requirements.txt
```

## Menjalankan

```powershell
python -m src.main                                    # default: 5 thread, 3 proses, 1510 data (compare, ~5 mnt)
python -m src.main --mode hybrid --data 100           # hybrid saja, cepat
python -m src.main --mode compare --data 100          # hybrid vs sekuensial + speedup riil
python -m unittest                                    # tes (4 tes)
python experiments/run_experiments.py --quick         # uji plumbing eksperimen
python experiments/run_experiments.py                 # 10 konfigurasi penuh (~55 mnt)
python experiments/plot_results.py                    # regenerasi 3 grafik
```

Opsi CLI: `--threads`, `--processes`, `--data`, `--mirrors`,
`--time-scale`, `--seed`, `--mode {hybrid,sequential,compare}`.

## Contoh output

```
Hybrid Project by: Muhammad Fadhlan Aminullah (247006111151)
Threads: 5 | Processes: 3 | Data: 1510
Total Time: 45.33 s | Throughput: 33.3 req/s | Speedup: 4.7 | Efficiency: 59.2%
--- Contoh hasil analisis ---
Success rate: 99.4% | Fallback ke mirror: 24.8%
Response time (ms): mean=... p95=... p99=... | Outlier: ...
Status: 200=... 502=... 504=...
```

## Ringkasan hasil (run nyata, `results/results.csv`)

- Skala thread (1510 data): 215,4 dtk (1) -> 35,2 dtk (8 thread), speedup 6,1.
- Skala proses: t_cpu 7,8 -> 3,0 dtk (1 ke 4 proses); total didominasi I/O (~42 dtk).
- Success rate 99,4%, fallback mirror ~24,8%. Detail: `docs/architecture.md`.
