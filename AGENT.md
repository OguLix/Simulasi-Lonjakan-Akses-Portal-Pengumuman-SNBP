# AGENT.md — Hybrid Parallel Load Simulator (UTS Komputasi Paralel dan Terdistribusi)

Dokumen ini adalah instruksi untuk AI agent yang mengerjakan kode proyek ini. Baca seluruhnya sebelum menulis kode apa pun.

## 1. Konteks proyek

- Mata kuliah: Komputasi Paralel dan Terdistribusi (Informatika, Universitas Siliwangi), UTS project-based individu.
- Tema: "Hybrid Computing for Real-World Simulation and Data Processing".
- Judul proyek: **Hybrid Parallel Load Simulator: Simulasi Lonjakan Akses Portal Pengumuman SNBP dengan Server Utama dan Mirror Menggunakan ThreadPool dan ProcessPool**.
- Pemilik: Fadhlan, NPM 247006111151.
- Skenario: ribuan peserta membuka portal pengumuman SNBP hampir bersamaan. Server utama berkapasitas terbatas sehingga sebagian request gagal (502/504). Request yang gagal dialihkan ke server mirror. Hasilnya dianalisis secara paralel.
- Seluruh server adalah **simulasi lokal**. Dilarang mengirim request jaringan ke situs asli (SNPMB, BKN, PTN, dan sebagainya).

## 2. Parameter wajib (dari NPM)

| Parameter | Nilai | Keterangan |
|---|---|---|
| NPM | 247006111151 | juga dipakai sebagai `random.seed(NPM)` |
| Jumlah thread | 5 | dua digit terakhir (51) mod 4 + 2 |
| Jumlah proses | 3 | dua digit tengah (61) mod 3 + 2 |
| Jumlah data | 1510 | tiga digit terakhir (151) x 10 |
| Server mirror | 3 | keputusan desain |

Semua nilai ini adalah **default** di `src/config.py`, tetapi bisa di-override lewat argumen CLI untuk eksperimen.

## 3. Bahasa dan teknologi

- Python 3.14 (lingkungan pemilik: Windows 11, Python 3.14.7, Intel Core i7-8565U 4 core / 8 thread).
- Pustaka standar untuk inti program: `concurrent.futures` (ThreadPoolExecutor, ProcessPoolExecutor), `random`, `time`, `statistics`, `hashlib`, `argparse`, `csv`, `json`, `dataclasses`.
- Pustaka luar hanya untuk eksperimen: `matplotlib` (grafik). `pandas` boleh dipakai di `experiments/` saja, bukan di `src/`.
- Tidak memakai MPI (opsional di soal, tidak dipakai).
- Dua paradigma yang dipakai: ThreadPool (I/O-bound) dan ProcessPool (CPU-bound).

### Catatan khusus Windows (wajib diperhatikan)

- Multiprocessing di Windows memakai `spawn`. Semua entry point harus dibungkus `if __name__ == "__main__":` dan memanggil `multiprocessing.freeze_support()`.
- Fungsi yang dikirim ke ProcessPool harus berada di level modul (bukan lambda, bukan fungsi bersarang) dan argumennya harus bisa di-pickle.
- Jangan memakai `fork`. Jangan mengandalkan state global yang diubah di proses induk.

## 4. Struktur folder

```
hybrid-snbp-simulator/
├── AGENT.md
├── README.md
├── STATUS.md                # diperbarui agent setiap selesai satu tugas
├── requirements.txt         # matplotlib (+ pandas jika dipakai)
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py            # NPM, nama, parameter turunan, konstanta simulasi
│   ├── generator.py         # membuat rencana request deterministik dari seed
│   ├── server_sim.py        # simulasi server utama dan mirror
│   ├── io_phase.py          # fase I/O: ThreadPoolExecutor
│   ├── cpu_phase.py         # fase CPU-bound: ProcessPoolExecutor + analisis
│   ├── metrics.py           # throughput, speedup, efisiensi
│   ├── pipeline.py          # run_sequential() dan run_hybrid()
│   └── main.py              # CLI: python -m src.main
├── experiments/
│   ├── run_experiments.py   # menjalankan 10 konfigurasi + baseline, tulis results.csv
│   └── plot_results.py      # membuat 3 grafik wajib
├── results/
│   ├── results.csv
│   ├── raw/                 # satu file JSON per run
│   └── figures/             # PNG grafik
├── docs/
│   ├── architecture.md      # deskripsi diagram arsitektur
│   └── hardware.md          # spesifikasi perangkat uji
└── tests/
    └── test_basic.py
```

## 5. Spesifikasi komponen

