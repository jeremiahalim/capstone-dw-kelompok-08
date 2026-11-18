# Laporan Penetapan Satuan, Periode, dan Kode SDG dari Metadata

Hasil verifikasi 7 seri utama dan pembanding terhadap berkas mentah di `data/raw/`:

| Sumber | Kode Seri | Nama Seri | Satuan | Periode | Kode SDG | Sumber Metadata | Catatan Audit |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| bps | `var2595` | 4.5.1* Rasio Angka Partisipasi Kasar (APK) pada jenjang SMA/sederajat untuk kuintil terendah/kuintil tertinggi menurut provinsi | `rasio_x100` | tahunan | `4.5.1` | BPS JSON (sdg4_4_5_1_v2595.json) | Satuan awal kosong; nilai berkisar 32-260 (rasio dikali 100). |
| bps | `var2600` | 4.5.1* Rasio Angka Partisipasi Kasar (APK) pada jenjang PT/sederajat untuk perempuan/laki-laki menurut provinsi | `rasio_x100` | tahunan | `4.5.1` | BPS JSON (sdg4_4_5_1_v2600.json) | Satuan awal kosong; nilai merupakan indeks paritas dikali 100. |
| bps | `var304` | Angka Partisipasi Murni (APM) Menurut Provinsi dan Jenjang Pendidikan | `persen` | tahunan | `4.1` | BPS JSON (sdg4_apm.json) | Dikoreksi dari kode katalog 4.5.1 ke 4.1 karena merupakan APM, bukan indeks paritas. |
| bps | `var1980` | Tingkat Penyelesaian Pendidikan Menurut Jenjang Pendidikan dan Provinsi | `persen` | tahunan | `4.1.2` | BPS JSON (sdg4_completion.json) | Satuan ditetapkan persen (kohort umur 3-5 tahun di atas umur lulus). |
| bps | `var2211` | Angka Partisipasi Sekolah (APS) Menurut Provinsi dan Kelompok Umur | `persen` | tahunan | `4.1` | BPS JSON (sdg4_aps.json) | var.note salah tempel definisi disabilitas diabaikan; definisi diambil dari judul. |
| wdi | `SE.ENR.PRSC.FM.ZS` | School enrollment, primary and secondary (gross), gender parity index (GPI) | `rasio` | tahunan | `4.5.1` | WDI Metadata (sumber2_indikator.json / sumber46_indikator.json) | Pembanding GPI WDI dengan skala rasio asli (0.77 - 1.02). |
| wdi | `SE.PRM.CMPT.ZS` | Primary completion rate, total (% of relevant age group) | `persen_apk` | tahunan | `4.1.2` | WDI Metadata (sumber2_indikator.json / sumber46_indikator.json) | Rasio masuk kasar tanpa batas umur sehingga nilai dapat melebihi 100. |
