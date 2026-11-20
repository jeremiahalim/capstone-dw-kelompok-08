# Data Dictionary — Kelompok 8 (Kesetaraan dan Penyelesaian Pendidikan)

Dihasilkan otomatis oleh `src/validasi/kamus_data.py` dari data nyata `data/silver/silver.parquet`. Tipe, jumlah kosong, dan rentang nilai dihitung langsung dari berkas Silver.

## 1. `data/silver/silver.parquet` (5,418 baris, 11 kolom)

Satu baris = satu `seri_kode x wilayah_kode x periode x rincian x _berkas_raw`. Kunci unik: `sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw`.

| kolom | tipe | kosong | rentang_atau_nilai | asal | arti |
| --- | --- | --- | --- | --- | --- |
| sumber | str | 0 | bps, wdi | nama folder sumber di data/raw/ | lembaga penerbit: bps atau wdi |
| seri_kode | str | 0 | SE.ENR.PRSC.FM.ZS, SE.PRM.CMPT.ZS, var1980, var2211, var2595, var2600, ... (7 nilai) | kode seri di sumbernya (BPS: 'var' + var.val; WDI: indicator.id) | identitas seri; detail lengkap di docs/seri.csv |
| wilayah_kode | int64 | 0 | 1100 - 9999 | kode BPS dua digit x 100 (log K-001) | susunan 38 provinsi 2025 (1100-9700) dan 9999 = Indonesia |
| nama_wilayah | str | 0 | ACEH, BALI, BANTEN, BENGKULU, DI YOGYAKARTA, DKI JAKARTA, ... (40 nilai) | nama wilayah BPS / 'Indonesia' untuk WDI | nama provinsi atau Indonesia |
| periode | str | 0 | 1970, 1971, 1972, 1973, 1974, 1975, ... (53 nilai) | tahun BPS, date WDI | bentuk baku periode (4 digit tahun: 1970-2025) |
| jenis_periode | str | 0 | tahun | diturunkan dari format periode (docs/seri.csv) | tahun, semester, triwulan, atau bulan |
| rincian | str | 0 | jenjang=sd, jenjang=sm, jenjang=sma, jenjang=smp, total, umur=13-15, ... (9 nilai) | turvar BPS; 'total' untuk seri tanpa rincian (log K-009) | 'total' atau 'dimensi=kode' (jenjang=..., umur=...) |
| nilai | float64 | 0 | 0.772750020027161 - 260.23 | datacontent BPS; value WDI (null dibuang, log K-010) | angka numerik sesuai satuan; baris tanpa nilai tidak masuk Silver |
| satuan | str | 0 | persen, persen_apk, rasio, rasio_x100 | audit metadata sumber (docs/seri.csv; log K-005) | satuan baku: persen, persen_apk, rasio, atau rasio_x100 |
| _berkas_raw | str | 0 | bps/2026-10-17/json/sdg4_4_5_1_v2595.json, bps/2026-10-17/json/sdg4_4_5_1_v2600.json, bps/2026-10-17/json/sdg4_apm.json, bps/2026-10-17/json/sdg4_aps.json, bps/2026-10-17/json/sdg4_completion.json, wdi/2026-10-20/data/kelompok-03-hal-01.json | jalur berkas mentah relatif terhadap data/raw/ | lineage: berkas asal baris ini |
| _sha256_raw | str | 0 | 06c48066f084752f88c482b94decbbacaf6991ea8507b699f351d9653756c5af, 684f1d2cc37f2ae7cbb57da4690ffa4173f3ed38e8f81dd53d7c332af301da3f, 7b649c5de4bbceb93fa223984c3cdf47bd48a58155c17f7f7125115cdc6500c3, ac1d12474a59846c4e487beef7d1011f916b2dd26a02a0ccf4b11b6e8ed7883d, ce205cbf83a8c34c941c1c96d35911a201d70f095f03c956308e0e3de4948dc8, e0b1421956b6673054b20aa8b5ecab4dce37ae2b73a7b1b9b0eb6d040652132f | src.common.manifest.sha256_raw | lineage: sidik SHA-256 berkas asal, dicocokkan dengan MANIFEST.csv |

