"""Konfigurasi default simulator (turunan NPM 247006111151)."""

NAMA = "Muhammad Fadhlan Aminullah"
NPM = 247006111151
SEED = NPM

# Turunan NPM: 51 mod 4 + 2 = 5 thread, 61 mod 3 + 2 = 3 proses, 151 x 10 = 1510 data.
THREADS = 5
PROCESSES = 3
N_DATA = 1510
MIRRORS = 3

# Skala sleep agar run sekuensial tidak terlalu lama (bisa di-override CLI).
TIME_SCALE = 0.25

# Profil lonjakan: peluang gagal naik pada 30%-70% antrean.
SURGE_START_FRAC = 0.30
SURGE_END_FRAC = 0.70
P_502_BASE = 0.08
P_502_SURGE = 0.25
P_504_BASE = 0.05
P_504_SURGE = 0.20
P_MIRROR_FAIL = 0.03

# Latensi lognormal (ms). Mean utama lebih tinggi dari mirror.
MU_UTAMA = 5.5
SIGMA_UTAMA = 0.6
MU_MIRROR = 5.0
SIGMA_MIRROR = 0.5
TIMEOUT_MS = 2000.0

# Beban CPU (dikalibrasi final di tahap 4 agar fase CPU sekuensial ~10-20 dtk).
CPU_WORK = 800
BOOTSTRAP_N = 200
