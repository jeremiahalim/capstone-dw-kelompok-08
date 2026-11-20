# Laporan Profil Seri Pembanding Nasional (WDI)

## 1. Ringkasan Ketersediaan Data Valid (Non-Null)

JSON World Bank mencantumkan seluruh deret tahun 1960-2025, tetapi nilai `null` berarti tidak ada pengamatan. Ringkasan berikut dihitung **hanya dari observasi valid (non-null)** yang benar-benar terbaca. Tabel lengkap seri x periode x rincian tersimpan di `reports/tabel_ketersediaan_wdi.csv`.

| seri_kode | nama_indikator | wilayah | rincian | satuan | rentang_mentah_json | rentang_valid | total_baris_json | observasi_valid | observasi_null | tahun_bolong_dalam_rentang | nilai_min | nilai_max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SE.ENR.PRSC.FM.ZS | School enrollment, primary and secondary (gross), gender parity index (GPI) | Indonesia | rasio_perempuan_laki_laki; jenjang=primer_sekunder (gross); wilayah nasional | rasio | 1960-2025 | 1970-2018 | 66 | 42 | 24 | 1979, 1980, 1985, 1986, 1987, 1997, 1998 | 0.7728 | 1.0223 |
| SE.PRM.CMPT.ZS | Primary completion rate, total (% of relevant age group) | Indonesia | total; jenjang=sd_primer (gross_intake_last_grade); wilayah nasional | persen_apk | 1960-2025 | 1972-2023 | 66 | 47 | 19 | 1979, 1980, 1998, 1999, 2000 | 48.4563 | 109.5452 |

## 2. Irisan Tahun (Overlap) dengan Seri Utama BPS

| Seri WDI | Seri BPS | Rincian BPS | Periode Valid WDI | Periode BPS (Indonesia) | Jumlah Tahun Irisan | Tahun Beririsan |
| --- | --- | --- | --- | --- | --- | --- |
| SE.ENR.PRSC.FM.ZS | var1980 | SD / Sederajat, SMA / Sederajat, SMP / Sederajat | 1970-2018 | 2015-2023 | 4 | 2015-2018 (2015, 2016, 2017, 2018) |
| SE.ENR.PRSC.FM.ZS | var2211 | 13-15, 16-18, 19-23, 7-12 | 1970-2018 | 2015-2025 | 4 | 2015-2018 (2015, 2016, 2017, 2018) |
| SE.ENR.PRSC.FM.ZS | var2595 | Tidak ada | 1970-2018 | 2020-2025 | 0 | Tidak ada irisan (0 tahun) |
| SE.ENR.PRSC.FM.ZS | var2600 | Tidak ada | 1970-2018 | 2020-2025 | 0 | Tidak ada irisan (0 tahun) |
| SE.ENR.PRSC.FM.ZS | var304 | SD/sederajat, SM/sederajat, SMP/sederajat | 1970-2018 | 2003-2025 | 16 | 2003-2018 (2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018) |
| SE.PRM.CMPT.ZS | var1980 | SD / Sederajat, SMA / Sederajat, SMP / Sederajat | 1972-2023 | 2015-2023 | 9 | 2015-2023 (2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023) |
| SE.PRM.CMPT.ZS | var2211 | 13-15, 16-18, 19-23, 7-12 | 1972-2023 | 2015-2025 | 9 | 2015-2023 (2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023) |
| SE.PRM.CMPT.ZS | var2595 | Tidak ada | 1972-2023 | 2020-2025 | 4 | 2020-2023 (2020, 2021, 2022, 2023) |
| SE.PRM.CMPT.ZS | var2600 | Tidak ada | 1972-2023 | 2020-2025 | 4 | 2020-2023 (2020, 2021, 2022, 2023) |
| SE.PRM.CMPT.ZS | var304 | SD/sederajat, SM/sederajat, SMP/sederajat | 1972-2023 | 2003-2025 | 21 | 2003-2023 (2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023) |

## 3. Evaluasi Kandidat Rincian Sebanding & Batasannya (untuk Tahap 6)

### A. SE.PRM.CMPT.ZS vs `var1980` (Tingkat Penyelesaian Pendidikan BPS)

- **Kandidat yang dapat dibandingkan:** `var1980` khusus rincian **SD/Sederajat (`jenjang=sd`)** pada baris nasional **Indonesia (`wilayah_kode = 9999`)**.
- **Rincian yang TIDAK dapat dibandingkan:** `SMP/Sederajat` dan `SMA/Sederajat` pada `var1980` (karena `SE.PRM.CMPT.ZS` khusus jenjang pendidikan dasar/SD), serta seluruh baris tingkat provinsi (karena WDI hanya tersedia di tingkat nasional).
- **Alasan & Batasan Definisi (TIDAK identik secara definisi/metode):**
  - **Definisi WDI (`SE.PRM.CMPT.ZS`, `sourceNote`):** Primary completion rate, or gross intake ratio to the last grade of primary education, is the number of new entrants (enrollments minus repeaters) in the last grade of primary education, regardless of age, divided by the population at the entrance age for the last grade of primary education. Data limitations preclude adjusting for students who drop out during the final year of primary education.
  - **Definisi BPS (`var1980`, `var.note`):** <p>
