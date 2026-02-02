# Komparasi Algoritma Hash: SHA-256 vs SHA-3 vs BLAKE2

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Status](https://img.shields.io/badge/Status-Scientific%20Benchmark-green.svg)

Proyek akhir mata kuliah **Kriptografi Terapan** (Kelompok 3 - II RKS A).
Repositori ini berisi *suite* pengujian ilmiah untuk membandingkan performa dan keamanan algoritma hash modern.

## 🎯 Fitur Utama
* **Scientific Benchmark:** Mengukur *Throughput* (MB/s) dan *Latency* (ns) dengan presisi tinggi.
* **Stability Analysis:** Menghitung *Standard Deviation* untuk memvalidasi kestabilan data.
* **Security Check:** Uji *Avalanche Effect* (Bit Flip Ratio) untuk memastikan kualitas pengacakan.
* **Statistical Significance:** Otomatis melakukan *Independent T-Test* (P-Value) untuk validitas perbandingan.
* **Resource Monitoring:** Memantau penggunaan CPU (%) dan Memori (MB) secara real-time.

## 📂 Struktur Folder
* `main.py`: Demo dasar hashing (SHA-256, SHA-3, BLAKE2).
* `benchmark.py`: Engine utama benchmarking.
* `visualize.py`: Generator grafik HD (Bar Chart dengan Error Bars).
* `generate_dummy.py`: Script pembuat data uji (1MB - 1GB).
* `dataset/`: Folder penyimpanan file dummy (tidak di-upload ke GitHub).
* `grafik_output/`: Folder output grafik hasil visualisasi.

## 🚀 Cara Menjalankan
1.  **Install Library:**
    ```bash
    pip install psutil tqdm scipy matplotlib seaborn pandas
    ```

2.  **Generate Data:**
    ```bash
    python generate_dummy.py
    ```

3.  **Jalankan Benchmark:**
    ```bash
    python benchmark.py
    ```
    *Output: File `hasil_god_mode.csv` dan `specs_info.txt` akan muncul.*

4.  **Buat Grafik:**
    ```bash
    python visualize.py
    ```
    *Output: Cek folder `grafik_output/`.*

## 📊 Algoritma yang Diuji
1.  **SHA-256:** Standar industri saat ini (Baseline).
2.  **SHA-3 (Keccak):** Standar terbaru NIST (FIPS 202).
3.  **BLAKE2b:** Algoritma *high-speed* modern (RFC 7693).

---
**Kelompok 3 - II RKS A**
* Lito (Lead Dev & Analyzer)
* Lino (Ops & Data)
* Hinggil (Researcher)
* Yosan (Documenter)