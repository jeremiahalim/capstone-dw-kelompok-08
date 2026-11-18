import os
import pandas as pd

def proses_grid_bps():
    print("Mulai memproses grid 38 provinsi untuk Kartu #7...")
    
    # Path file input dari folder raw BPS
    input_path = 'data/raw/bps/2026-10-17/sdg4_completion.csv'
    
    if not os.path.exists(input_path):
        print(f"File tidak ditemukan di {input_path}. Periksa kembali path filenya.")
        return

    # Membaca data mentah
    df = pd.read_csv(input_path)
    print(f"Berhasil memuat data dari {input_path}")

    # Memastikan direktori silver ada
    os.makedirs('data/silver', exist_ok=True)
    
    # Menyimpan hasil ke folder silver
    output_path = 'data/silver/grid_38_provinsi_completion.csv'
    df.to_csv(output_path, index=False)
    
    print(f"File grid berhasil disimpan ke {output_path}")

if __name__ == "__main__":
    proses_grid_bps()