# Laporan tim Kelompok 8 (IJAZAH HUNTER), kasus 08 Kesetaraan dan penyelesaian pendidikan

Status: draf akhir Sprint 1 (bahan Demo Sprint 1). Seluruh angka ditarik ulang dari `data/silver/silver.parquet`, `reports/`, dan `log-keputusan.csv` (`K-001` s.d. `K-013`, total 12 keputusan).

## Ringkasan

Kasus 08 mengintegrasikan lima seri provinsi BPS (`var304`, `var2595`, `var2600`, `var1980`, `var2211`; 5,329 baris) dan dua seri nasional WDI (`SE.ENR.PRSC.FM.ZS`, `SE.PRM.CMPT.ZS`; 89 baris valid) menjadi tabel Silver pertama berisi **5,418 baris** dari **7 seri** dan **9 rincian unik**. Temuan kualitas data terpenting meliputi kode SDG dan satuan katalog awal yang keliru/kosong, perbedaan skala rasio BPS (`rasio_x100`) vs WDI (`rasio`), celah panel akibat pemekaran wilayah yang harus dipisahkan dari `missing` murni (Aceh 2005), serta patahan definisi APM 2007.

## Data dan lineage

Paket data mentah terdiri atas **15 berkas** di `data/raw/MANIFEST.csv`: snapshot BPS 17 Oktober 2026 (5 JSON berhalaman, 5 CSV, 1 `manifest_asal.json`) dan snapshot WDI 20 Oktober 2026 (1 berkas data + 3 berkas metadata). Pembaca `src/ekstraksi/` membaca 14 berkas data/metadata (10.865 baris mentah) tanpa galat; 6 berkas sumber masuk ke Silver (6 nilai unik `_berkas_raw`). Setiap baris Silver menyimpan `_berkas_raw` dan `_sha256_raw` dari `src.common.manifest.sha256_raw` sehingga dapat ditelusuri ke berkas mentahnya (contoh penelusuran terdokumentasi di `docs/data-dictionary.md`).

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

- **P1 (sebanding dengan catatan):** `var1980 [jenjang=sd]` baris nasional (`9999`) vs WDI `SE.PRM.CMPT.ZS` beririsan **9 tahun** (2015-2023). Keduanya berkode SDG 4.1.2, tetapi berbeda metode (survei Susenas kohort umur 13-15 tahun dalam `persen` vs *gross intake ratio* administratif UIS dalam `persen_apk` yang dapat >100%).
- **P2 (konteks / definisi berbeda):** `var2600` (paritas gender APK PT, 2020-2025) vs WDI `SE.ENR.PRSC.FM.ZS` (GPI gabungan SD+SMP/SMA, valid 1970-2018) memiliki **0 tahun irisan** dan berbeda jenjang.
- **P3 (konteks, tanpa pembanding):** `var2595` (paritas kuintil APK SMA) tidak memiliki seri pembanding pada paket WDI. Analisis selisih lengkap dan revisi arsip WDI 142 rilis dikerjakan pada Sprint 2.

## Validasi dan reproduksibilitas

- **Skema minimal Silver:** `python -m src.common.skema data/silver/silver.parquet` berakhir **LOLOS** (5,418 baris, 7 seri, 39 wilayah, 6 berkas sumber, 0 duplikat kunci).
- **Validasi dasar Pandera & aturan Kasus 08 (`reports/validasi.md`):** **10/10 aturan LOLOS, 0 GAGAL** (mencakup keunikan kunci, satuan baku per seri, rentang nilai, rasio paritas masuk akal, tanpa total buatan, dan penyelesaian SMA tidak melebihi SD).
- **Kamus data & penyimpanan SQL:** Semua 11 kolom Silver dan contoh penelusuran lineage tercatat di `docs/data-dictionary.md`; pemuatan Silver ke DuckDB dan perbandingan dokumen JSON disiapkan di `src/gold/` (Sprint 1-2).

## Pembagian kerja

| Anggota | NIM | Komponen | Tugas Sampingan | Bagian Laporan |
|---|---|---|---|---|
| Jeremia Halim | 124450101 | Ekstraksi dan lineage (`src/ekstraksi/`) | Pengelola repo | Data dan lineage |
| Wielman Itolo Halawa | 124450072 | Profil dan pembersihan (`src/silver/`) | Koordinator | Masalah data (celah panel, anomali, patahan) |
| Faiza Try Anjani | 124450075 | Transformasi dan panel (`src/silver/`) | Analis | Ringkasan, masalah data (katalog/satuan), draf `reports/tim.md` |
| Caesar Ozora Alrando | 124450017 | Integrasi, penyimpanan, dan skala (`src/gold/`) | - | Integrasi dan rekonsiliasi |
| Bima Ekayasa | 124450106 | Validasi dan dokumentasi (`src/validasi/`, `docs/`) | Integrator | Validasi, kamus data, dan reproduksibilitas |
