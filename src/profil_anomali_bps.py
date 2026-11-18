import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("reports/gambar", exist_ok=True)
os.makedirs("reports", exist_ok=True)

# Jalur file menyesuaikan folder hasil unduhan BPS di data/raw/bps/2026-10-17/
BASE_DIR = "data/raw/bps/2026-10-17"

files = {
    "var304 (APM)": os.path.join(BASE_DIR, "sdg4_apm.csv"),
    "var1980 (Completion)": os.path.join(BASE_DIR, "sdg4_completion.csv"),
    "var2211 (APS)": os.path.join(BASE_DIR, "sdg4_aps.csv"),
    "var2595 (SDG 4.5.1 v2595)": os.path.join(BASE_DIR, "sdg4_4_5_1_v2595.csv"),
    "var2600 (SDG 4.5.1 v2600)": os.path.join(BASE_DIR, "sdg4_4_5_1_v2600.csv"),
}

ringkasan_profil = []
daftar_anomali = []

for label, filename in files.items():
    # Cek apakah file ada di root, jika tidak cari di subfolder data/raw/
    filepath = filename
    if not os.path.exists(filepath):
        if os.path.exists(os.path.join("data", filename)):
            filepath = os.path.join("data", filename)
        elif os.path.exists(os.path.join("data", "raw", filename)):
            filepath = os.path.join("data", "raw", filename)
            
    df = pd.read_csv(filepath)
    var_id = df["var_id"].iloc[0]
    
    # 1. Statistik Deskriptif per Seri
    desc = df["nilai"].describe()
    q1 = desc["25%"]
    q3 = desc["75%"]
    iqr = q3 - q1
    batas_bawah = q1 - 1.5 * iqr
    batas_atas = q3 + 1.5 * iqr
    
    mean_val = desc["mean"]
    std_val = desc["std"]
    
    ringkasan_profil.append({
        "Seri": label,
        "var_id": var_id,
        "Jumlah_Baris": len(df),
        "Jumlah_Wilayah": df["wilayah"].nunique(),
        "Rentang_Tahun": f"{df['tahun'].min()}-{df['tahun'].max()}",
        "Rincian": ", ".join(df["turvar"].astype(str).unique()),
        "Mean": round(mean_val, 2),
        "Median": round(desc["50%"], 2),
        "Std": round(std_val, 2),
        "Min": round(desc["min"], 2),
        "Max": round(desc["max"], 2),
        "Batas_IQR": f"[{round(batas_bawah, 2)}, {round(batas_atas, 2)}]"
    })
    
    # 2. Deteksi Calon Anomali (IQR & Z-Score)
    df["z_score"] = (df["nilai"] - mean_val) / std_val
    for idx, row in df.iterrows():
        alasan = []
        if row["nilai"] < batas_bawah or row["nilai"] > batas_atas:
            alasan.append(f"Di luar batas IQR")
        if abs(row["z_score"]) > 3:
            alasan.append(f"|Z-score| > 3")
            
        if alasan:
            daftar_anomali.append({
                "Seri": label,
                "Wilayah": row["wilayah"],
                "Rincian": row["turvar"],
                "Periode": row["tahun"],
                "Nilai": row["nilai"],
                "Alasan_Ditandai": "; ".join(alasan)
            })
            
    # 3. Visualisasi Boxplot & Time Series
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    sns.boxplot(data=df, x="turvar", y="nilai", ax=axes[0], palette="Set2")
    axes[0].set_title(f"Boxplot {label}")
    axes[0].tick_params(axis='x', rotation=25)
    
    sns.lineplot(data=df, x="tahun", y="nilai", hue="turvar", marker="o", ax=axes[1])
    axes[1].set_title(f"Deret Waktu {label}")
    axes[1].legend(title="Rincian", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    nama_gambar = f"reports/gambar/profil_var{var_id}.png"
    plt.savefig(nama_gambar, dpi=150)
    plt.close()
    print(f"Grafik tersimpan: {nama_gambar}")

# Simpan hasil ringkasan ke Markdown
df_profil = pd.DataFrame(ringkasan_profil)
df_anomali = pd.DataFrame(daftar_anomali)

with open("reports/profil_dan_anomali_bps.md", "w", encoding="utf-8") as f:
    f.write("# Ringkasan Profil dan Calon Anomali 5 Seri BPS\n\n")
    f.write("## 1. Statistik Deskriptif per Seri\n\n")
    f.write(df_profil.to_markdown(index=False))
    f.write("\n\n## 2. Daftar Calon Anomali Terdeteksi\n\n")
    if not df_anomali.empty:
        f.write(df_anomali.to_markdown(index=False))
    else:
        f.write("Tidak ditemukan anomali ekstrem berdasarkan kriteria IQR/Z-score.\n")

print("Selesai! Laporan tersimpan di reports/profil_dan_anomali_bps.md")