<strong>Definisi Indikator:</strong> Indikator ini mengukur persentase anak dan remaja yang berhasil menyelesaikan jenjang pendidikan yang sesuai dengan rentang usianya. Rentang usia yang termasuk dalam perhitungan ini adalah antara 1 sampai dengan 3 tahun sejak usia kelulusan jenjang pendidikan pada umumnya. Berdasarkan usia wajib belajar yang dimulai sejak 7 tahun, maka dengan asumsi siswa belajar penuh waktu dan tidak tinggal kelas, mereka lulus SD/sederajat pada usia sekitar 12 tahun. Oleh karena itu rentang usia yang digunakan untuk penghitungan tingkat ketuntasan SD/sederajat adalah anak atau remaja usia 13 tahun (12 + 1 tahun) sampai dengan 15 tahun (12 + 3 tahun). Tingkat penyelesaian yang mencapai atau mendekati 100% menunjukkan bahwa hampir seluruh anak-anak dan remaja telah menyelesaikan jenjang pendidikan yang seharusnya atau sesuai usia mereka, tanpa keterlambatan yang signifikan atau berarti.<br />
<br />
<strong>Sumber Data:</strong> Susenas KOR</p>
- **Implikasi untuk Tahap 6:** Keduanya sama-sama memantau penyelesaian jenjang SD di tingkat nasional dan memiliki irisan periode (lihat tabel irisan di atas). Namun, secara metodologi keduanya **berbeda definisi dan metode**: `var1980` BPS adalah *completion rate* berbasis survei rumah tangga (Susenas) pada kohort umur 3-5 tahun di atas usia resmi kelulusan SD sehingga nilainya selalu di rentang **0-100%** (`persen`), sedangkan `SE.PRM.CMPT.ZS` WDI adalah *gross intake ratio to the last grade of primary* berbasis data administratif/estimasi populasi tanpa batas usia sehingga nilainya **dapat melebihi 100%** (`persen_apk`). Oleh karena itu, pada rekonsiliasi Tahap 6 keduanya tetap disandingkan sebagai pasangan utama, tetapi selisih yang muncul tidak dihapus dan dikategorikan sebagai **definisi berbeda** dan/atau **metode berbeda**.

### B. SE.ENR.PRSC.FM.ZS vs Seri 4.5.1 dan Partisipasi BPS

- **Definisi WDI (`SE.ENR.PRSC.FM.ZS`, `sourceNote`):** Gender parity index for gross enrollment ratio in primary and secondary education is the ratio of girls to boys enrolled at primary and secondary levels in public and private schools.
- **Kandidat yang dapat dibandingkan:** **Tidak ada rincian seri utama BPS yang sebanding langsung.**
- **Batasan terhadap masing-masing seri BPS:**
  - **`var2595` (Paritas Kuintil APK SMA, 2020-2025):** Tidak sebanding karena berbeda **jenis paritas** (kuintil ekonomi terendah/tertinggi vs jenis kelamin perempuan/laki-laki), berbeda **jenjang** (SMA saja vs gabungan Primer & Sekunder), berbeda **skala** (`rasio_x100` vs `rasio`), dan **tidak ada irisan tahun (0 tahun)** karena data valid WDI berakhir pada 2018.
  - **`var2600` (Paritas Gender APK PT, 2020-2025):** Tidak sebanding karena meski sama-sama paritas gender (perempuan/laki-laki), **jenjangnya berbeda** (Perguruan Tinggi vs gabungan Primer & Sekunder), berbeda **skala** (`rasio_x100` vs `rasio`), dan **tidak ada irisan tahun (0 tahun)**.
  - **`var304` (APM, 2003-2025) & `var2211` (APS, 2015-2025):** Meski memiliki irisan tahun dengan WDI, keduanya mengukur persentase partisipasi total per jenjang/kelompok umur tanpa rincian jenis kelamin (bukan rasio paritas gender APK).
- **Implikasi untuk Tahap 6:** Pasangan seri paritas BPS (`var2595`/`var2600`) terhadap `SE.ENR.PRSC.FM.ZS` harus dilaporkan secara eksplisit sebagai **definisi berbeda** disertai catatan keterbatasan **tidak adanya irisan periode**.
