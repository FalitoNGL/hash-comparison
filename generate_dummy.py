import os

DATASET_DIR = "dataset"

FILE_SIZES = [
    (1, "1MB"),
    (10, "10MB"),
    (100, "100MB"),
    (1024, "1GB")
]


def create_dummy_files():
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

    print("=== Membuat File Dummy ===\n")

    for size_mb, label in FILE_SIZES:
        filename = f"test_{label}.dat"
        filepath = os.path.join(DATASET_DIR, filename)

        if os.path.exists(filepath):
            print(f"  [{label}] Sudah ada, skip.")
            continue

        print(f"  [{label}] Membuat file {size_mb} MB...", end=" ", flush=True)

        chunk = os.urandom(1024 * 1024)
        with open(filepath, 'wb') as f:
            for _ in range(size_mb):
                f.write(chunk)

        print("Selesai.")

    print(f"\n[SUCCESS] File dummy tersimpan di folder '{DATASET_DIR}/'.")


if __name__ == "__main__":
    create_dummy_files()
