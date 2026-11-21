# Tabel Nasional dan Daftar Pasangan Rekonsiliasi (Persiapan Tahap 6)

Dihasilkan oleh `src/gold/nasional.py` dari baris nasional Indonesia (`wilayah_kode = 9999`) pada `data/silver/silver.parquet`. Selisih dihitung penuh pada Sprint 2; Sprint 1 memastikan keterbandingan tiap pasangan dan mencatat tahun yang beririsan.

Tabel nasional lebar (`periode x seri`): `reports/tabel_nasional.csv` (53 periode, 14 kolom seri/rincian).

## 1. Ringkasan Pasangan Rekonsiliasi

| id | seri_utama | pembanding | jenis | periode_beririsan | tahun | dugaan_kategori |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | var1980 [jenjang=sd] | SE.PRM.CMPT.ZS [total] | selisih | 9 | 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023 | definisi berbeda: umur 3-5 tahun di atas umur lulus (BPS) vs siswa baru kelas terakhir tanpa memandang umur (WDI) |
| P2 | var2600 [total] | SE.ENR.PRSC.FM.ZS [total] | konteks | 0 | — | definisi berbeda: jenjang berbeda (PT vs SD dan menengah); skala BPS x100, WDI x1 |
| P3 | var2595 [total] | — | konteks | 0 | — | tidak ada seri paritas kuintil di paket pembanding |

## 2. Rincian Keterbandingan per Pasangan

### P1: Penyelesaian SD: BPS (kohort umur) vs WDI (rasio masuk kasar kelas terakhir)
- Seri utama: `var1980` (rincian `jenjang=sd`)
- Pembanding: `SE.PRM.CMPT.ZS` (rincian `total`)
- Jenis: **selisih**; tahun beririsan: 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023
- Dugaan kategori selisih (diuji di Sprint 2): definisi berbeda: umur 3-5 tahun di atas umur lulus (BPS) vs siswa baru kelas terakhir tanpa memandang umur (WDI)

Pertanyaan keterbandingan dan jawabannya:

1. **Definisi BPS?** var.note: persentase anak dan remaja yang menyelesaikan jenjang pendidikan pada rentang umur 1-3 tahun (standar SDG 3-5 tahun) di atas usia lulus normal, berbasis Susenas KOR (0-100%).
2. **Definisi WDI?** sourceNote: gross intake ratio to the last grade of primary education, tanpa memandang usia, dibagi populasi usia resmi kelas terakhir SD; nilai dapat melebihi 100%.

### P2: Paritas: BPS APK PT perempuan/laki-laki vs WDI GPI SD+menengah
- Seri utama: `var2600` (rincian `total`)
- Pembanding: `SE.ENR.PRSC.FM.ZS` (rincian `total`)
- Jenis: **konteks**; tahun beririsan: —
- Dugaan kategori selisih (diuji di Sprint 2): definisi berbeda: jenjang berbeda (PT vs SD dan menengah); skala BPS x100, WDI x1

Pertanyaan keterbandingan dan jawabannya:

1. **Jenis paritas sama?** Ya, sama-sama jenis kelamin (perempuan/laki-laki). Namun jenjangnya berbeda (Perguruan Tinggi vs Primer & Sekunder), skala berbeda (rasio_x100 vs rasio), dan tidak ada tahun beririsan karena WDI berakhir 2018 sedangkan BPS mulai 2020.

### P3: Paritas kuintil APK SMA (BPS): tanpa pembanding di paket
- Seri utama: `var2595` (rincian `total`)
- Pembanding: tidak ada di paket
- Jenis: **konteks**; tahun beririsan: —
- Dugaan kategori selisih (diuji di Sprint 2): tidak ada seri paritas kuintil di paket pembanding

Pertanyaan keterbandingan dan jawabannya:

1. **Apa jenis rasionya?** Rasio APK jenjang SMA untuk kuintil pengeluaran terendah dibagi kuintil tertinggi (judul JSON), bukan paritas jenis kelamin.
