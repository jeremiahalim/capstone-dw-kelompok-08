import os
import json
import pandas as pd

# Path file JSON sumber WDI
file_path = "data/raw/wdi/2026-10-20/data/kelompok-03-hal-01.json"
print(f"Membaca file JSON: {file_path}")

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    flattened_data = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, list):
                for subitem in item:
                    if isinstance(subitem, dict):
                        flattened_data.append(subitem)
            elif isinstance(item, dict):
                flattened_data.append(item)
                
    df = pd.json_normalize(flattened_data)
    
    target_series = ['SE.ENR.PRSC.FM.ZS', 'SE.PRM.CMPT.ZS']
    profil_list = []
    
    for series in target_series:
        sub_df = df[df['indicator.id'] == series]
        if not sub_df.empty:
            nama_indikator = sub_df['indicator.value'].iloc[0]
            min_tahun = sub_df['date'].min()
            max_tahun = sub_df['date'].max()
            total_obs = len(sub_df)
            valid_obs = sub_df['value'].dropna().count()
            
            profil_list.append({
                'Indicator Code': series,
                'Indicator Name': nama_indikator,
                'Start Year': min_tahun,
                'End Year': max_tahun,
                'Total Observations': total_obs,
                'Valid Observations': valid_obs
            })

    df_profil = pd.DataFrame(profil_list)
    
    # Pastikan direktori reports ada
    os.makedirs('reports', exist_ok=True)
    
    # Simpan ringkasan ke CSV
    output_csv = 'reports/tabel_ketersediaan_wdi.csv'
    df_profil.to_csv(output_csv, index=False)
    print(f"\nTabel ketersediaan berhasil disimpan ke: {output_csv}")
    
    # Buat laporan markdown
    report_content = f"""# Laporan Profil Seri Pembanding Nasional (WDI)
Tanggal Analisis: 2026-11-15

## 1. Tabel Ketersediaan Seri x Periode
Tabel berikut merangkum ketersediaan data untuk seri pembanding WDI yang dianalisis:

| Indicator Code | Indicator Name | Start Year | End Year | Total Observations | Valid Observations |
|----------------|----------------|------------|----------|-------------------|--------------------|
"""
    for _, row in df_profil.iterrows():
        report_content += f"| {row['Indicator Code']} | {row['Indicator Name']} | {row['Start Year']} | {row['End Year']} | {row['Total Observations']} | {row['Valid Observations']} |\n"

    report_content += """
## 2. Analisis Perbandingan & Kandidat Sebanding
* **SE.ENR.PRSC.FM.ZS (Gender Parity Index / GPI Pendidikan Primer & Sekunder)**: 
  * *Alasan Kelayakan*: Seri ini cocok digunakan sebagai pembanding nasional untuk melihat kesenjangan gender (*gender parity*) yang sejalan dengan indikator utama pendidikan pada jenjang terkait.
* **SE.PRM.CMPT.ZS (Primary Completion Rate, Total %)**: 
  * *Alasan Kelayakan*: Memiliki cakupan historis yang panjang (1960–2025) dan memberikan metrik persentase penyelesaian pendidikan dasar yang sangat akurat untuk disandingkan dengan data rujukan BPS.
"""
    
    output_md = 'reports/profil_seri_pembanding.md'
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"Laporan Markdown berhasil disimpan ke: {output_md}")

else:
    print(f"File {file_path} tidak ditemukan.")