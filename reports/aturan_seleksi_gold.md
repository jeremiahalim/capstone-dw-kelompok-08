# Audit Aturan Seleksi Satu Nilai per Sel Gold (Kartu #20)

Dihasilkan otomatis oleh `src/gold/aturan_seleksi.py` (dipanggil dari `python pipeline.py`).

## 1. Ringkasan Pemilihan Baris Silver ke Panel Provinsi Gold
| Tahap / Aturan | Ref Log | Baris Silver Tidak Terpilih | Keterangan |
| --- | --- | ---: | --- |
| Pemisahan wilayah nasional (`wilayah_kode = 9999`) | K-014 | 241 | 152 BPS nasional + 89 WDI dialihkan ke tabel nasional Gold & rekonsiliasi |
| Saringan periode sub-tahunan (`jenis_periode != tahun`) | K-015 | 0 | Seluruh baris Kasus 08 tahunan; sub-tahunan tidak dirata-rata paksa |
| Pemetaan rincian sebanding ke 12 indikator Gold | K-016 | 0 | Seluruh 12 kombinasi provinsi masuk panel lebar terpisah per satuan |
| Pemilihan snapshot terbaru & format JSON kanonik | K-017 | 0 | Saat ini 1 snapshot BPS (2026-10-17); bila ada >1, tanggal terbaru menang |
| **Total baris Silver masuk** | - | **5,418** | **Terpilih ke sel Gold: 5,177 baris (duplikat sel = 0)** |

## 2. Penanda Patahan & Outlier Sprint 1 yang Terbawa Utuh
- `flag_patahan_definisi`: **99 sel** (`var304` tahun 2007, `K-013`).
- `flag_patahan_wilayah`: **30 sel** (provinsi induk tahun pemekaran, `K-012`).
- `flag_outlier`: **18 sel** (calon anomali IQR dipertahankan tanpa diubah, `K-003`).
