"""
Benchmark: SHA-256 vs SHA-3 vs BLAKE2
Scientific Grade - Tugas Akhir Kriptografi Terapan
"""

import hashlib
import time
import tracemalloc
import csv
import os
import platform
import re
import threading
from statistics import median, mean, stdev

# External libraries
import psutil
from tqdm import tqdm

# === KONFIGURASI ===
ALGORITHMS = {
    'SHA-256': hashlib.sha256,
    'SHA3-256': hashlib.sha3_256,
    'BLAKE2': hashlib.blake2b
}

DATASET_DIR = "dataset"
OUTPUT_CSV = "hasil_benchmark.csv"
SPECS_FILE = "specs_info.txt"
WARMUP_ITERATIONS = 2
BENCHMARK_ITERATIONS = 30
CHUNK_SIZE = 8192


# === 1. SYSTEM INFO ===
def get_system_info():
    """Ambil informasi sistem lengkap."""
    info = {
        'OS': f"{platform.system()} {platform.release()} (Build {platform.version()})",
        'Processor': platform.processor() or "Unknown",
        'Architecture': platform.machine(),
        'Python Version': platform.python_version(),
        'CPU Cores (Physical)': psutil.cpu_count(logical=False),
        'CPU Cores (Logical)': psutil.cpu_count(logical=True),
        'CPU Frequency': f"{psutil.cpu_freq().current:.0f} MHz" if psutil.cpu_freq() else "N/A",
        'RAM Total': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
        'RAM Available': f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
        'RAM Usage': f"{psutil.virtual_memory().percent:.1f}%",
    }
    
    # CPU name via WMIC (Windows)
    try:
        import subprocess
        result = subprocess.run(['wmic', 'cpu', 'get', 'name'], 
                                capture_output=True, text=True, timeout=5)
        cpu_name = result.stdout.strip().split('\n')[-1].strip()
        if cpu_name:
            info['Processor'] = cpu_name
    except:
        pass
    
    return info


