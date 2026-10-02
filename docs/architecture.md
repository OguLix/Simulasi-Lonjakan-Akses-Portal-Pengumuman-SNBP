# Arsitektur

Simulasi lonjakan akses portal pengumuman SNBP: ribuan peserta membuka portal
hampir bersamaan. Server utama berkapasitas terbatas, sebagian request gagal
(502/504) lalu dialihkan sekali ke satu dari 3 server mirror.

## Alur

```
generator -> io_phase (ThreadPool) -> cpu_phase (ProcessPool) -> metrics
```

1. `generator.py`: susun rencana request deterministik (`random.Random(seed)`,
   seed = NPM 247006111151). Semua angka acak (status, latensi, mirror pilihan)
   ditetapkan di sini supaya run dapat diulang persis.
2. `server_sim.py`: tiap request tidur `latensi * TIME_SCALE` (I/O, melepas GIL).
3. `io_phase.py`: `ThreadPoolExecutor(5)`. Coba server utama dulu, kalau status
   bukan 200 coba sekali ke mirror. Hasil diurutkan per `id`.
4. `cpu_phase.py`: `ProcessPoolExecutor`. Log dibagi rata per proses; tiap chunk
   menghitung checksum SHA-256 berulang (`CPU_WORK=4000`) dan bootstrap
   (`BOOTSTRAP_N=300`, seed per resample sehingga gabungan paralel identik
   dengan sekuensial). Agregat menghitung mean/median/p95/p99, success rate,
   distribusi status, fallback %, outlier z-score (|z|>3), dan CI 95%.
5. `metrics.py`: throughput = data/waktu; speedup = T_seq/T_hybrid (data sama);
   efisiensi = speedup/proses x 100.

## Profil lonjakan

Peluang gagal utama naik di tengah antrean (30%-70%): 502 sebesar 8% di luar
dan 25% saat lonjakan; 504 sebesar 5% dan 20%. Mirror gagal ~3%.
Latensi lognormal (median utama ~244 ms, mirror ~148 ms); request 504
menunggu sampai `TIMEOUT_MS` = 2000 ms. Response time terukur sudah dikali
`TIME_SCALE` (0.25), jadi merupakan "waktu simulasi terskala", bukan
waktu dinding mentah. Untuk request fallback, response time adalah jumlah
waktu percobaan utama + mirror.

## Hasil run nyata (1510 data, seed 247006111151)

Skala thread (1 proses): 1 thread 215,4 dtk, 2 thread 112,7 dtk,
3 thread 77,8 dtk, 5 thread 49,7 dtk, 8 thread 35,2 dtk (speedup maks 6,1).
Skala proses (5 thread): 1 proses 49,7 dtk (t_cpu 7,8), 2 proses 46,8 dtk
(4,9), 3 proses 45,3 dtk (3,5), 4 proses 44,8 dtk (3,0). Total didominasi
fase I/O (~42 dtk), sehingga tambah proses hanya memangkas t_cpu.
Success rate 99,4%, fallback ke mirror ~24,8%.

Catatan: kolom utama `efisiensi_pct` memakai speedup / (thread + proses).
Rumus contoh soal (speedup / proses) tidak cocok untuk desain hybrid karena
speedup di sini sebagian besar berasal dari thread I/O, sehingga rumus soal
menghasilkan >100% (sampai ~600%). Rumus soal dipertahankan sebagai
pembanding di kolom `efisiensi_per_proses_pct`.
