# AI_LOG — Kelompok 8 (IJAZAH HUNTER)

Satu baris per pemakaian AI yang bermakna (Gemini, ChatGPT, Copilot, dan sejenisnya).
Ringkas dan jujur; transkrip penuh tidak diminta. Yang dinilai bukan "pakai AI atau tidak",
melainkan "mengerti atau tidak" — isi kolom terakhir dengan apa yang Anda ubah dari keluarannya.

| Tanggal | Siapa (NIM) | Alat | Untuk apa | Apa yang diubah dari keluarannya |
|---|---|---|---|---|
| 2026-11-18 | 124450101 | Gemini | kerangka pembaca JSON/CSV BPS & WDI (`src/ekstraksi/`) serta audit `MANIFEST.csv` | verifikasi langsung jumlah 14 berkas data (10.865 baris mentah), cek `data_hash`, dan jaga berkas starter tetap utuh |
| 2026-11-18 | 124450075 | Gemini | pemetaan `turvar` ke 9 rincian baku dan pembangunan `data/silver/silver.parquet` | koreksi kode SDG `var304` ke `4.1`, pisahkan satuan `rasio_x100` vs `rasio`, dan buang 43 baris null WDI sesuai metadata |
| 2026-11-20 | 124450072 | Gemini | audit kelengkapan grid 38 provinsi dan klasifikasi anomali/patahan (`K-011`–`K-013`) | cocokkan langsung peta pemekaran provinsi dan `var.note` BPS 2007 agar 30 patahan wilayah & 1 patahan definisi tidak salah ditandai sebagai outlier |
| 2026-11-20 | 124450017 | Gemini | kerangka tabel nasional awal, pasangan rekonsiliasi Sprint 1, dan DDL awal DuckDB (`silver.sql`) | pisahkan pasangan aktif P1 (9 tahun irisan) dari pasangan konteks P2/P3 dan pastikan jumlah baris SQL sama dengan Parquet Silver (5.418) |
| 2026-11-20 | 124450106 | Gemini | kerangka aturan validasi Silver Pandera dan kamus data (`docs/data-dictionary.md`) | sesuaikan rentang nilai per satuan (`persen`, `rasio_x100`, `rasio`, `persen_apk`) dan tambah contoh penelusuran lineage `_berkas_raw` |
| 2026-11-23 | 124450072 | Gemini | draf aturan seleksi satu nilai per sel Gold (`src/gold/aturan_seleksi.py`, `K-014`–`K-017`) | verifikasi pemisahan 241 baris nasional (`9999`), cek 0 duplikat pada 5.177 sel provinsi, dan bawa utuh penanda patahan/outlier Sprint 1 |
| 2026-11-23 | 124450075 | Gemini | kerangka panel provinsi Gold (`src/gold/panel.py`) dan ringkasan `reports/tim.md` (`ringkas_integrasi.py`) | pisahkan kolom paritas `x100` vs `rasio` dari partisipasi; pada revisi review (`deb23fb`), hapus nilai bawaan (*fallback*) dan tambah `_cek_berkas_sumber()` agar gagal eksplisit (`FileNotFoundError`) bila berkas sumber hilang |
| 2026-11-23 | 124450101 | Gemini | draf tabel nasional Gold (`nasional_gold.py`) dan tabel rekonsiliasi (`rekonsiliasi.py`) | perbaiki `AttributeError` pada `itertuples()` kolom sementara berawalan `_` dengan alias sementara sambil mempertahankan `_berkas_raw_utama`/`_berkas_raw_pembanding`, serta verifikasi median selisih 7,38 pp (7,17% relatif) dari metadata BPS & WDI |
| 2026-11-23 | 124450017 | Gemini | perluasan DDL 5 tabel DuckDB (`src/gold/gudang.sql`), loader `muat_sql.py`, dan narasi *Data dan lineage* | selaraskan nama kolom & batasan `CHECK` dengan seluruh Parquet Gold hingga 5/5 tabel berstatus `COCOK` dan pastikan `*.duckdb` tidak di-commit |
| 2026-11-23 | 124450106 | Gemini | draf 6 aturan validasi keras Gold & rekonsiliasi (`src/validasi/aturan_gold.py`) | sambungkan pemanggilan tepat di `src/validasi/__init__.py` (bukan `src/__init__.py`), sinkronkan cabang ke `origin/main`, dan uji 16/16 aturan lolos dari `python pipeline.py` |