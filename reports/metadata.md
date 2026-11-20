# Laporan Audit Metadata Seri: Nama, Satuan, Periode, dan Kode SDG

Dihasilkan oleh `src/silver/metadata.py` langsung dari berkas mentah di `data/raw/`. Tabel referensi lengkap tersimpan di `docs/seri.csv` dan setiap koreksi katalog tercatat di `log-keputusan.csv` (`K-004` s.d. `K-008`). Seluruh 7 seri berjenis periode tahunan (`tahun` di Silver); tidak ada perata-rataan periode semesteran/bulanan.

## 1. Judul di Berkas Mentah, Sumber Metadata, dan Nama Baku

| seri_kode | nama_seri | asal_metadata | nama_baku |
| --- | --- | --- | --- |
| var304 | Angka Partisipasi Murni (APM) Menurut Provinsi dan Jenjang Pendidikan | bps/2026-10-17/json/sdg4_apm.json (var.label, var.note) | Angka Partisipasi Murni (APM) menurut jenjang SD, SMP, SM |
| var2595 | 4.5.1* Rasio Angka Partisipasi Kasar (APK) pada jenjang SMA/sederajat untuk kuintil terendah/kuintil tertinggi menurut provinsi | bps/2026-10-17/json/sdg4_4_5_1_v2595.json (var.label) | Rasio APK SMA/sederajat kuintil terendah terhadap kuintil tertinggi |
| var2600 | 4.5.1* Rasio Angka Partisipasi Kasar (APK) pada jenjang PT/sederajat untuk perempuan/laki-laki menurut provinsi | bps/2026-10-17/json/sdg4_4_5_1_v2600.json (var.label) | Rasio APK perguruan tinggi perempuan terhadap laki-laki |
| var1980 | Tingkat Penyelesaian Pendidikan Menurut Jenjang Pendidikan dan Provinsi | bps/2026-10-17/json/sdg4_completion.json (var.label, var.note) | Tingkat penyelesaian pendidikan menurut jenjang (SD, SMP, SMA) |
| var2211 | Angka Partisipasi Sekolah (APS) Menurut Provinsi dan Kelompok Umur | bps/2026-10-17/json/sdg4_aps.json (var.label) | Angka Partisipasi Sekolah (APS) menurut kelompok umur |
| SE.ENR.PRSC.FM.ZS | School enrollment, primary and secondary (gross), gender parity index (GPI) | wdi/2026-10-20/metadata/sumber2_indikator.json & sumber46_indikator.json | School enrollment, primary and secondary (gross), gender parity index (GPI) |
| SE.PRM.CMPT.ZS | Primary completion rate, total (% of relevant age group) | wdi/2026-10-20/metadata/sumber2_indikator.json & sumber46_indikator.json | Primary completion rate, total (% of relevant age group) |

## 2. Perbandingan Katalog Awal vs Satuan & Kode SDG Final (beserta Bukti)

| seri_kode | katalog_satuan | satuan | rentang_aktual | bukti_satuan | katalog_sdg | kode_sdg | bukti_sdg |
| --- | --- | --- | --- | --- | --- | --- | --- |
| var304 | tidak_ada | persen | 23.57 - 99.59 | judul 'Angka Partisipasi Murni'; var.unit kosong; nilai <= 100% | 4.5.1 | 4.1 | APM per jenjang bukan indeks paritas (4.5.1), melainkan partisipasi jenjang dasar-menengah (target 4.1) |
| var2595 | tidak_ada | rasio_x100 | 31.98 - 124.16 | judul 'Rasio APK ... kuintil terendah/tertinggi'; var.unit kosong; nilai 32-124 (rasio dikali 100) | 4.5.1 | 4.5.1 | var.label diawali '4.5.1*'; indeks paritas kuintil pengeluaran jenjang SMA |
| var2600 | tidak_ada | rasio_x100 | 62.00 - 260.23 | judul 'Rasio APK ... perempuan/laki-laki'; var.unit kosong; nilai 62-260 (rasio dikali 100) | 4.5.1 | 4.5.1 | var.label diawali '4.5.1*'; indeks paritas jenis kelamin jenjang perguruan tinggi |
| var1980 | tidak_ada | persen | 27.44 - 99.45 | var.note: persentase anak dan remaja yang menyelesaikan jenjang pendidikan (0-100%) | 4.1.2 | 4.1.2 | definisi var.note sesuai SDG 4.1.2 completion rate berbasis Susenas |
| var2211 | tidak_ada | persen | 12.48 - 99.90 | judul 'Angka Partisipasi Sekolah'; var.unit kosong; nilai <= 100% | — | — | tidak terpetakan ke kode SDG; dipertahankan sebagai konteks partisipasi umur (K-008) |
| SE.ENR.PRSC.FM.ZS | — | rasio | 0.77 - 1.02 | name menyebut 'gender parity index (GPI)'; skala rasio asli (0.77-1.02) | — | 4.5.1 | tercantum pada metadata/sumber46_indikator.json (SDG 4.5.1) |
| SE.PRM.CMPT.ZS | — | persen_apk | 48.46 - 109.55 | sourceNote: gross intake ratio to last grade of primary tanpa batas umur sehingga dapat > 100% | — | 4.1.2 | tercantum pada metadata/sumber46_indikator.json (SDG 4.1.2) |