## 2. Kamus Rincian

Aturan penulisan rincian (`log-keputusan.csv` `K-009`): dimensi yang bervariasi ditulis `nama=kode`, dan baris tanpa dimensi bervariasi ditulis `total`. Pemetaan dari `turvar` BPS:
- `jenjang`: `sd` (SD/Sederajat), `smp` (SMP/Sederajat), `sm` (SM/Sederajat), `sma` (SMA/Sederajat).
- `umur`: `7-12`, `13-15`, `16-18`, `19-23`.

| rincian | dipakai_seri |
| --- | --- |
| jenjang=sd | var1980, var304 |
| jenjang=sm | var304 |
| jenjang=sma | var1980 |
| jenjang=smp | var1980, var304 |
| total | SE.ENR.PRSC.FM.ZS, SE.PRM.CMPT.ZS, var2595, var2600 |
| umur=13-15 | var2211 |
| umur=16-18 | var2211 |
| umur=19-23 | var2211 |
| umur=7-12 | var2211 |

## 3. Satuan dan Kode SDG per Seri

| sumber | seri_kode | satuan | kode_sdg | nama_baku |
| --- | --- | --- | --- | --- |
| bps | var304 | persen | 4.1 | Angka Partisipasi Murni (APM) menurut jenjang SD, SMP, SM |
| bps | var2595 | rasio_x100 | 4.5.1 | Rasio APK SMA/sederajat kuintil terendah terhadap kuintil tertinggi |
| bps | var2600 | rasio_x100 | 4.5.1 | Rasio APK perguruan tinggi perempuan terhadap laki-laki |
| bps | var1980 | persen | 4.1.2 | Tingkat penyelesaian pendidikan menurut jenjang (SD, SMP, SMA) |
| bps | var2211 | persen | — | Angka Partisipasi Sekolah (APS) menurut kelompok umur |
| wdi | SE.ENR.PRSC.FM.ZS | rasio | 4.5.1 | School enrollment, primary and secondary (gross), gender parity index (GPI) |
| wdi | SE.PRM.CMPT.ZS | persen_apk | 4.1.2 | Primary completion rate, total (% of relevant age group) |

## 4. Aturan Kode Wilayah (`log-keputusan.csv` `K-001`)

`9999` = Indonesia (nasional); provinsi = kode dua digit BPS dikali 100 (`1100` Aceh s.d. `9700` Papua Pegunungan) pada susunan 38 provinsi tahun 2025. Provinsi pemekaran dibiarkan apa adanya (hanya berisi tahun sejak berdiri).

## 5. Contoh Penelusuran Lineage Satu Baris Silver ke Berkas Mentah

| sumber | seri_kode | wilayah_kode | periode | rincian | nilai | _berkas_raw | _sha256_raw |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bps | var1980 | 1100 | 2015 | jenjang=sd | 96.47 | bps/2026-10-17/json/sdg4_completion.json | e0b1421956b6673054b20aa8b5ecab4dce37ae2b73a7b1b9b0eb6d040652132f |

1. Kolom _berkas_raw menunjuk langsung ke berkas mentah `data/raw/bps/2026-10-17/json/sdg4_completion.json`.
2. Pada `data/raw/MANIFEST.csv`, berkas tersebut memiliki sidik SHA-256 `e0b1421956b6...` yang identik dengan kolom _sha256_raw, membuktikan data dibaca dari berkas mentah asli tanpa suntingan.
3. Di dalam berkas JSON BPS tersebut, nilai ditemukan pada `datacontent` untuk gabungan kode wilayah (`vervar`), kode variabel (`var`), kode rincian (`turvar`), dan kode tahun (`tahun`) yang sama.

## 6. `data/gold/<tabel>.parquet`

_Kolom panel Gold dan tabel rekonsiliasi akan ditambahkan pada Sprint 2–3._
