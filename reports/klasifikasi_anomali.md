# Klasifikasi Anomali, Patahan Seri, Galat Input, dan Deduplikasi (Kartu #8)

Dihasilkan oleh `src/silver/deteksi_anomali_bps.py` berdasarkan `data/silver/silver.parquet` dan `reports/profil_dan_anomali_bps.md`.

## 1. Pemeriksaan Galat Input (Rentang Satuan pada Semua Baris Silver)

- Total baris Silver diperiksa: **5,418**.
- Jumlah galat input ditemukan: **0 baris** (tidak ada nilai di luar rentang satuan sah).
- **Keputusan:** **Tidak ada perbaikan/perubahan nilai galat input** (`dampak_baris = 0`, tercatat di `log-keputusan.csv` `K-003`).

## 2. Klasifikasi Seluruh Calon Anomali dari Laporan Profil (`reports/profil_dan_anomali_bps.md`)

Sebanyak **18 calon anomali** pada laporan profil dihubungkan ke kategori dan alasannya (semuanya merupakan `outlier_asli` / `perbedaan_struktural` yang dipertahankan tanpa diubah, tercatat di `K-003`):

| Seri | Wilayah | Rincian | Periode | Nilai | Tanda_Profil | Kategori | Tindakan | Alasan_Keputusan | Ref_Log |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| var2595 (SDG 4.5.1 v2595) | KEP. RIAU | Tidak ada | 2020 | 109.35 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Fluktuasi rasio paritas kuintil SMA pada provinsi perkotaan/berpenduduk kecil (mis. DKI Jakarta, Bali, Kep. Riau, Kaltara, Sulbar); nilai sah dalam rentang rasio_x100. | K-003 |
| var2595 (SDG 4.5.1 v2595) | DKI JAKARTA | Tidak ada | 2020 | 114.78 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Fluktuasi rasio paritas kuintil SMA pada provinsi perkotaan/berpenduduk kecil (mis. DKI Jakarta, Bali, Kep. Riau, Kaltara, Sulbar); nilai sah dalam rentang rasio_x100. | K-003 |
| var2595 (SDG 4.5.1 v2595) | BALI | Tidak ada | 2025 | 109.59 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Fluktuasi rasio paritas kuintil SMA pada provinsi perkotaan/berpenduduk kecil (mis. DKI Jakarta, Bali, Kep. Riau, Kaltara, Sulbar); nilai sah dalam rentang rasio_x100. | K-003 |
| var2595 (SDG 4.5.1 v2595) | KALIMANTAN UTARA | Tidak ada | 2021 | 53.59 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Fluktuasi rasio paritas kuintil SMA pada provinsi perkotaan/berpenduduk kecil (mis. DKI Jakarta, Bali, Kep. Riau, Kaltara, Sulbar); nilai sah dalam rentang rasio_x100. | K-003 |
| var2595 (SDG 4.5.1 v2595) | SULAWESI BARAT | Tidak ada | 2021 | 112.73 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Fluktuasi rasio paritas kuintil SMA pada provinsi perkotaan/berpenduduk kecil (mis. DKI Jakarta, Bali, Kep. Riau, Kaltara, Sulbar); nilai sah dalam rentang rasio_x100. | K-003 |
| var2595 (SDG 4.5.1 v2595) | PAPUA BARAT | Tidak ada | 2025 | 46.8 | Di luar batas IQR | outlier_asli (perbedaan_struktural) | ditandai, nilai tidak diubah | Rasio APK kuintil terendah/tertinggi SMA di wilayah Papua mencerminkan kesenjangan akses ekonomi riil; nilai positif sah dalam satuan rasio_x100. | K-003 |
| var2595 (SDG 4.5.1 v2595) | PAPUA BARAT DAYA | Tidak ada | 2025 | 51.81 | Di luar batas IQR | outlier_asli (perbedaan_struktural) | ditandai, nilai tidak diubah | Rasio APK kuintil terendah/tertinggi SMA di wilayah Papua mencerminkan kesenjangan akses ekonomi riil; nilai positif sah dalam satuan rasio_x100. | K-003 |
| var2595 (SDG 4.5.1 v2595) | PAPUA SELATAN | Tidak ada | 2024 | 53.42 | Di luar batas IQR | outlier_asli (perbedaan_struktural) | ditandai, nilai tidak diubah | Rasio APK kuintil terendah/tertinggi SMA di wilayah Papua mencerminkan kesenjangan akses ekonomi riil; nilai positif sah dalam satuan rasio_x100. | K-003 |
| var2595 (SDG 4.5.1 v2595) | PAPUA PEGUNUNGAN | Tidak ada | 2024 | 44.0 | Di luar batas IQR | outlier_asli (perbedaan_struktural) | ditandai, nilai tidak diubah | Rasio APK kuintil terendah/tertinggi SMA di wilayah Papua mencerminkan kesenjangan akses ekonomi riil; nilai positif sah dalam satuan rasio_x100. | K-003 |
| var2595 (SDG 4.5.1 v2595) | PAPUA PEGUNUNGAN | Tidak ada | 2025 | 44.51 | Di luar batas IQR | outlier_asli (perbedaan_struktural) | ditandai, nilai tidak diubah | Rasio APK kuintil terendah/tertinggi SMA di wilayah Papua mencerminkan kesenjangan akses ekonomi riil; nilai positif sah dalam satuan rasio_x100. | K-003 |
| var2600 (SDG 4.5.1 v2600) | LAMPUNG | Tidak ada | 2025 | 165.5 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Rasio paritas gender APK PT tinggi (>160, mis. Kaltara, Sulut, Gorontalo, Sulbar, Lampung) karena jumlah mahasiswi lebih besar dan populasi dasar kelompok usia PT kecil; sah dalam rasio_x100. | K-003 |
| var2600 (SDG 4.5.1 v2600) | KALIMANTAN UTARA | Tidak ada | 2023 | 165.96 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Rasio paritas gender APK PT tinggi (>160, mis. Kaltara, Sulut, Gorontalo, Sulbar, Lampung) karena jumlah mahasiswi lebih besar dan populasi dasar kelompok usia PT kecil; sah dalam rasio_x100. | K-003 |
| var2600 (SDG 4.5.1 v2600) | KALIMANTAN UTARA | Tidak ada | 2024 | 161.15 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Rasio paritas gender APK PT tinggi (>160, mis. Kaltara, Sulut, Gorontalo, Sulbar, Lampung) karena jumlah mahasiswi lebih besar dan populasi dasar kelompok usia PT kecil; sah dalam rasio_x100. | K-003 |
| var2600 (SDG 4.5.1 v2600) | GORONTALO | Tidak ada | 2021 | 175.5 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Rasio paritas gender APK PT tinggi (>160, mis. Kaltara, Sulut, Gorontalo, Sulbar, Lampung) karena jumlah mahasiswi lebih besar dan populasi dasar kelompok usia PT kecil; sah dalam rasio_x100. | K-003 |
| var2600 (SDG 4.5.1 v2600) | SULAWESI BARAT | Tidak ada | 2024 | 170.21 | Di luar batas IQR | outlier_asli | ditandai, nilai tidak diubah | Rasio paritas gender APK PT tinggi (>160, mis. Kaltara, Sulut, Gorontalo, Sulbar, Lampung) karena jumlah mahasiswi lebih besar dan populasi dasar kelompok usia PT kecil; sah dalam rasio_x100. | K-003 |
| var2600 (SDG 4.5.1 v2600) | PAPUA SELATAN | Tidak ada | 2024 | 77.69 | Di luar batas IQR | outlier_asli (perbedaan_struktural) | ditandai, nilai tidak diubah | Rasio paritas gender APK PT di Papua Selatan/Pegunungan (<80) mencerminkan partisipasi perempuan lebih rendah dibanding laki-laki; nilai sah dalam rasio_x100. | K-003 |
| var2600 (SDG 4.5.1 v2600) | PAPUA SELATAN | Tidak ada | 2025 | 72.46 | Di luar batas IQR | outlier_asli (perbedaan_struktural) | ditandai, nilai tidak diubah | Rasio paritas gender APK PT di Papua Selatan/Pegunungan (<80) mencerminkan partisipasi perempuan lebih rendah dibanding laki-laki; nilai sah dalam rasio_x100. | K-003 |
| var2600 (SDG 4.5.1 v2600) | PAPUA PEGUNUNGAN | Tidak ada | 2025 | 62.0 | Di luar batas IQR | outlier_asli (perbedaan_struktural) | ditandai, nilai tidak diubah | Rasio paritas gender APK PT di Papua Selatan/Pegunungan (<80) mencerminkan partisipasi perempuan lebih rendah dibanding laki-laki; nilai sah dalam rasio_x100. | K-003 |