## 3. Ringkasan Koreksi Katalog, Periode, dan Rujukan Log Keputusan

| seri_kode | periode_aktual | jenis_periode | koreksi_katalog | ref_log |
| --- | --- | --- | --- | --- |
| var304 | 2003-2025 | tahunan | satuan tidak_ada -> persen; kode SDG 4.5.1 -> 4.1 | K-004, K-005 |
| var2595 | 2020-2025 | tahunan | satuan tidak_ada -> rasio_x100 | K-004, K-005 |
| var2600 | 2020-2025 | tahunan | satuan tidak_ada -> rasio_x100 | K-004, K-005 |
| var1980 | 2015-2023 | tahunan | satuan tidak_ada -> persen | K-005 |
| var2211 | 2015-2025 | tahunan | satuan tidak_ada -> persen; var.note salah tempel (disabilitas) diabaikan | K-005, K-007, K-008 |
| SE.ENR.PRSC.FM.ZS | 1970-2018 | tahunan | kode SDG kosong -> 4.5.1; satuan ditetapkan rasio | K-005, K-006 |
| SE.PRM.CMPT.ZS | 1972-2023 | tahunan | kode SDG kosong -> 4.1.2; satuan ditetapkan persen_apk | K-005, K-006 |

## 4. Kutipan Catatan Metadata Sumber — BPS (`var.note`, tanpa tag HTML)

| seri_kode | berkas | var_note_bersih |
| --- | --- | --- |
| var1980 | bps/2026-10-17/json/sdg4_completion.json | Definisi Indikator: Indikator ini mengukur persentase anak dan remaja yang berhasil menyelesaikan jenjang pendidikan yang sesuai dengan rentang usianya. Rentang usia yang termasuk dalam perhitungan ini adalah antara 1 sampai dengan 3 tahun sejak usia kelulusan jenjang pendidikan pada umumnya. Berdasarkan usia wajib belajar yang dimulai sejak 7 tahun, maka dengan asumsi siswa belajar penuh waktu dan tidak tinggal kelas, mereka lulus SD/sederajat pada usia sekitar 12 tahun. Oleh karena itu rentang usia yang digunakan untuk penghitungan tingkat ketuntasan SD/sederajat adalah anak atau remaja usia 13 tahun (12 + 1 tahun) sampai dengan 15 tahun (12 + 3 tahun). Tingkat penyelesaian yang mencapai atau mendekati 100% menunjukkan bahwa hampir seluruh anak-anak dan remaja telah menyelesaikan jenjang pendidikan yang seharusnya atau sesuai usia mereka, tanpa keterlambatan yang signifikan atau berarti. Sumber Data: Susenas KOR |
| var2211 | bps/2026-10-17/json/sdg4_aps.json | Sumber : BPS, Susenas Definisi : Angka yang menggambarkan ketimpangan partisipasi sekolah antara penduduk berusia 7-17 tahun dengan disabilitas dan tanpa disabilitas |
| var2595 | bps/2026-10-17/json/sdg4_4_5_1_v2595.json | (kosong) |
| var2600 | bps/2026-10-17/json/sdg4_4_5_1_v2600.json | (kosong) |
| var304 | bps/2026-10-17/json/sdg4_apm.json | Sumber: BPS, Susenas Catatan: Mulai tahun 2007, APM mencakup pendidikan non-formal (paket A setara SD sederajat, paket B setara SMP sederajat dan paket C setara SMA/SMK sederajat) |

## 5. Kutipan Catatan Metadata Sumber — WDI (`sourceNote`) & Cek Berkas Ganda

| seri_kode | berkas | sourceNote |
| --- | --- | --- |
| SE.ENR.PRSC.FM.ZS | sumber2_indikator.json | Gender parity index for gross enrollment ratio in primary and secondary education is the ratio of girls to boys enrolled at primary and secondary levels in public and private schools. |
| SE.PRM.CMPT.ZS | sumber2_indikator.json | Primary completion rate, or gross intake ratio to the last grade of primary education, is the number of new entrants (enrollments minus repeaters) in the last grade of primary education, regardless of age, divided by the population at the entrance age for the last grade of primary education. Data limitations preclude adjusting for students who drop out during the final year of primary education. |

### Pemeriksaan Metadata WDI yang Muncul di Lebih dari Satu Berkas

| seri_kode | jumlah_berkas | daftar_berkas | isi_sama |
| --- | --- | --- | --- |
| SE.ENR.PRSC.FM.ZS | 2 | sumber2_indikator.json, sumber46_indikator.json | ya |
| SE.PRM.CMPT.ZS | 2 | sumber2_indikator.json, sumber46_indikator.json | ya |