### 5.1 `generator.py`
- Memanggil `random.seed(NPM)` lalu membuat daftar `N` objek request (dataclass) secara **deterministik**: `id`, `index_antrean`, `service_time_utama`, `status_utama`, `service_time_mirror`, `status_mirror`, `mirror_dipilih`.
- Semua angka acak ditentukan di generator, **bukan** saat thread berjalan, supaya hasil sama setiap kali dijalankan dengan seed yang sama.
- Profil lonjakan: peluang gagal server utama naik pada fase tengah antrean (kira-kira 30%-70% dari total request). Contoh awal: peluang 502 sekitar 8% di luar lonjakan dan 25% saat lonjakan; peluang 504 (timeout) sekitar 5% dan 20%. Mirror: peluang gagal sekitar 3%. Nilai persisnya diletakkan sebagai konstanta di `config.py` dan dijelaskan di `docs/architecture.md`.
- Latensi memakai distribusi lognormal (mean server utama lebih tinggi dari mirror). Request 504 memiliki latensi sama dengan batas timeout.

### 5.2 `server_sim.py`
- Fungsi `kirim_request(req, mirror)` mensimulasikan I/O dengan `time.sleep(latensi * TIME_SCALE)`. Ini melepas GIL sehingga thread benar-benar bermanfaat.
- `TIME_SCALE` default 0.25 (di `config.py`) agar satu run sekuensial tidak terlalu lama. Dapat diubah lewat CLI.
- Mengembalikan record: `id`, `server` ("utama" atau "mirror-N"), `status` (200/502/504), `response_time_ms` (waktu terukur), `fallback` (bool).

### 5.3 `io_phase.py` (fase I/O, ThreadPoolExecutor)
- Memakai `ThreadPoolExecutor(max_workers=THREADS)`.
- Logika per request: kirim ke server utama. Jika status bukan 200, kirim ke mirror (satu kali). Catat hasil akhir beserta apakah memakai fallback.
- Mengembalikan daftar record (urut berdasarkan `id`) dan waktu fase I/O.

### 5.4 `cpu_phase.py` (fase CPU-bound, ProcessPoolExecutor)
- Memakai `ProcessPoolExecutor(max_workers=PROCESSES)`. Log dibagi menjadi `PROCESSES` chunk berukuran hampir sama.
- Analisis per chunk **harus benar-benar berat di CPU** agar speedup terlihat. Isi analisis:
  - statistik dasar: rata-rata, median, p95, p99, minimum, maksimum;
  - success rate dan distribusi kode status (200/502/504);
  - persentase fallback;
  - deteksi outlier dengan z-score;
  - checksum integritas tiap record (hash SHA-256 berulang sebanyak `CPU_WORK`);
  - bootstrap confidence interval rata-rata response time (resampling berulang, jumlah resample = `BOOTSTRAP_N`). Pakai `random.Random(seed_chunk)` lokal, bukan state global.
- `CPU_WORK` dan `BOOTSTRAP_N` dikalibrasi sehingga fase CPU sekuensial untuk 1510 data kira-kira 10-20 detik di laptop pemilik. Catat nilai akhir di `config.py` dan `docs/architecture.md`.
- Hasil chunk digabung menjadi statistik akhir. Statistik gabungan harus **setara** dengan hasil versi sekuensial (uji ini wajib ada di `tests/`).

### 5.5 `pipeline.py`
- `run_sequential(n)`: tanpa pool apa pun (loop biasa untuk I/O, lalu analisis satu proses). Ini baseline untuk speedup.
- `run_hybrid(n, threads, processes)`: fase I/O dengan thread, lalu fase CPU dengan proses.
- Waktu total diukur dengan `time.perf_counter()` dari awal fase I/O sampai agregasi selesai, **termasuk** biaya pembuatan pool. Catat juga `t_io` dan `t_cpu` terpisah.

### 5.6 `metrics.py`
- Throughput = jumlah request / waktu total (req/s).
- Speedup = T_sekuensial / T_hybrid, dengan baseline sekuensial **pada jumlah data yang sama**.
- Efisiensi (%) = Speedup / jumlah proses x 100. (Rumus ini sesuai contoh di soal: speedup 3.1 dengan 4 proses menghasilkan 77.5%.) Simpan juga `efisiensi_total_worker` = Speedup / (thread + proses) x 100 sebagai kolom tambahan, tetapi kolom utama untuk laporan adalah rumus pertama.

### 5.7 `main.py` (CLI)
Argumen: `--threads`, `--processes`, `--data`, `--mirrors`, `--time-scale`, `--seed`, `--mode {hybrid,sequential,compare}`.

Output terminal **wajib** (nama + NPM otomatis), format mengikuti soal:

```
Hybrid Project by: Fadhlan (247006111151)
Threads: 5 | Processes: 3 | Data: 1510
Total Time: X.XX s | Throughput: X.X req/s | Speedup: X.X | Efficiency: XX.X%
--- Contoh hasil analisis ---
Success rate: XX.X% | Fallback ke mirror: XX.X%
Response time (ms): mean=... p95=... p99=... | Outlier: ...
Status: 200=... 502=... 504=...
```

