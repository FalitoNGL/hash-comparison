import hashlib
import time
import tracemalloc
import csv
import os
import platform
import re
import threading
from statistics import mean, stdev

import psutil
from tqdm import tqdm

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


def get_system_info():
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
    info = get_system_info()
    
def print_and_save_specs():
    info = get_system_info()
    
    print("\n--- TAHAP 1: INFORMASI SISTEM ---")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    with open(SPECS_FILE, 'w', encoding='utf-8') as f:
        f.write("SPESIFIKASI SISTEM\n")
        f.write("=" * 50 + "\n")
        for key, value in info.items():
            f.write(f"{key}: {value}\n")
        f.write("=" * 50 + "\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return info


def compute_hash(filepath, algorithm):
    hasher = ALGORITHMS[algorithm]()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_hash_bytes(data, algorithm):
    hasher = ALGORITHMS[algorithm]()
    hasher.update(data)
    return hasher.hexdigest()


def run_benchmark(filepath, algorithm, show_details=False, file_label=""):
    file_size = os.path.getsize(filepath)
    times_ns = []
    memories = []
    cpu_readings = []
    
    for _ in range(WARMUP_ITERATIONS):
        _ = compute_hash(filepath, algorithm)
    
    iteration_results = []
    for i in range(BENCHMARK_ITERATIONS):
        tracemalloc.start()
        
        cpu_before = psutil.cpu_percent(interval=None)
        start_ns = time.perf_counter_ns()
        _ = compute_hash(filepath, algorithm)
        elapsed_ns = time.perf_counter_ns() - start_ns
        cpu_after = psutil.cpu_percent(interval=None)
        
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        times_ns.append(elapsed_ns)
        memories.append(peak_mem / (1024 * 1024))
        cpu_readings.append((cpu_before + cpu_after) / 2)
        
        iteration_results.append({
            'iteration': i + 1,
            'time_sec': elapsed_ns / 1e9,
            'time_ms': elapsed_ns / 1e6,
            'memory_mb': peak_mem / (1024 * 1024),
            'cpu_pct': (cpu_before + cpu_after) / 2
        })
    
    times_sec = [t / 1e9 for t in times_ns]
    
    mean_time = mean(times_sec)
    std_time = stdev(times_sec) if len(times_sec) > 1 else 0
    avg_memory = mean(memories)
    avg_cpu = mean(cpu_readings)
    
    file_size_mb = file_size / (1024 * 1024)
    throughput = file_size_mb / mean_time if mean_time > 0 else 0
    
    return {
        'iterations': iteration_results,
        'mean_time': mean_time,
        'std_time': std_time,
        'throughput': throughput,
        'cpu_usage': avg_cpu,
        'peak_memory': avg_memory
    }


def hex_to_bin(hex_str):
    return bin(int(hex_str, 16))[2:].zfill(len(hex_str) * 4)


def hamming_distance(bin1, bin2):
    return sum(b1 != b2 for b1, b2 in zip(bin1, bin2))


def avalanche_test(filepath, algorithm):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    hash_original = compute_hash_bytes(data, algorithm)
    
    modified = bytearray(data)
    modified[-1] ^= 0x01
    hash_modified = compute_hash_bytes(bytes(modified), algorithm)
    
    bin1 = hex_to_bin(hash_original)
    bin2 = hex_to_bin(hash_modified)
    
    diff = hamming_distance(bin1, bin2)
    total = len(bin1)
    
    return round((diff / total) * 100, 2)


def get_size_from_filename(filename):
    match = re.search(r'(\d+)(MB|GB)', filename, re.IGNORECASE)
    if match:
        size = int(match.group(1))
        unit = match.group(2).upper()
        if unit == "GB":
            size *= 1024
        return size
    return 0


def format_size(bytes_size):
    if bytes_size >= 1024**3:
        return f"{bytes_size / (1024**3):.2f} GB"
    elif bytes_size >= 1024**2:
        return f"{bytes_size / (1024**2):.2f} MB"
    elif bytes_size >= 1024:
        return f"{bytes_size / 1024:.2f} KB"
    return f"{bytes_size} B"


def main():
    print("\n=== BENCHMARK: SHA-256 vs SHA-3 vs BLAKE2 ===")
    
    print_and_save_specs()
    
    print("\n--- TAHAP 2: PERSIAPAN DATASET ---")
    
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        print(f"\n  [ERROR] Folder '{DATASET_DIR}/' kosong.")
        print(f"          Jalankan 'py generate_dummy.py' terlebih dahulu.")
        return
    
    files = [f for f in os.listdir(DATASET_DIR) 
             if os.path.isfile(os.path.join(DATASET_DIR, f))]
    
    if not files:
        print(f"\n  [ERROR] Folder '{DATASET_DIR}/' kosong.")
        return
    
    files.sort(key=get_size_from_filename)
    
    print(f"\n  Jumlah File     : {len(files)}")
    print(f"  Iterasi/Test    : {BENCHMARK_ITERATIONS}x (+ {WARMUP_ITERATIONS} warm-up)")
    print(f"  Algoritma       : {', '.join(ALGORITHMS.keys())}")
    print(f"\n  Daftar File:")
    for f in files:
        fpath = os.path.join(DATASET_DIR, f)
        fsize = os.path.getsize(fpath)
        print(f"    - {f} ({format_size(fsize)})")
    
    print("\n--- TAHAP 3: PROSES BENCHMARK ---")
    
    all_results = []
    all_raw_iterations = []
    test_number = 0
    total_tests = len(files) * len(ALGORITHMS)
    
    for file in files:
        filepath = os.path.join(DATASET_DIR, file)
        file_size = os.path.getsize(filepath)
        
        print(f"\n[ FILE: {file} ({format_size(file_size)}) ]")
        
        for algo in ALGORITHMS:
            test_number += 1
            print(f"\n  [{test_number}/{total_tests}] Algoritma: {algo}")
            print(f"  {'-' * 40}")
            
            try:
                result = run_benchmark(filepath, algo)
                
                print(f"  {'Iter':<6} {'Time (ms)':<12} {'Memory (MB)':<14} {'CPU (%)':<10}")
                print(f"  {'-' * 40}")
                
                for iter_data in result['iterations']:
                    print(f"  {iter_data['iteration']:<6} "
                          f"{iter_data['time_ms']:<12.4f} "
                          f"{iter_data['memory_mb']:<14.4f} "
                          f"{iter_data['cpu_pct']:<10.1f}")
                
                print(f"  {'-' * 40}")
                print(f"  Mean Time   : {result['mean_time']*1000:.4f} ms")
                print(f"  Std Dev     : {result['std_time']*1000:.4f} ms")
                print(f"  Throughput  : {result['throughput']:.2f} MB/s")
                
                avalanche = avalanche_test(filepath, algo)
                print(f"  Avalanche   : {avalanche}%")
                
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
                
                for iter_data in result['iterations']:
                    all_raw_iterations.append({
                        'Filename': file,
                        'Size_Bytes': file_size,
                        'Algorithm': algo,
                        'Iteration': iter_data['iteration'],
                        'Time_Sec': round(iter_data['time_sec'], 9),
                        'Time_Ms': round(iter_data['time_ms'], 4),
                        'Memory_MB': round(iter_data['memory_mb'], 4),
                        'CPU_Pct': round(iter_data['cpu_pct'], 1)
                    })
                
            except Exception as e:
                print(f"  [ERROR] {e}")
    
    print("\n--- TAHAP 4: RINGKASAN HASIL ---")
    
    algo_summary = {}
    for r in all_results:
        algo = r['Algorithm']
        if algo not in algo_summary:
            algo_summary[algo] = {
                'times': [], 'throughputs': [], 'avalanches': []
            }
        algo_summary[algo]['times'].append(r['Mean_Time_Sec'])
        algo_summary[algo]['throughputs'].append(r['Throughput_MBps'])
        algo_summary[algo]['avalanches'].append(r['Avalanche_Pct'])
    
    print(f"\n  {'Algoritma':<12} {'Avg Time (ms)':<16} {'Avg Throughput':<18} {'Avg Avalanche':<14}")
    print(f"  {'-' * 58}")
    
    for algo, data in algo_summary.items():
        avg_time = mean(data['times']) * 1000
        avg_throughput = mean(data['throughputs'])
        avg_avalanche = mean(data['avalanches'])
        print(f"  {algo:<12} {avg_time:<16.4f} {avg_throughput:<18.2f} {avg_avalanche:<14.2f}%")
    
    print("\n--- TAHAP 5: EXPORT DATA ---")
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Filename', 'Size_Bytes', 'Algorithm', 'Mean_Time_Sec', 
                      'Stdev_Time', 'Throughput_MBps', 'CPU_Usage_Pct', 
                      'Peak_Memory_MB', 'Avalanche_Pct']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)
    
    raw_csv = "hasil_benchmark_raw.csv"
    with open(raw_csv, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Filename', 'Size_Bytes', 'Algorithm', 'Iteration',
                      'Time_Sec', 'Time_Ms', 'Memory_MB', 'CPU_Pct']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_raw_iterations)
    
    print(f"\n  [OK] Hasil ringkasan   : {OUTPUT_CSV}")
    print(f"  [OK] Hasil per iterasi : {raw_csv}")
    print(f"  [OK] Spesifikasi sistem: {SPECS_FILE}")
    print(f"  [OK] Total pengujian   : {len(all_results)} ({len(all_raw_iterations)} iterasi)")
    
    print("\n=== BENCHMARK SELESAI ===\n")


if __name__ == "__main__":
    main()
