# Laporan tim Kelompok 8 (IJAZAH HUNTER), kasus 08 Kesetaraan dan penyelesaian pendidikan

Status: draf akhir Sprint 1 (bahan Demo Sprint 1). Seluruh angka ditarik ulang dari `data/silver/silver.parquet`, `reports/`, dan `log-keputusan.csv` (`K-001` s.d. `K-013`, total 12 keputusan).

## Ringkasan

Kasus 08 mengintegrasikan lima seri provinsi BPS (`var304`, `var2595`, `var2600`, `var1980`, `var2211`; 5,329 baris) dan dua seri nasional WDI (`SE.ENR.PRSC.FM.ZS`, `SE.PRM.CMPT.ZS`; 89 baris valid) menjadi tabel Silver pertama berisi **5,418 baris** dari **7 seri** dan **9 rincian unik**. Temuan kualitas data terpenting meliputi kode SDG dan satuan katalog awal yang keliru/kosong, perbedaan skala rasio BPS (`rasio_x100`) vs WDI (`rasio`), celah panel akibat pemekaran wilayah yang harus dipisahkan dari `missing` murni (Aceh 2005), serta patahan definisi APM 2007.

## Data dan lineage

Paket data mentah terdiri atas **15 berkas** di `data/raw/MANIFEST.csv`: snapshot BPS 17 Oktober 2026 (5 JSON berhalaman, 5 CSV, 1 `manifest_asal.json`) dan snapshot WDI 20 Oktober 2026 (1 berkas data + 3 berkas metadata). Pembaca `src/ekstraksi/` membaca 14 berkas data/metadata (10.865 baris mentah) tanpa galat; 6 berkas sumber masuk ke Silver (6 nilai unik `_berkas_raw`). Setiap baris Silver menyimpan `_berkas_raw` dan `_sha256_raw` dari `src.common.manifest.sha256_raw` sehingga dapat ditelusuri ke berkas mentahnya (contoh penelusuran terdokumentasi di `docs/data-dictionary.md`).
**Pilihan basis data dan perbandingan dengan dokumen JSON:** Lapis Bronze (`data/raw/`) tetap menyimpan respons JSON mentah sebagai dokumen karena unggul menjaga struktur bersarang WebAPI BPS/WDI dan seluruh metadata asli (`var.note`, `sourceNote`) untuk keperluan audit. Untuk lapis Silver dan Gold, tim memilih **DuckDB** (`data/gold/gudang.duckdb`, DDL di `src/gold/gudang.sql`, dimuat otomatis oleh `python pipeline.py` dan tidak di-commit karena `*.duckdb` masuk `.gitignore`) karena bersifat tanpa server (*embedded*), kolumnar/analitik (OLAP) untuk agregasi dan join panel 38 provinsi, terintegrasi langsung dengan Parquet, serta menegakkan kunci primer dan batasan `CHECK` di seluruh tabel (`seri`, `silver`, `gold_panel_provinsi`, `gold_tabel_nasional`, `gold_rekonsiliasi`).

## Masalah data dan penanganannya

Ringkasan seluruh masalah kualitas data yang ditemukan pada Sprint 1 (celah panel, anomali, patahan seri, deduplikasi/revisi, dan koreksi katalog) beserta keputusan, alternatif yang ditolak, dampak baris, dan rujukan `log-keputusan.csv`:

