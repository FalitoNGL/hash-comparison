# Komparasi Algoritma Hash: SHA-256 vs SHA-3 vs BLAKE2

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Status](https://img.shields.io/badge/Status-Scientific%20Benchmark-green.svg)

Proyek akhir mata kuliah **Kriptografi Terapan** (Kelompok 3 - II RKS A).
Repositori ini berisi *suite* pengujian ilmiah untuk membandingkan performa dan keamanan algoritma hash modern.

## 🎯 Fitur Utama
* **Scientific Benchmark:** Mengukur *Throughput* (MB/s) dengan 30 iterasi per test.
* **Stability Analysis:** Menghitung *Standard Deviation* untuk memvalidasi kestabilan data.
* **Security Check:** Uji *Avalanche Effect* (Bit Flip Ratio) untuk memastikan kualitas pengacakan.
* **Resource Monitoring:** Memantau penggunaan CPU (%) dan Memori (MB) secara real-time.
* **Detailed Output:** Menampilkan hasil per iterasi dengan output terpisah per tahap.

## 📂 Struktur Folder
| File | Deskripsi |
|------|-----------|
| `main.py` | Demo dasar hashing |
| `benchmark.py` | Engine utama benchmarking |
| `visualize.py` | Generator grafik HD |
| `generate_dummy.py` | Pembuat data uji (1MB - 1GB) |
| `dataset/` | Folder file dummy (tidak di-upload) |
| `grafik_output/` | Folder output grafik |

## 🚀 Cara Menjalankan

### 1. Install Dependencies
```bash
pip install psutil tqdm matplotlib seaborn pandas
```

### 2. Generate Data Uji
```bash
python generate_dummy.py
```

### 3. Jalankan Benchmark
```bash
python benchmark.py
```
Output: `hasil_benchmark.csv` dan `specs_info.txt`

### 4. Buat Visualisasi
```bash
python visualize.py
```
Output: Folder `grafik_output/`

## 📊 Algoritma yang Diuji
| Algoritma | Standar | Keterangan |
|-----------|---------|------------|
| SHA-256 | FIPS 180-4 | Baseline industri |
| SHA3-256 | FIPS 202 | Standar terbaru NIST |
| BLAKE2 | RFC 7693 | High-speed modern |

## 📈 Output Benchmark
Benchmark menampilkan 5 tahap terpisah:
1. **Tahap 1:** Informasi Sistem
2. **Tahap 2:** Persiapan Dataset
3. **Tahap 3:** Proses Benchmark (30 iterasi per test)
4. **Tahap 4:** Ringkasan Hasil
5. **Tahap 5:** Export Data

---
**Kelompok 3 - II RKS A**
* Lito (Lead Dev & Analyzer)
* Lino (Ops & Data)
* Hinggil (Researcher)
* Yosan (Documenter)