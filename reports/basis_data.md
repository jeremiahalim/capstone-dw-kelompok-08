# Pilihan Basis Data & Skema SQL Silver-Gold (Kartu #23)

**Pilihan: DuckDB** (`data/gold/gudang.duckdb`, dibuat ulang oleh `src/gold/muat_sql.py` dari `python pipeline.py`; tidak di-commit karena `*.duckdb` masuk `.gitignore`).

## 1. Alasan Pemilihan DuckDB untuk Lapis Silver & Gold
- **Tanpa server, satu berkas:** seluruh anggota tim dan dosen penguji cukup menjalankan `python pipeline.py` tanpa memasang server PostgreSQL.
- **Mesin analitik kolumnar (OLAP):** jauh lebih cepat daripada SQLite untuk agregasi, join panel 38 provinsi, dan tolok ukur skala 142 rilis WDI di Sprint 3.
- **Menegakkan integritas skema:** DDL `src/gold/gudang.sql` menegakkan kunci primer, foreign key (`REFERENCES seri`), tipe kolom, serta batasan `CHECK`.

## 2. Perbandingan dengan Menyimpan Respons JSON Mentah sebagai Dokumen
- **Dokumen JSON mentah (tepat untuk lapis Bronze / `data/raw/`):** unggul menjaga struktur bersarang WebAPI BPS/WDI dan seluruh metadata asli (`var.note`, `sourceNote`) secara utuh tanpa kehilangan konteks untuk audit.
- **SQL relasional kolumnar DuckDB (tepat untuk lapis Silver & Gold):** unggul untuk kueri analitik lintas seri, penegakan kunci primer agar tidak ada sel ganda, tipe numerik ketat, dan pembacaan langsung berkas Parquet.

## 3. Verifikasi Jumlah Baris Parquet vs SQL

| Tabel SQL | Berkas Parquet | Baris Parquet | Baris SQL | Status |
| --- | --- | ---: | ---: | --- |
| `seri` | `docs/seri.csv` | 7 | 7 | COCOK |
| `silver` | `data/silver/silver.parquet` | 5418 | 5418 | COCOK |
| `gold_panel_provinsi` | `data/gold/panel_provinsi.parquet` | 769 | 769 | COCOK |
| `gold_tabel_nasional` | `data/gold/tabel_nasional.parquet` | 241 | 241 | COCOK |
| `gold_rekonsiliasi` | `data/gold/rekonsiliasi.parquet` | 101 | 101 | COCOK |