| Kategori | Masalah & Bukti | Keputusan Penanganan | Alternatif Ditolak | Dampak Baris / Sel | Ref Log |
|---|---|---|---|---|---|
| Koreksi katalog (SDG) | Tiga seri berkode `4.5.1`; dari judul JSON, `var304` adalah APM (bukan paritas) | `var2595` kuintil SMA (`4.5.1`), `var2600` gender PT (`4.5.1`), `var304` dikoreksi ke `4.1` | Menyimpulkan identitas hanya dari kode katalog | 2,376 baris (`var304`) | K-004 |
| Koreksi katalog (Satuan) | Satuan 5 seri BPS tercatat `tidak_ada`; rasio BPS berskala 32-260 sedangkan GPI WDI 0,77-1,02 | Tetapkan `persen` (APM/APS/penyelesaian), `rasio_x100` (paritas BPS), `rasio` (GPI WDI), `persen_apk` (penyelesaian SD WDI) | Membiarkan `tidak_ada` atau menyamakan satuan BPS dan WDI | 5,329 baris BPS | K-005 |
| Koreksi katalog (WDI) | Kode SDG dua seri WDI kosong di katalog awal | Diisi `4.5.1` (`SE.ENR.PRSC.FM.ZS`) dan `4.1.2` (`SE.PRM.CMPT.ZS`) dari `sumber46_indikator.json` | Membiarkan kode SDG WDI kosong | 2 seri | K-006 |
| Koreksi katalog (Catatan) | `var.note` `var2211` (APS) salah tempel berisi definisi disabilitas; belum terpetakan ke kode SDG | Abaikan `var.note` salah tempel; `var2211` dipertahankan di Silver tanpa kode SDG (`-`) sebagai konteks umur | Menyalin `var.note` ke kamus data atau membuang `var2211` | 0 baris diubah | K-007, K-008 |
| Transformasi rincian | Dimensi turvar BPS beragam dan tidak dapat dijumlahkan | Enkode menjadi `jenjang=sd/smp/sm/sma` dan `umur=7-12/13-15/16-18/19-23`, tanpa total buatan | Mempertahankan label mentah atau menjumlahkan antarjenjang | 9 rincian unik | K-009 |
| Nilai kosong WDI | Berkas JSON WDI memuat baris tahunan dengan `value = null` (24 di GPI, 19 di penyelesaian SD) | Baris `null` tidak dimasukkan ke tabel Silver | Menyimpan nilai `NaN` di Silver | 43 baris dibuang | K-010 |
| Celah panel & wilayah | Pemekaran provinsi 2003-2025 pada grid 38 provinsi x periode (5.776 sel; nasional `9999` dipisah) | Bedakan `belum_ada` (527 sel) dan `batas_lama` (69 sel) dari `missing`; gabung provinsi pakai kode bukan nama | Menganggap semua sel kosong sebagai `missing` atau bobot penduduk | 599 sel kosong grid | K-001, K-002 |
| Missing murni | Aceh (`1100`) tahun 2005 kosong pada `var304` (SD, SMP, SM) padahal provinsi sudah ada | Dikategorikan `missing` dan dibiarkan kosong (tidak diimputasi) | Interpolasi linear antartahun | 3 sel | K-011 |
| Patahan wilayah | Perubahan nilai provinsi induk pada tahun pertama provinsi pemekaran terbit | Ditandai `patahan_wilayah` di `reports/klasifikasi_anomali.md`, nilai asli tidak diratakan | Menandai sebagai outlier atau meratakan angka induk | 30 kejadian | K-012 |
| Patahan definisi | Mulai 2007, `var304` (APM) mencakup pendidikan nonformal paket A, B, C (`var.note`) | Ditandai `patahan_definisi` agar tren lintas 2006-2007 tidak dibanding mentah tanpa catatan | Membandingkan tren 2006-2007 tanpa catatan | 1 patahan | K-013 |
| Anomali & galat input | Profil IQR/z-score menandai 18 calon anomali (termasuk Papua & provinsi perkotaan/kecil); cek rentang satuan pada 5,418 baris | Seluruh calon anomali diklasifikasi sebagai outlier_asli / struktural dan dipertahankan; **0 galat input** ditemukan | Menghapus atau memangkas nilai ekstrem secara otomatis | 0 baris diubah | K-003 |
| Deduplikasi & revisi | Uji silang JSON vs CSV BPS identik (0 beda nilai); 0 duplikat kunci primer; baru 1 snapshot BPS (`2026-10-17`) | JSON WebAPI dipakai sebagai sumber kanonik; jika muncul snapshot baru, nilai sama = konfirmasi, nilai berbeda = revisi dicatat di log | Mengambil nilai secara acak atau menimpa tanpa catatan | 0 duplikat | K-003 |

## Integrasi dan rekonsiliasi

Integrasi Sprint 2 menyusun panel Gold (`data/gold/panel_provinsi.parquet`, **769 baris** berdasarkan 4 aturan tahap gold di `log-keputusan.csv` `K-014`-`K-017`), tabel nasional Gold (`data/gold/tabel_nasional.parquet`, **241 baris** dengan kolom `asal_angka`: 152 `baris_indonesia` + 89 `pembanding`, 0 agregat buatan), dan tabel rekonsiliasi (`data/gold/rekonsiliasi.parquet`, **101 baris**, seluruh periode tanpa pasangan tetap ditampilkan dan selisih tidak dihapus).
### Ringkasan Pasangan & Kategori Penjelasan