## 3. Patahan Definisi yang Dinyatakan Penerbit (`K-013`)

| seri_kode | periode_mulai | bukti_metadata | tindakan |
| --- | --- | --- | --- |
| var304 | 2007 | var.note var304: mulai 2007 APM mencakup pendidikan nonformal (paket A, B, C) | ditandai patahan_definisi; nilai tidak diubah (log K-013) |

## 4. Patahan Wilayah akibat Pemekaran Provinsi (`K-012`): 30 kejadian

Nilai provinsi induk sebelum periode ini mencakup wilayah provinsi pemekaran; sesudahnya tidak. Perubahannya ditandai sebagai `patahan_wilayah`, bukan outlier dan tidak diratakan.

| seri_kode | induk | wilayah_kode | periode | anak | nilai_sebelum | nilai_sesudah |
| --- | --- | --- | --- | --- | --- | --- |
| var2211 [umur=13-15] | Papua Barat | 9100 | 2024 | Papua Barat Daya | 97.42 | 95.61 |
| var2211 [umur=13-15] | Papua | 9400 | 2024 | Papua Selatan, Papua Tengah, Papua Pegunungan | 80.91 | 96.98 |
| var2211 [umur=16-18] | Papua Barat | 9100 | 2024 | Papua Barat Daya | 80.58 | 75.32 |
| var2211 [umur=16-18] | Papua | 9400 | 2024 | Papua Selatan, Papua Tengah, Papua Pegunungan | 64.15 | 80.38 |
| var2211 [umur=19-23] | Papua Barat | 9100 | 2024 | Papua Barat Daya | 35.74 | 31.18 |
| var2211 [umur=19-23] | Papua | 9400 | 2024 | Papua Selatan, Papua Tengah, Papua Pegunungan | 26.06 | 38.17 |
| var2211 [umur=7-12] | Papua Barat | 9100 | 2024 | Papua Barat Daya | 98.41 | 97.6 |
| var2211 [umur=7-12] | Papua | 9400 | 2024 | Papua Selatan, Papua Tengah, Papua Pegunungan | 83.61 | 97.09 |
| var2595 | Papua Barat | 9100 | 2024 | Papua Barat Daya | 103.66 | 63.44 |
| var2595 | Papua | 9400 | 2024 | Papua Selatan, Papua Tengah, Papua Pegunungan | 83.51 | 83.06 |
| var2600 | Papua Barat | 9100 | 2024 | Papua Barat Daya | 103.13 | 147.16 |
| var2600 | Papua | 9400 | 2024 | Papua Selatan, Papua Tengah, Papua Pegunungan | 80.66 | 115.81 |
| var304 [jenjang=sd] | Riau | 1400 | 2005 | Kepulauan Riau | 94.64 | 94.95 |
| var304 [jenjang=sd] | Kalimantan Timur | 6400 | 2015 | Kalimantan Utara | 96.81 | 97.0 |
| var304 [jenjang=sd] | Sulawesi Selatan | 7300 | 2006 | Sulawesi Barat | 92.04 | 91.08 |
| var304 [jenjang=sd] | Papua Barat | 9100 | 2024 | Papua Barat Daya | 94.52 | 95.15 |
| var304 [jenjang=sd] | Papua | 9400 | 2006 | Papua Barat | 81.05 | 78.11 |
| var304 [jenjang=sd] | Papua | 9400 | 2024 | Papua Selatan, Papua Tengah, Papua Pegunungan | 80.67 | 92.52 |
| var304 [jenjang=sm] | Riau | 1400 | 2005 | Kepulauan Riau | 47.73 | 50.51 |
| var304 [jenjang=sm] | Kalimantan Timur | 6400 | 2015 | Kalimantan Utara | 67.41 | 67.78 |
| var304 [jenjang=sm] | Sulawesi Selatan | 7300 | 2006 | Sulawesi Barat | 39.95 | 40.86 |
| var304 [jenjang=sm] | Papua Barat | 9100 | 2024 | Papua Barat Daya | 65.92 | 61.18 |
| var304 [jenjang=sm] | Papua | 9400 | 2006 | Papua Barat | 40.49 | 33.36 |
| var304 [jenjang=sm] | Papua | 9400 | 2024 | Papua Selatan, Papua Tengah, Papua Pegunungan | 48.32 | 61.33 |
| var304 [jenjang=smp] | Riau | 1400 | 2005 | Kepulauan Riau | 69.65 | 72.5 |
| var304 [jenjang=smp] | Kalimantan Timur | 6400 | 2015 | Kalimantan Utara | 78.96 | 79.06 |
| var304 [jenjang=smp] | Sulawesi Selatan | 7300 | 2006 | Sulawesi Barat | 59.1 | 60.27 |
| var304 [jenjang=smp] | Papua Barat | 9100 | 2024 | Papua Barat Daya | 74.7 | 72.1 |
| var304 [jenjang=smp] | Papua | 9400 | 2006 | Papua Barat | 44.95 | 47.36 |
| var304 [jenjang=smp] | Papua | 9400 | 2024 | Papua Selatan, Papua Tengah, Papua Pegunungan | 60.23 | 75.41 |

