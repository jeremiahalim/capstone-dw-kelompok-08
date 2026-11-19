# Ringkasan Profil dan Calon Anomali 5 Seri BPS

## 1. Statistik Deskriptif per Seri

| Seri                      |   var_id |   Jumlah_Baris |   Jumlah_Wilayah | Rentang_Tahun   | Rincian                                          |   Mean |   Median |   Std |   Min |    Max | Batas_IQR       |
|:--------------------------|---------:|---------------:|-----------------:|:----------------|:-------------------------------------------------|-------:|---------:|------:|------:|-------:|:----------------|
| var304 (APM)              |      304 |           2376 |               39 | 2003-2025       | SD/sederajat, SMP/sederajat, SM/sederajat        |  73.91 |    73.37 | 18.43 | 23.57 |  99.59 | [11.13, 142.38] |
| var1980 (Completion)      |     1980 |            945 |               35 | 2015-2023       | SD / Sederajat, SMP / Sederajat, SMA / Sederajat |  80.29 |    85.53 | 16.07 | 27.44 |  99.45 | [26.89, 134.17] |
| var2211 (APS)             |     2211 |           1572 |               39 | 2015-2025       | 7-12, 13-15, 16-18, 19-23                        |  74.49 |    84.11 | 28.03 | 12.48 |  99.9  | [-5.61, 160.63] |
| var2595 (SDG 4.5.1 v2595) |     2595 |            218 |               39 | 2020-2025       | Tidak ada                                        |  80.79 |    81.15 | 12.55 | 31.98 | 124.16 | [53.6, 108.22]  |
| var2600 (SDG 4.5.1 v2600) |     2600 |            218 |               39 | 2020-2025       | Tidak ada                                        | 118.91 |   116.65 | 19.84 | 62    | 260.23 | [78.72, 156.19] |

## 2. Daftar Calon Anomali Terdeteksi

| Seri                      | Wilayah          | Rincian         |   Periode |   Nilai | Alasan_Ditandai                  |
|:--------------------------|:-----------------|:----------------|----------:|--------:|:---------------------------------|
| var1980 (Completion)      | PAPUA            | SMA / Sederajat |      2015 |   28.23 | |Z-score| > 3                    |
| var1980 (Completion)      | PAPUA            | SMA / Sederajat |      2018 |   29.56 | |Z-score| > 3                    |
| var1980 (Completion)      | PAPUA            | SMA / Sederajat |      2019 |   27.44 | |Z-score| > 3                    |
| var1980 (Completion)      | PAPUA            | SMA / Sederajat |      2020 |   30.92 | |Z-score| > 3                    |
| var2595 (SDG 4.5.1 v2595) | KEP. RIAU        | Tidak ada       |      2020 |  109.35 | Di luar batas IQR                |
| var2595 (SDG 4.5.1 v2595) | DKI JAKARTA      | Tidak ada       |      2020 |  114.78 | Di luar batas IQR                |
| var2595 (SDG 4.5.1 v2595) | DKI JAKARTA      | Tidak ada       |      2025 |  124.16 | Di luar batas IQR; |Z-score| > 3 |
| var2595 (SDG 4.5.1 v2595) | BALI             | Tidak ada       |      2025 |  109.59 | Di luar batas IQR                |
| var2595 (SDG 4.5.1 v2595) | KALIMANTAN UTARA | Tidak ada       |      2021 |   53.59 | Di luar batas IQR                |
| var2595 (SDG 4.5.1 v2595) | SULAWESI BARAT   | Tidak ada       |      2021 |  112.73 | Di luar batas IQR                |
| var2595 (SDG 4.5.1 v2595) | PAPUA BARAT      | Tidak ada       |      2025 |   46.8  | Di luar batas IQR                |
| var2595 (SDG 4.5.1 v2595) | PAPUA BARAT DAYA | Tidak ada       |      2025 |   51.81 | Di luar batas IQR                |
| var2595 (SDG 4.5.1 v2595) | PAPUA SELATAN    | Tidak ada       |      2024 |   53.42 | Di luar batas IQR                |
| var2595 (SDG 4.5.1 v2595) | PAPUA TENGAH     | Tidak ada       |      2025 |   31.98 | Di luar batas IQR; |Z-score| > 3 |
| var2595 (SDG 4.5.1 v2595) | PAPUA PEGUNUNGAN | Tidak ada       |      2024 |   44    | Di luar batas IQR                |
| var2595 (SDG 4.5.1 v2595) | PAPUA PEGUNUNGAN | Tidak ada       |      2025 |   44.51 | Di luar batas IQR                |
| var2600 (SDG 4.5.1 v2600) | LAMPUNG          | Tidak ada       |      2025 |  165.5  | Di luar batas IQR                |
| var2600 (SDG 4.5.1 v2600) | KALIMANTAN UTARA | Tidak ada       |      2023 |  165.96 | Di luar batas IQR                |
| var2600 (SDG 4.5.1 v2600) | KALIMANTAN UTARA | Tidak ada       |      2024 |  161.15 | Di luar batas IQR                |
| var2600 (SDG 4.5.1 v2600) | KALIMANTAN UTARA | Tidak ada       |      2025 |  260.23 | Di luar batas IQR; |Z-score| > 3 |
| var2600 (SDG 4.5.1 v2600) | SULAWESI UTARA   | Tidak ada       |      2024 |  183.03 | Di luar batas IQR; |Z-score| > 3 |
| var2600 (SDG 4.5.1 v2600) | GORONTALO        | Tidak ada       |      2021 |  175.5  | Di luar batas IQR                |
| var2600 (SDG 4.5.1 v2600) | SULAWESI BARAT   | Tidak ada       |      2024 |  170.21 | Di luar batas IQR                |
| var2600 (SDG 4.5.1 v2600) | PAPUA SELATAN    | Tidak ada       |      2024 |   77.69 | Di luar batas IQR                |
| var2600 (SDG 4.5.1 v2600) | PAPUA SELATAN    | Tidak ada       |      2025 |   72.46 | Di luar batas IQR                |
| var2600 (SDG 4.5.1 v2600) | PAPUA PEGUNUNGAN | Tidak ada       |      2025 |   62    | Di luar batas IQR                |