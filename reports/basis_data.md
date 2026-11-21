# Pilihan Basis Data dan Rancangan Skema SQL Silver (Draf Laporan Tim)

**Pilihan: DuckDB** (`data/gold/gudang.duckdb`, dibuat ulang oleh `src/gold/muat_sql.py`; tidak di-commit karena `*.duckdb` masuk `.gitignore`).

## 1. Alasan Pemilihan DuckDB
- **Satu berkas tanpa server:** seluruh anggota tim dan dosen penguji dapat menjalankan skrip pemuat langsung dari klon repositori tanpa memasang layanan server tambahan.
- **Dirancang untuk kueri analitik (OLAP):** sangat cepat untuk agregasi, *pivot*, dan penggabungan panel yang menjadi pekerjaan utama Gold di Sprint 2.
- **Terintegrasi langsung dengan Parquet & Tahap 7:** dapat membaca `data/silver/silver.parquet` secara native dan dipakai kembali untuk tolok ukur perbandingan `pandas` vs `DuckDB` pada arsip WDI di Sprint 3.

Alternatif yang dipertimbangkan:
- **SQLite:** paling sederhana dan tersedia di pustaka standar Python, tetapi kalah cepat untuk kueri analitik/pivot skala besar di Tahap 7.
- **PostgreSQL:** dekat dengan lingkungan produksi, tetapi membutuhkan instalasi dan konfigurasi server lokal di setiap laptop anggota dan penguji.

## 2. Rancangan Skema SQL (`src/gold/silver.sql`)
- **Tabel `seri` (7 baris):** memuat katalog seri dari `docs/seri.csv` dengan `PRIMARY KEY (seri_kode)` dan `CHECK (tingkat IN ('provinsi', 'nasional'))`.
- **Tabel `silver` (5,418 baris):** memuat seluruh baris `data/silver/silver.parquet` dengan `PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)`, `FOREIGN KEY (seri_kode) REFERENCES seri (seri_kode)`, serta `CHECK` untuk `wilayah_kode`, `jenis_periode`, dan panjang `_sha256_raw` (= 64).
- Basis data berperan sebagai lapis validasi terakhir: baris yang melanggar kunci primer, rujukan seri, atau aturan `CHECK` otomatis ditolak saat dimuat.

## 3. Perbandingan Tabel SQL vs Menyimpan Respons JSON Mentah sebagai Dokumen
Respons JSON WebAPI BPS dan WDI berbentuk dokumen bersarang (*nested document*): satu berkas berisi beberapa halaman tahun, daftar kamus label (`vervar`, `turvar`, `tahun`), metadata seri (`var.note` yang memuat tag HTML), serta objek `datacontent` dengan kunci gabungan.
- **Penyimpanan dokumen (JSON mentah di `data/raw/`):** unggul untuk arsip lapis Bronze karena mempertahankan seluruh metadata, struktur asli, dan sidik SHA-256 tanpa perubahan apa pun.
- **Penyimpanan relasional/tabel (Silver di DuckDB):** jauh lebih tepat untuk analisis dan integrasi karena setiap observasi sudah terurai menjadi kolom datar (`wilayah_kode`, `periode`, `rincian`, `nilai`, `satuan`) yang dapat dikueri dengan SQL, digabung antarsumber, serta ditegakkan kunci primer dan integritas referensialnya.
Tim mempertahankan keduanya sesuai fungsi lapisannya: respons JSON mentah tetap sebagai dokumen arsip di `data/raw/` (Bronze), sedangkan data terstruktur dimuat sebagai tabel relasional di DuckDB (Silver/Gold).