## 5. Deduplikasi, Snapshot, dan Uji Silang Format JSON vs CSV BPS

- Kunci primer kembar di Silver: **0**.
- Jumlah snapshot BPS di paket Kasus 8: **1 snapshot** (`2026-10-17`).
- **Aturan tertulis deduplikasi dua snapshot:** bila di kemudian hari tersedia dua snapshot untuk kunci yang sama, angka yang sama diperlakukan sebagai konfirmasi (ambil snapshot terbaru) dan angka berbeda diperlakukan sebagai revisi (dicatat di log).
- **Uji silang JSON vs CSV BPS:** JSON WebAPI dipilih sebagai sumber kanonik Silver karena memuat judul dan metadata lengkap; nilai keduanya identik (`Nilai_Berbeda = 0`):

| Berkas | Baris_JSON | Baris_CSV | Pasangan_Sama | Nilai_Berbeda |
| --- | --- | --- | --- | --- |
| sdg4_4_5_1_v2595 | 218 | 218 | 218 | 0 |
| sdg4_4_5_1_v2600 | 218 | 218 | 218 | 0 |
| sdg4_apm | 2376 | 2376 | 2376 | 0 |
| sdg4_aps | 1572 | 1572 | 1572 | 0 |
| sdg4_completion | 945 | 945 | 945 | 0 |