Nama lengkap yang dicetak disimpan sebagai konstanta `NAMA` di `config.py`. Tanyakan ke pemilik jika belum jelas.

## 6. Eksperimen

`experiments/run_experiments.py` menjalankan **10 konfigurasi** (sesuai tabel di soal) dan baseline sekuensial untuk tiap ukuran data. Setiap konfigurasi dijalankan **3 kali**, ambil **median** waktu.

| No | Thread | Proses | Data |
|---|---|---|---|
| 1 | 1 | 1 | 1510 |
| 2 | 2 | 1 | 1510 |
| 3 | 3 | 1 | 1510 |
| 4 | 5 | 1 | 1510 |
| 5 | 8 | 1 | 1510 |
| 6 | 5 | 2 | 1510 |
| 7 | 5 | 3 | 1510 |
| 8 | 5 | 4 | 1510 |
| 9 | 5 | 3 | 500 |
| 10 | 5 | 3 | 1000 |

Baseline sekuensial dijalankan untuk data 500, 1000, dan 1510.

`results.csv` berisi kolom: `no, threads, processes, data, waktu_s, t_io_s, t_cpu_s, throughput, speedup, efisiensi_pct, efisiensi_total_worker_pct, success_rate, fallback_pct`.

`plot_results.py` membuat tiga grafik wajib dari `results.csv`, disimpan ke `results/figures/`:
1. Waktu vs jumlah thread (konfigurasi 1-5, proses tetap 1).
2. Waktu vs jumlah proses (konfigurasi 4, 6, 7, 8, thread tetap 5).
3. Speedup vs konfigurasi (semua 10 konfigurasi).

Grafik harus punya judul, label sumbu dengan satuan, dan bahasa Indonesia.

## 7. Aturan kerja agent

1. Kerjakan bertahap sesuai urutan di bagian 8. Setelah tiap tahap: jalankan tes, perbarui `STATUS.md`, lalu commit.
2. **Jangan mengarang hasil eksperimen.** Semua angka di `results.csv` harus berasal dari run nyata di mesin ini. Jika sebuah run gagal, catat apa adanya di `STATUS.md`.
3. Hasil harus reproducible: seed yang sama menghasilkan rencana request yang sama.
4. Tidak ada request jaringan sungguhan. Tidak ada kredensial atau data pribadi di repo.
5. Kode bersih dan mudah dijelaskan: docstring singkat berbahasa Indonesia, nama variabel jelas, tidak terlalu rumit. Pemilik harus bisa menjelaskan kodenya sendiri saat ditanya dosen.
6. Jika ada keputusan desain yang tidak tercantum di sini, pilih opsi paling sederhana dan catat di `STATUS.md` bagian "Keputusan". Jangan mengubah parameter di bagian 2 tanpa persetujuan pemilik.
7. Jangan menambahkan MPI, framework web, atau dependensi besar.
8. Commit kecil dan sering dengan pesan jelas, misalnya `feat: tambah fase I/O dengan ThreadPoolExecutor`.

## 8. Urutan pengerjaan

1. Inisialisasi repo: struktur folder, `.gitignore`, `requirements.txt`, `README.md` awal, `STATUS.md`.
2. `config.py` dan `generator.py` (+ tes determinisme).
3. `server_sim.py` dan `io_phase.py`.
4. `cpu_phase.py` dan kalibrasi `CPU_WORK`/`BOOTSTRAP_N` (+ tes kesetaraan hasil paralel vs sekuensial).
5. `metrics.py`, `pipeline.py`, `main.py` dengan format output sesuai bagian 5.7.
6. `experiments/run_experiments.py`, jalankan, hasilkan `results.csv`.
7. `experiments/plot_results.py`, hasilkan tiga grafik.
8. `docs/architecture.md` dan `docs/hardware.md` (isi dengan spesifikasi perangkat di bagian 3 dan versi Python hasil `python --version`).
9. Rapikan `README.md`: cara instalasi, cara menjalankan, contoh output, ringkasan hasil.

## 9. Definition of done

- [ ] `python -m src.main` menampilkan Nama + NPM, jumlah thread dan proses, waktu total, throughput, speedup, efisiensi, dan contoh hasil analisis.
- [ ] Default menggunakan 5 thread, 3 proses, 1510 data, seed 247006111151.
- [ ] Minimal dua paradigma paralel dipakai (ThreadPool dan ProcessPool).
- [ ] `results/results.csv` berisi 10 konfigurasi dari run nyata, dan 3 grafik ada di `results/figures/`.
- [ ] Tes lulus (`python -m unittest` atau `pytest`).
- [ ] `STATUS.md` mencatat apa yang selesai, masalah yang ditemui, dan keputusan desain.
- [ ] README cukup jelas untuk dijalankan dari nol di Windows.
