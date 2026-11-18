import os
import pandas as pd

def main():
    print("=== Menjalankan Skrip Automasi Analisis Anomali & Deduplikasi (Kartu #8) ===")

    log_path = "log-keputusan.csv"
    
    # 1. Pastikan file log-keputusan.csv tersedia
    if not os.path.exists(log_path):
        print(f"Error: {log_path} tidak ditemukan di direktori kerja.")
        return

    df_log = pd.read_csv(log_path)

    # 2. Definisikan aturan klasifikasi dan deduplikasi untuk Kartu #8
    # Berdasarkan analisis profil:
    # - Outlier Asli: Contohnya angka kelulusan SMA Papua (var1980) tahun 2015, 2018, 2019, 2020 yang sah secara statistik & riil di lapangan.
    # - Patahan Seri: Lonjakan serentak akibat perubahan definisi/metodologi nasional.
    # - Galat Input: Kesalahan ketik murni yang dikoreksi.
    # - Aturan Deduplikasi: Angka sama dari dua snapshot = konfirmasi (bukan duplikat salah); angka berbeda = revisi.
    
    kategori_summary = (
        "Klasifikasi anomali: (1) Outlier asli di Papua (var1980) dipertahankan karena fakta riil lapangan; "
        "(2) Patahan seri diidentifikasi akibat perubahan metodologi; "
        "(3) Galat input dikoreksi. "
        "Aturan deduplikasi: Nilai sama dari dua snapshot adalah konfirmasi, nilai berbeda adalah revisi."
    )

    # 3. Buat entri keputusan baru untuk K-003
    new_entry = {
        "id": "K-003",
        "tanggal": "2026-11-15",
        "nim": 124450072,
        "tahap": "analisis_anomali",
        "seri_kode": "sdg4_completion_dan_bps",
        "keputusan": kategori_summary,
        "alternatif_ditolak": "Mengubah atau menghapus seluruh nilai ekstrem (outlier asli & patahan seri) secara otomatis tanpa verifikasi",
        "alasan": "Menjaga integritas data historis wilayah dan membedakan antara kesalahan input murni dengan fluktuasi struktural yang sah",
        "dampak_baris": "Seluruh anomali terklasifikasi dan aturan deduplikasi resmi tercatat dalam log keputusan tanpa merusak baris data valid"
    }

    # Cek apakah K-003 sudah ada sebelumnya agar tidak duplikat
    if "K-003" in df_log["id"].values:
        print("Keputusan K-003 sudah tercatat sebelumnya di log-keputusan.csv.")
    else:
        # Tambahkan baris baru ke dataframe log
        df_log = pd.concat([df_log, pd.DataFrame([new_entry])], ignore_index=True)
        df_log.to_csv(log_path, index=False)
        print("Berhasil menambahkan keputusan K-003 otomatis ke log-keputusan.csv!")

    print("=== Proses Kartu #8 Selesai ===")

if __name__ == "__main__":
    main()