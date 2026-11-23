# Ringkasan Panel Gold Provinsi x Periode x Indikator (Kartu #21)

Dihasilkan otomatis oleh `src/gold/panel.py` dari `data/silver/silver.parquet`.

- **Panel lebar (`data/gold/panel_provinsi.parquet`):** **769 baris** (38 provinsi, periode 2003-2025, 0 duplikat kunci `wilayah_kode, periode`).
- **Lineage sel Gold (`data/gold/panel_lineage.parquet`):** **5,177 sel** (5 seri utama: `var1980, var2211, var2595, var2600, var304`, 0 duplikat kunci `wilayah_kode, periode, indikator_gold`).
- **Pemisahan satuan & versi asli:** tingkat penyelesaian melebar per jenjang (`penyelesaian_sd/smp/sma`, `persen`), partisipasi dalam kolom terpisah (`apm_*`, `aps_*`, `persen`), dan rasio paritas terpisah dengan versi asli `rasio_x100` (`paritas_*_x100`) berdampingan dengan versi normalisasi `rasio` (`paritas_*_rasio` = nilai / 100).
- **Penanda Sprint 1 terbawa:** `ada_patahan_definisi`=33 baris, `ada_patahan_wilayah`=6 baris, `ada_outlier`=16 baris.
