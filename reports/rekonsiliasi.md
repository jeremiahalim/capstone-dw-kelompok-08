# Hasil Rekonsiliasi Seri Utama vs Pembanding Nasional (Kartu #24)

Dihasilkan otomatis oleh `src/gold/rekonsiliasi.py` ke `data/gold/rekonsiliasi.parquet` (**101 baris**, termasuk seluruh periode tanpa pasangan; selisih tidak dihapus).

## 1. Pasangan Aktif P1: `var1980 [jenjang=sd]` vs `SE.PRM.CMPT.ZS` (2015-2023)

- Jumlah tahun beririsan: **9 tahun** (2015-2023); periode WDI tanpa pasangan: 38 tahun (1972-2014).
- Median selisih absolut: **7.38 poin persen** (signed median: `-7.38` poin persen; WDI selalu lebih tinggi).
- **Kategori penjelasan:** `definisi` (*definisi berbeda* — Susenas kohort umur 13-15 tahun dalam `persen` 0-100% vs *gross intake ratio* administratif UIS dalam `persen_apk` yang dapat >100%).

| periode | nilai_utama | nilai_pembanding | selisih | selisih_absolut | kategori_selisih |
| --- | --- | --- | --- | --- | --- |
| 2015 | 91.44 | 108.9 | -17.4567 | 17.4567 | definisi |
| 2016 | 93.88 | 107.21 | -13.3334 | 13.3334 | definisi |
| 2017 | 95.25 | 104.77 | -9.5235 | 9.5235 | definisi |
| 2018 | 94.68 | 102.63 | -7.9475 | 7.9475 | definisi |
| 2019 | 95.48 | 102.86 | -7.3762 | 7.3762 | definisi |
| 2020 | 96.0 | 102.12 | -6.1197 | 6.1197 | definisi |
| 2021 | 97.37 | 103.37 | -5.9968 | 5.9968 | definisi |
| 2022 | 97.82 | 102.07 | -4.2481 | 4.2481 | definisi |
| 2023 | 97.83 | 99.95 | -2.1222 | 2.1222 | definisi |

## 2. Pasangan Konteks P2 & P3 (Dilaporkan sebagai Definisi Berbeda)

- **P2 (`var2600` vs `SE.ENR.PRSC.FM.ZS`, 48 baris):** 0 tahun beririsan (BPS PT 2020-2025 vs WDI SD+menengah 1970-2018), jenjang dan skala berbeda -> kategori `definisi`.
- **P3 (`var2595`, 6 baris):** paritas kuintil SMA tanpa seri pembanding kuintil di paket WDI -> kategori `definisi`.
