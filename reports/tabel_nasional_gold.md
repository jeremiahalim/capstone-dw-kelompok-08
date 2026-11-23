# Ringkasan Tabel Nasional Gold (Kartu #22)

Dihasilkan otomatis oleh `src/gold/nasional_gold.py` (dipanggil dari `src/gold/nasional.py` -> `python pipeline.py`).

- **Tabel nasional utama (`data/gold/tabel_nasional.parquet`):** **241 baris** (1 baris per `periode x seri_kode x rincian`, 0 duplikat), mencakup **7 seri** pada **53 periode** (1970-2025).
- **Tabel nasional lebar (`data/gold/tabel_nasional_lebar.parquet`):** **53 periode x 14 kolom seri/rincian** berdampingan.
- **Distribusi kolom `asal_angka`:**
  - `baris_indonesia`: **152 baris** (seluruh 5 seri utama BPS `var304`, `var2595`, `var2600`, `var1980`, `var2211` menerbitkan baris resmi Indonesia `wilayah_kode = 9999`).
  - `pembanding`: **89 baris** (2 seri nasional WDI `SE.ENR.PRSC.FM.ZS` dan `SE.PRM.CMPT.ZS`).
  - `agregat`: **0 baris** (tidak diperlukan agregasi buatan dari provinsi karena seluruh seri utama BPS sudah memiliki angka nasional resmi).
- **Lineage:** 100% baris membawa `_berkas_raw` dan `_sha256_raw` (0 nilai kosong).