def print_and_save_specs():
    """Print dan simpan spesifikasi sistem."""
    info = get_system_info()
    
    print("\n" + "=" * 65)
    print("  SPESIFIKASI SISTEM")
    print("=" * 65)
    for key, value in info.items():
        print(f"  {key}: {value}")
    print("=" * 65)
    
    with open(SPECS_FILE, 'w', encoding='utf-8') as f:
        f.write("SPESIFIKASI SISTEM\n")
        f.write("=" * 50 + "\n")
        for key, value in info.items():
            f.write(f"{key}: {value}\n")
        f.write("=" * 50 + "\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return info


# === 2. HASH FUNCTION ===
def compute_hash(filepath, algorithm):
    """Hitung hash file secara chunk-based."""
    hasher = ALGORITHMS[algorithm]()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_hash_bytes(data, algorithm):
    """Hitung hash dari bytes."""
    hasher = ALGORITHMS[algorithm]()
    hasher.update(data)
    return hasher.hexdigest()


# === 3. CPU MONITOR ===
class CPUMonitor:
    """Monitor CPU usage selama proses berjalan."""
    
    def __init__(self):
        self.cpu_readings = []
        self.running = False
        self.thread = None
    
    def start(self):
        self.cpu_readings = []
        self.running = True
        self.thread = threading.Thread(target=self._monitor)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        return mean(self.cpu_readings) if self.cpu_readings else 0.0
    
    def _monitor(self):
        while self.running:
            self.cpu_readings.append(psutil.cpu_percent(interval=0.1))


# === 4. BENCHMARK FUNCTION ===
def run_benchmark(filepath, algorithm):
    """
    Jalankan benchmark dengan standar scientific:
    - Warm-up: 2 iterasi (dibuang)
    - Iterasi: 30x dengan timing nanoseconds
    """
    file_size = os.path.getsize(filepath)
    times_ns = []
    memories = []
    cpu_readings = []
    
    # Warm-up (2 iterasi, tidak dicatat)
    for _ in range(WARMUP_ITERATIONS):
        _ = compute_hash(filepath, algorithm)
    
    # Benchmark iterations
    for _ in range(BENCHMARK_ITERATIONS):
        tracemalloc.start()
        
        # CPU snapshot sebelum
        cpu_before = psutil.cpu_percent(interval=None)
        
        start_ns = time.perf_counter_ns()
        _ = compute_hash(filepath, algorithm)
        elapsed_ns = time.perf_counter_ns() - start_ns
        
        # CPU snapshot sesudah
        cpu_after = psutil.cpu_percent(interval=None)
        
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        times_ns.append(elapsed_ns)
        memories.append(peak_mem / (1024 * 1024))  # MB
        cpu_readings.append((cpu_before + cpu_after) / 2)
    
    # Convert nanoseconds to seconds
    times_sec = [t / 1e9 for t in times_ns]
    
    # Calculate metrics
    mean_time = mean(times_sec)
    std_time = stdev(times_sec) if len(times_sec) > 1 else 0
    avg_memory = mean(memories)
    avg_cpu = mean(cpu_readings)
    
    # Throughput: MB/s
    file_size_mb = file_size / (1024 * 1024)
    throughput = file_size_mb / mean_time if mean_time > 0 else 0
    
    return {
        'mean_time': mean_time,
        'std_time': std_time,
        'throughput': throughput,
        'cpu_usage': avg_cpu,
        'peak_memory': avg_memory
    }


# === 5. AVALANCHE TEST ===
def hex_to_bin(hex_str):
    """Konversi hex ke binary string."""
    return bin(int(hex_str, 16))[2:].zfill(len(hex_str) * 4)


def hamming_distance(bin1, bin2):
    """Hitung jumlah bit berbeda."""
    return sum(b1 != b2 for b1, b2 in zip(bin1, bin2))


def avalanche_test(filepath, algorithm):
    """
    Uji Avalanche Effect:
    - Hash file asli
    - Flip 1 bit, hash lagi
    - Hitung % perbedaan (target ~50%)
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    
    hash_original = compute_hash_bytes(data, algorithm)
    
    # Flip 1 bit (bit terakhir dari byte terakhir)
    modified = bytearray(data)
    modified[-1] ^= 0x01
    
    hash_modified = compute_hash_bytes(bytes(modified), algorithm)
    
    bin1 = hex_to_bin(hash_original)
    bin2 = hex_to_bin(hash_modified)
    
    diff = hamming_distance(bin1, bin2)
    total = len(bin1)
    
    return round((diff / total) * 100, 2)


# === 6. UTILITY ===
def get_size_from_filename(filename):
    """Ekstrak ukuran dari nama file untuk sorting."""
    match = re.search(r'(\d+)(MB|GB)', filename, re.IGNORECASE)
    if match:
        size = int(match.group(1))
        unit = match.group(2).upper()
        if unit == "GB":
            size *= 1024
        return size
    return 0


# === 7. MAIN ===
def main():
    """Jalankan benchmark lengkap."""
    
    # Print header
    print("\n" + "=" * 65)
    print("  BENCHMARK: SHA-256 vs SHA3-256 vs BLAKE2b")
    print("  Tugas Akhir Kriptografi Terapan")
    print("=" * 65)
    
    # System specs
    print_and_save_specs()
    
    # Check dataset
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        print(f"\n[ERROR] Folder '{DATASET_DIR}/' kosong.")
        print(f"        Jalankan 'py generate_dummy.py' terlebih dahulu.")
        return
    
    files = [f for f in os.listdir(DATASET_DIR) 
             if os.path.isfile(os.path.join(DATASET_DIR, f))]
    
    if not files:
        print(f"\n[ERROR] Folder '{DATASET_DIR}/' kosong.")
        return
    
    files.sort(key=get_size_from_filename)
    
    print(f"\n  Files: {len(files)}")
    print(f"  Iterations: {BENCHMARK_ITERATIONS}x (+ {WARMUP_ITERATIONS} warm-up)")
    print(f"  Algorithms: {', '.join(ALGORITHMS.keys())}")
    print("\n" + "-" * 65)
    
    all_results = []
    total_tests = len(files) * len(ALGORITHMS)
    
    # Progress bar
    with tqdm(total=total_tests, desc="Benchmarking", unit="test", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
        
        for file in files:
            filepath = os.path.join(DATASET_DIR, file)
            file_size = os.path.getsize(filepath)
            
            for algo in ALGORITHMS:
                pbar.set_postfix_str(f"{file} - {algo}")
                
                try:
                    # Speed benchmark
                    result = run_benchmark(filepath, algo)
                    
                    # Avalanche test
                    avalanche = avalanche_test(filepath, algo)
                    
                    all_results.append({
                        'Filename': file,
                        'Size_Bytes': file_size,
                        'Algorithm': algo,
                        'Mean_Time_Sec': round(result['mean_time'], 6),
                        'Stdev_Time': round(result['std_time'], 6),
                        'Throughput_MBps': round(result['throughput'], 2),
                        'CPU_Usage_Pct': round(result['cpu_usage'], 1),
                        'Peak_Memory_MB': round(result['peak_memory'], 4),
                        'Avalanche_Pct': avalanche
                    })
                    
                except Exception as e:
                    tqdm.write(f"[ERROR] {file} - {algo}: {e}")
                
                pbar.update(1)
    
    # Export CSV
    print("\n" + "-" * 65)
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Filename', 'Size_Bytes', 'Algorithm', 'Mean_Time_Sec', 
                      'Stdev_Time', 'Throughput_MBps', 'CPU_Usage_Pct', 
                      'Peak_Memory_MB', 'Avalanche_Pct']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"\n  [SUCCESS] Hasil disimpan ke '{OUTPUT_CSV}'")
    print(f"  [SUCCESS] Spesifikasi sistem disimpan ke '{SPECS_FILE}'")
    print(f"  [INFO] Total: {len(all_results)} pengujian selesai.")
    print("\n" + "=" * 65)
    print("  BENCHMARK SELESAI!")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()