| ID | Seri Utama (BPS) | Pembanding (WDI) | Total Baris | Berpasangan | Besar Selisih | Kategori |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | var1980 [jenjang=sd] | SE.PRM.CMPT.ZS | 47 | 9 | median absolut 7.38 pp (-17.46 di 2015 -> -2.12 di 2023) | definisi |
| P2 | var2600 (PT) | SE.ENR.PRSC.FM.ZS (SD+menengah) | 48 | 0 | - (0 tahun beririsan) | definisi |
| P3 | var2595 (kuintil SMA) | tidak_ada | 6 | 0 | - (tanpa pembanding) | definisi |
### Rincian Selisih Pasangan Aktif P1 (2015-2023)
Pada seluruh **9 tahun beririsan**, WDI `SE.PRM.CMPT.ZS` selalu berada di atas BPS `var1980 [jenjang=sd]` (median selisih absolut **7.38 poin persen**, signed median `-7.38` poin persen). Selisih menyempit konsisten dari **-17.46 pp** (2015) menjadi **-2.12 pp** (2023):
| periode | nilai_utama | nilai_pembanding | selisih | selisih_absolut | kategori_selisih |
| --- | --- | --- | --- | --- | --- |
| 2015 | 91.44 | 108.9 | -17.4567 | 17.4567 | definisi |
| 2016 | 93.88 | 107.21 | -13.3334 | 13.3334 | definisi |
| 2017 | 95.25 | 104.77 | -9.5235 | 9.5235 | definisi |
| 2018 | 94.68 | 102.63 | -7.9475 | 7.9475 | definisi |
| 2019 | 95.48 | 102.86 | -7.3762 | 7.3762 | definisi |
| 2020 | 96.0 | 102.12 | -6.1197 | 6.1197 | definisi |
| 2021 | 97.37 | 103.37 | -5.9968 | 5.9968 | definisi |
| 2022 | 97.82 | 102.07 | -4.2481 | 4.2481 | definisi |
| 2023 | 97.83 | 99.95 | -2.1222 | 2.1222 | definisi |
### Penjelasan Kategori Selisih
- **`definisi` (P1 `var1980 [jenjang=sd]` vs `SE.PRM.CMPT.ZS`):** BPS mengukur persentase penduduk kelompok umur 13-15 tahun yang telah menyelesaikan SD berbasis survei rumah tangga Susenas (`persen`, batas atas 100%), sedangkan WDI mengukur *gross intake ratio* ke kelas terakhir SD tanpa memandang umur dari data administratif UIS (`persen_apk`, dapat melebihi 100% saat banyak siswa masuk lebih awal/terlambat, terlihat pada 2015-2022). Penyempitan selisih mencerminkan berkurangnya porsi siswa di luar usia resmi kelas 6 SD.
- **`definisi` (P2 `var2600` vs `SE.ENR.PRSC.FM.ZS`):** Dilaporkan sebagai *definisi berbeda* karena jenjang berbeda (Perguruan Tinggi pada BPS 2020-2025 vs gabungan SD+menengah pada WDI 1970-2018), skala berbeda (`rasio_x100` vs `rasio`), dan tidak ada tahun beririsan (0 tahun).
- **`definisi` (P3 `var2595`):** Mengukur paritas kuintil pengeluaran jenjang SMA yang tidak memiliki seri pembanding kuintil pada paket WDI. Analisis revisi 142 rilis arsip WDI (`vintage`) dilanjutkan pada Sprint 3.
## Validasi dan reproduksibilitas

- **Skema minimal Silver:** `python -m src.common.skema data/silver/silver.parquet` berakhir **LOLOS** (5,418 baris, 7 seri, 39 wilayah, 6 berkas sumber, 0 duplikat kunci).
- **Validasi dasar Pandera & aturan Kasus 08 (`reports/validasi.md`):** **10/10 aturan LOLOS, 0 GAGAL** (mencakup keunikan kunci, satuan baku per seri, rentang nilai, rasio paritas masuk akal, tanpa total buatan, dan penyelesaian SMA tidak melebihi SD).
- **Kamus data & penyimpanan SQL:** Semua 11 kolom Silver dan contoh penelusuran lineage tercatat di `docs/data-dictionary.md`; pemuatan Silver ke DuckDB dan perbandingan dokumen JSON disiapkan di `src/gold/` (Sprint 1-2).

## Pembagian kerja

| Anggota | NIM | Komponen | Tugas Sampingan | Bagian Laporan |
|---|---|---|---|---|
| Jeremia Halim | 124450101 | Ekstraksi dan lineage (`src/ekstraksi/`) | Reproduksi dan demo | Data dan lineage |
| Wielman Itolo Halawa | 124450072 | Profil dan pembersihan (`src/silver/`) | Koordinator | Masalah data (celah panel, anomali, patahan) |
| Faiza Try Anjani | 124450075 | Transformasi dan panel (`src/silver/`) |  Analisis utama | Ringkasan, masalah data (katalog/satuan), draf `reports/tim.md` |
| Caesar Ozora Alrando | 124450017 | Integrasi, penyimpanan, dan skala (`src/gold/`) | Penjaga data dan evaluasi | Integrasi dan rekonsiliasi |
| Bima Ekayasa | 124450106 | Validasi dan dokumentasi (`src/validasi/`, `docs/`) | Integrator | Validasi, kamus data, dan reproduksibilitas |
