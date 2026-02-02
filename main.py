import hashlib
import os

ALGORITHMS = {
    'SHA-256': hashlib.sha256,
    'SHA3-256': hashlib.sha3_256,
    'BLAKE2': hashlib.blake2b
}

def compute_hash(filepath, algorithm):
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Algoritma '{algorithm}' tidak didukung.")
    
    hasher = ALGORITHMS[algorithm]()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


if __name__ == "__main__":
    dummy_file = "test_hash.txt"
    with open(dummy_file, 'w') as f:
        f.write("Implementasi Algoritma Hash SHA-256 vs SHA-3 vs BLAKE2")
    
    print("=== Hash Comparison ===\n")
    for algo in ALGORITHMS:
        result = compute_hash(dummy_file, algo)
        print(f"{algo.upper():10} : {result}")
