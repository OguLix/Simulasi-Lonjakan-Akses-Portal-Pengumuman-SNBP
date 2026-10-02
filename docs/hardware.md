# Perangkat Uji

- OS: Windows 11 (build 26200)
- CPU: Intel64 Family 6 Model 142 Stepping 11 (Whiskey Lake, sekelas
  Core i7-8565U), 4 core / 8 thread (`os.cpu_count() = 8`)
- Python: 3.14.7 (`python --version`)
- Dependensi: matplotlib (grafik saja)

Seluruh angka di `results/results.csv` berasal dari run nyata di mesin ini
(3x ulangan per konfigurasi, diambil median). Total run penuh ~55 menit.
Run dingin pertama fase CPU sempat lebih lambat (~2x) dibanding run hangat,
kemungkinan throttling/CPU berbagi di mesin uji.
