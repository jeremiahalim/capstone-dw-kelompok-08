# Kelengkapan Panel 38 Provinsi x Periode dan Kategori Sel Kosong

Dihasilkan oleh `src/silver/proses_grid.py` dari `data/silver/silver.parquet`.

Grid menggunakan susunan **38 provinsi tahun 2025** x **periode terbit** per seri; baris nasional **Indonesia (`9999`)** dipisahkan dari baris provinsi.

- `belum_ada`: provinsi belum dibentuk pada tahun tersebut (bukan missing).
- `batas_lama`: provinsi baru sudah dibentuk, tetapi BPS masih menerbitkan provinsi induk dengan batas lama (angka tidak dipecah).
- `missing`: provinsi sudah ada dan seharusnya terbit, tetapi nilainya kosong (strategi: dibiarkan kosong / tidak diimputasi, dicatat di `log-keputusan.csv`).

## 1. Rekap Jumlah Sel per Kategori (Tingkat Provinsi)

| seri_kode | batas_lama | belum_ada | missing | terisi |
| --- | --- | --- | --- | --- |
| var1980 [jenjang=sd] | 4 | 32 | 0 | 306 |
| var1980 [jenjang=sma] | 4 | 32 | 0 | 306 |
| var1980 [jenjang=smp] | 4 | 32 | 0 | 306 |
| var2211 [umur=13-15] | 4 | 32 | 0 | 382 |
| var2211 [umur=16-18] | 4 | 32 | 0 | 382 |
| var2211 [umur=19-23] | 4 | 32 | 0 | 382 |
| var2211 [umur=7-12] | 4 | 32 | 0 | 382 |
| var2595 | 4 | 12 | 0 | 212 |
| var2600 | 4 | 12 | 0 | 212 |
| var304 [jenjang=sd] | 11 | 93 | 1 | 769 |
| var304 [jenjang=sm] | 11 | 93 | 1 | 769 |
| var304 [jenjang=smp] | 11 | 93 | 1 | 769 |

## 2. Persen Sel Terisi per Seri per Periode (Tingkat Provinsi)

| seri_kode | periode | sel | terisi | seharusnya_ada | persen_dari_38 | persen_dari_seharusnya |
| --- | --- | --- | --- | --- | --- | --- |
| var1980 [jenjang=sd] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sd] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sd] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sd] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sd] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sd] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sd] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sd] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sd] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sma] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sma] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sma] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sma] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sma] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sma] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sma] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sma] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=sma] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=smp] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=smp] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=smp] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=smp] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=smp] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=smp] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=smp] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=smp] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var1980 [jenjang=smp] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=13-15] | 2024 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2211 [umur=13-15] | 2025 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2211 [umur=16-18] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=16-18] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=16-18] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=16-18] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=16-18] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=16-18] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=16-18] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=16-18] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=16-18] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=16-18] | 2024 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2211 [umur=16-18] | 2025 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2211 [umur=19-23] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=19-23] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=19-23] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=19-23] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=19-23] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=19-23] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=19-23] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=19-23] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=19-23] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=19-23] | 2024 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2211 [umur=19-23] | 2025 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2211 [umur=7-12] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=7-12] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=7-12] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=7-12] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=7-12] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=7-12] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=7-12] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=7-12] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=7-12] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2211 [umur=7-12] | 2024 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2211 [umur=7-12] | 2025 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2595 | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2595 | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2595 | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2595 | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2595 | 2024 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2595 | 2025 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2600 | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2600 | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2600 | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2600 | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var2600 | 2024 | 38 | 38 | 38 | 100.0 | 100.0 |
| var2600 | 2025 | 38 | 38 | 38 | 100.0 | 100.0 |
| var304 [jenjang=sd] | 2003 | 38 | 30 | 30 | 78.9 | 100.0 |
| var304 [jenjang=sd] | 2004 | 38 | 30 | 30 | 78.9 | 100.0 |
| var304 [jenjang=sd] | 2005 | 38 | 30 | 31 | 78.9 | 96.8 |
| var304 [jenjang=sd] | 2006 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sd] | 2007 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sd] | 2008 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sd] | 2009 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sd] | 2010 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sd] | 2011 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sd] | 2012 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sd] | 2013 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sd] | 2014 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sd] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sd] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sd] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sd] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sd] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sd] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sd] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sd] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sd] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sd] | 2024 | 38 | 38 | 38 | 100.0 | 100.0 |
| var304 [jenjang=sd] | 2025 | 38 | 38 | 38 | 100.0 | 100.0 |
| var304 [jenjang=sm] | 2003 | 38 | 30 | 30 | 78.9 | 100.0 |
| var304 [jenjang=sm] | 2004 | 38 | 30 | 30 | 78.9 | 100.0 |
| var304 [jenjang=sm] | 2005 | 38 | 30 | 31 | 78.9 | 96.8 |
| var304 [jenjang=sm] | 2006 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sm] | 2007 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sm] | 2008 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sm] | 2009 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sm] | 2010 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sm] | 2011 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sm] | 2012 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sm] | 2013 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sm] | 2014 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=sm] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sm] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sm] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sm] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sm] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sm] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sm] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sm] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sm] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=sm] | 2024 | 38 | 38 | 38 | 100.0 | 100.0 |
| var304 [jenjang=sm] | 2025 | 38 | 38 | 38 | 100.0 | 100.0 |
| var304 [jenjang=smp] | 2003 | 38 | 30 | 30 | 78.9 | 100.0 |
| var304 [jenjang=smp] | 2004 | 38 | 30 | 30 | 78.9 | 100.0 |
| var304 [jenjang=smp] | 2005 | 38 | 30 | 31 | 78.9 | 96.8 |
| var304 [jenjang=smp] | 2006 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=smp] | 2007 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=smp] | 2008 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=smp] | 2009 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=smp] | 2010 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=smp] | 2011 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=smp] | 2012 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=smp] | 2013 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=smp] | 2014 | 38 | 33 | 33 | 86.8 | 100.0 |
| var304 [jenjang=smp] | 2015 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=smp] | 2016 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=smp] | 2017 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=smp] | 2018 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=smp] | 2019 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=smp] | 2020 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=smp] | 2021 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=smp] | 2022 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=smp] | 2023 | 38 | 34 | 34 | 89.5 | 100.0 |
| var304 [jenjang=smp] | 2024 | 38 | 38 | 38 | 100.0 | 100.0 |
| var304 [jenjang=smp] | 2025 | 38 | 38 | 38 | 100.0 | 100.0 |

