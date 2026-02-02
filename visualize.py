import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

INPUT_CSV = "hasil_benchmark.csv"
OUTPUT_DIR = "grafik_output"
DPI = 300

COLORS = {
    'SHA-256': '#2ecc71',
    'SHA3-256': '#e74c3c',
    'BLAKE2': '#3498db'
}


def setup_style():
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        'font.family': 'sans-serif'
    })


def load_data():
    df = pd.read_csv(INPUT_CSV)
    
    def size_to_label(size_bytes):
        size_mb = size_bytes / (1024 * 1024)
        if size_mb >= 1024:
            return f"{int(size_mb / 1024)} GB"
        else:
            return f"{int(size_mb)} MB"
    
    df['Size_Label'] = df['Size_Bytes'].apply(size_to_label)
    
    size_order = df.groupby('Size_Label')['Size_Bytes'].first().sort_values().index.tolist()
    df['Size_Label'] = pd.Categorical(df['Size_Label'], categories=size_order, ordered=True)
    
    return df


def plot_throughput_comparison(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sizes = df['Size_Label'].unique()
    algorithms = df['Algorithm'].unique()
    x = np.arange(len(sizes))
    width = 0.25
    
    for i, algo in enumerate(algorithms):
        algo_data = df[df['Algorithm'] == algo].sort_values('Size_Bytes')
        throughputs = algo_data['Throughput_MBps'].values
        stdevs = algo_data['Stdev_Time'].values * 100
        
        bars = ax.bar(x + (i - 1) * width, throughputs, width, 
                      label=algo, color=COLORS.get(algo, '#888888'),
                      yerr=stdevs, capsize=3, error_kw={'linewidth': 1})
    
    ax.set_xlabel('Ukuran File', fontweight='bold')
    ax.set_ylabel('Throughput (MB/s)', fontweight='bold')
    ax.set_title('Perbandingan Throughput: SHA-256 vs SHA3-256 vs BLAKE2', 
                 fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(sizes)
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    ax.grid(axis='y', alpha=0.3)
    
    for container in ax.containers:
        if hasattr(container, 'datavalues'):
            ax.bar_label(container, fmt='%.0f', padding=5, fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/01_throughput_comparison.png", dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  [OK] 01_throughput_comparison.png")


def plot_efficiency_matrix(df):
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for algo in df['Algorithm'].unique():
        algo_data = df[df['Algorithm'] == algo]
        
        sizes = algo_data['Peak_Memory_MB'].values * 2000
        
        scatter = ax.scatter(
            algo_data['Throughput_MBps'],
            algo_data['CPU_Usage_Pct'],
            s=sizes,
            c=COLORS.get(algo, '#888888'),
            label=algo,
            alpha=0.7,
            edgecolors='white',
            linewidth=2
        )
        
        for idx, row in algo_data.iterrows():
            ax.annotate(
                row['Size_Label'],
                (row['Throughput_MBps'], row['CPU_Usage_Pct']),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=8,
                alpha=0.7
            )
    
    ax.set_xlabel('Throughput (MB/s)', fontweight='bold')
    ax.set_ylabel('CPU Usage (%)', fontweight='bold')
    ax.set_title('Efficiency Matrix: Speed vs Resource Usage', fontweight='bold', pad=15)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    ax.invert_yaxis()
    
    ax.axhline(y=df['CPU_Usage_Pct'].mean(), color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=df['Throughput_MBps'].mean(), color='gray', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/02_efficiency_matrix.png", dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  [OK] 02_efficiency_matrix.png")


def plot_avalanche_consistency(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for algo in df['Algorithm'].unique():
        algo_data = df[df['Algorithm'] == algo].sort_values('Size_Bytes')
        
        ax.plot(
            algo_data['Size_Label'],
            algo_data['Avalanche_Pct'],
            marker='o',
            markersize=10,
            linewidth=2,
            label=algo,
            color=COLORS.get(algo, '#888888')
        )
        
        for idx, row in algo_data.iterrows():
            ax.annotate(
                f"{row['Avalanche_Pct']:.1f}%",
                (row['Size_Label'], row['Avalanche_Pct']),
                xytext=(0, 10),
                textcoords='offset points',
                ha='center',
                fontsize=9
            )
    
    ax.axhline(y=50, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Target Ideal (50%)')
    
    ax.axhspan(45, 55, alpha=0.1, color='green', label='Range Ideal (45-55%)')
    
    ax.set_xlabel('Ukuran File', fontweight='bold')
    ax.set_ylabel('Avalanche Effect (%)', fontweight='bold')
    ax.set_title('Konsistensi Avalanche Effect: Kualitas Pengacakan Hash', fontweight='bold', pad=15)
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(40, 60)
    
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/03_avalanche_consistency.png", dpi=DPI, bbox_inches='tight')
    plt.close()
    print("  [OK] 03_avalanche_consistency.png")


def main():
    print("\n" + "=" * 50)
    print("  VISUALIZE - Grafik HD untuk Jurnal")
    print("=" * 50)
    
    if not os.path.exists(INPUT_CSV):
        print(f"\n[ERROR] File '{INPUT_CSV}' tidak ditemukan.")
        print(f"        Jalankan 'py benchmark.py' terlebih dahulu.")
        return
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    setup_style()
    
    print(f"\n  Loading data dari '{INPUT_CSV}'...")
    df = load_data()
    print(f"  Total records: {len(df)}")
    
    print("\n  Generating grafik...")
    
    plot_throughput_comparison(df)
    plot_efficiency_matrix(df)
    plot_avalanche_consistency(df)
    
    print("\n" + "-" * 50)
    print(f"  [SUCCESS] Semua grafik tersimpan di folder '{OUTPUT_DIR}/'")
    print(f"  [INFO] Format: PNG, DPI: {DPI}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