## 3. Kelengkapan Baris Indonesia (wilayah_kode = 9999)

| seri_kode | periode | kategori | bukti |
| --- | --- | --- | --- |
| var1980 [jenjang=sd] | 2015 | terisi | nilai tersedia pada data silver |
| var1980 [jenjang=sd] | 2016 | terisi | nilai tersedia pada data silver |
| var1980 [jenjang=sd] | 2017 | terisi | nilai tersedia pada data silver |
| var1980 [jenjang=sd] | 2018 | terisi | nilai tersedia pada data silver |
| var1980 [jenjang=sd] | 2019 | terisi | nilai tersedia pada data silver |
| var1980 [jenjang=sd] | 2020 | terisi | nilai tersedia pada data silver |
| var1980 [jenjang=sd] | 2021 | terisi | nilai tersedia pada data silver |
| var1980 [jenjang=sd] | 2022 | terisi | nilai tersedia pada data silver |
| var1980 [jenjang=sd] | 2023 | terisi | nilai tersedia pada data silver |
| var1980 [jenjang=sma] | 2015 | terisi | nilai tersedia pada data silver |

## 4. Batas Pemakaian Panel

| seri_kode | tingkat | periode_pertama | periode_terakhir | jumlah_periode |
| --- | --- | --- | --- | --- |
| var1980 [jenjang=sd] | nasional | 2015 | 2023 | 9 |
| var1980 [jenjang=sd] | provinsi | 2015 | 2023 | 9 |
| var1980 [jenjang=sma] | nasional | 2015 | 2023 | 9 |
| var1980 [jenjang=sma] | provinsi | 2015 | 2023 | 9 |
| var1980 [jenjang=smp] | nasional | 2015 | 2023 | 9 |
| var1980 [jenjang=smp] | provinsi | 2015 | 2023 | 9 |
| var2211 [umur=13-15] | nasional | 2015 | 2025 | 11 |
| var2211 [umur=13-15] | provinsi | 2015 | 2025 | 11 |
| var2211 [umur=16-18] | nasional | 2015 | 2025 | 11 |
| var2211 [umur=16-18] | provinsi | 2015 | 2025 | 11 |
| var2211 [umur=19-23] | nasional | 2015 | 2025 | 11 |
| var2211 [umur=19-23] | provinsi | 2015 | 2025 | 11 |
| var2211 [umur=7-12] | nasional | 2015 | 2025 | 11 |
| var2211 [umur=7-12] | provinsi | 2015 | 2025 | 11 |
| var2595 | nasional | 2020 | 2025 | 6 |
| var2595 | provinsi | 2020 | 2025 | 6 |
| var2600 | nasional | 2020 | 2025 | 6 |
| var2600 | provinsi | 2020 | 2025 | 6 |
| var304 [jenjang=sd] | nasional | 2003 | 2025 | 23 |
| var304 [jenjang=sd] | provinsi | 2003 | 2025 | 23 |
| var304 [jenjang=sm] | nasional | 2003 | 2025 | 23 |
| var304 [jenjang=sm] | provinsi | 2003 | 2025 | 23 |
| var304 [jenjang=smp] | nasional | 2003 | 2025 | 23 |
| var304 [jenjang=smp] | provinsi | 2003 | 2025 | 23 |

Daftar lengkap seluruh sel kosong beserta buktinya tersimpan di `reports/grid_sel_kosong.csv` (599 baris).