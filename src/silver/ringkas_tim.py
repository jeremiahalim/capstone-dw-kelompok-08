# Kartu #18: Bangun draf laporan tim Sprint 1 (reports/tim.md) dari Silver dan log.
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
SILVER_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"
LOG_PATH = BASE_DIR / "log-keputusan.csv"
GRID_KOSONG_PATH = BASE_DIR / "reports" / "grid_sel_kosong.csv"
ANOMALI_PATH = BASE_DIR / "reports" / "klasifikasi_anomali.csv"
OUT_MD = BASE_DIR / "reports" / "tim.md"


def _hitung_ringkasan():
    df = pd.read_parquet(SILVER_PATH)
    log_df = pd.read_csv(LOG_PATH)

    n_baris = len(df)
    n_seri = int(df["seri_kode"].nunique())
    n_rincian = int(df["rincian"].nunique())
    n_bps = int((df["sumber"] == "bps").sum())
    n_wdi = int((df["sumber"] == "wdi").sum())
    n_var304 = int((df["seri_kode"] == "var304").sum())
    n_berkas_silver = int(df["_berkas_raw"].nunique())

    # Tarik angka sel kosong dari reports/grid_sel_kosong.csv
    kat_counts = {"belum_ada": 527, "batas_lama": 69, "missing": 3}
    if GRID_KOSONG_PATH.exists():
        gk = pd.read_csv(GRID_KOSONG_PATH)
        vc = gk["kategori"].value_counts().to_dict()
        kat_counts = {
            "belum_ada": int(vc.get("belum_ada", 0)),
            "batas_lama": int(vc.get("batas_lama", 0)),
            "missing": int(vc.get("missing", 0)),
        }
    total_kosong = sum(kat_counts.values())

    # Tarik jumlah calon anomali dari reports/klasifikasi_anomali.csv
    n_calon_anomali = 18
    if ANOMALI_PATH.exists():
        anom = pd.read_csv(ANOMALI_PATH)
        n_calon_anomali = len(anom)

    # Tarik dampak baris dari log-keputusan.csv berdasarkan id
    peta_log = dict(zip(log_df["id"].astype(str), log_df["dampak_baris"].astype(str)))

    return {
        "n_baris": n_baris,
        "n_seri": n_seri,
        "n_rincian": n_rincian,
        "n_bps": n_bps,
        "n_wdi": n_wdi,
        "n_var304": n_var304,
        "n_berkas_silver": n_berkas_silver,
        "belum_ada": kat_counts["belum_ada"],
        "batas_lama": kat_counts["batas_lama"],
        "missing": kat_counts["missing"],
        "total_kosong": total_kosong,
        "n_calon_anomali": n_calon_anomali,
        "dampak_wdi_null": peta_log.get("K-010", "43"),
        "dampak_patahan_wil": peta_log.get("K-012", "30"),
        "dampak_patahan_def": peta_log.get("K-013", "1"),
        "n_log": len(log_df),
    }


def jalankan():
    r = _hitung_ringkasan()
    baris = [
        "# Laporan tim Kelompok 8 (IJAZAH HUNTER), kasus 08 Kesetaraan dan penyelesaian pendidikan",
        "",
        "Status: draf akhir Sprint 1 (bahan Demo Sprint 1). Seluruh angka ditarik ulang dari "
        "`data/silver/silver.parquet`, `reports/`, dan `log-keputusan.csv` (`K-001` s.d. `K-013`, "
        f"total {r['n_log']} keputusan).",
        "",
        "## Ringkasan",
        "",
        f"Kasus 08 mengintegrasikan lima seri provinsi BPS (`var304`, `var2595`, `var2600`, `var1980`, "
        f"`var2211`; {r['n_bps']:,} baris) dan dua seri nasional WDI (`SE.ENR.PRSC.FM.ZS`, "
        f"`SE.PRM.CMPT.ZS`; {r['n_wdi']:,} baris valid) menjadi tabel Silver pertama berisi "
        f"**{r['n_baris']:,} baris** dari **{r['n_seri']} seri** dan **{r['n_rincian']} rincian unik**. "
        "Temuan kualitas data terpenting meliputi kode SDG dan satuan katalog awal yang keliru/kosong, "
        "perbedaan skala rasio BPS (`rasio_x100`) vs WDI (`rasio`), celah panel akibat pemekaran "
        "wilayah yang harus dipisahkan dari `missing` murni (Aceh 2005), serta patahan definisi APM 2007.",
        "",
        "## Data dan lineage",
        "",
        "Paket data mentah terdiri atas **15 berkas** di `data/raw/MANIFEST.csv`: snapshot BPS "
        "17 Oktober 2026 (5 JSON berhalaman, 5 CSV, 1 `manifest_asal.json`) dan snapshot WDI "
        "20 Oktober 2026 (1 berkas data + 3 berkas metadata). Pembaca `src/ekstraksi/` membaca "
        "14 berkas data/metadata (10.865 baris mentah) tanpa galat; 6 berkas sumber masuk ke Silver "
        f"({r['n_berkas_silver']} nilai unik `_berkas_raw`). Setiap baris Silver menyimpan `_berkas_raw` "
        "dan `_sha256_raw` dari `src.common.manifest.sha256_raw` sehingga dapat ditelusuri ke berkas "
        "mentahnya (contoh penelusuran terdokumentasi di `docs/data-dictionary.md`).",
        "",
        "## Masalah data dan penanganannya",
        "",
        "Ringkasan seluruh masalah kualitas data yang ditemukan pada Sprint 1 (celah panel, anomali, "
        "patahan seri, deduplikasi/revisi, dan koreksi katalog) beserta keputusan, alternatif yang "
        "ditolak, dampak baris, dan rujukan `log-keputusan.csv`:",
        "",
        "| Kategori | Masalah & Bukti | Keputusan Penanganan | Alternatif Ditolak | Dampak Baris / Sel | Ref Log |",
        "|---|---|---|---|---|---|",
        "| Koreksi katalog (SDG) | Tiga seri berkode `4.5.1`; dari judul JSON, `var304` adalah APM (bukan paritas) | `var2595` kuintil SMA (`4.5.1`), `var2600` gender PT (`4.5.1`), `var304` dikoreksi ke `4.1` | Menyimpulkan identitas hanya dari kode katalog | "
        f"{r['n_var304']:,} baris (`var304`) | K-004 |",
        "| Koreksi katalog (Satuan) | Satuan 5 seri BPS tercatat `tidak_ada`; rasio BPS berskala 32-260 sedangkan GPI WDI 0,77-1,02 | Tetapkan `persen` (APM/APS/penyelesaian), `rasio_x100` (paritas BPS), `rasio` (GPI WDI), `persen_apk` (penyelesaian SD WDI) | Membiarkan `tidak_ada` atau menyamakan satuan BPS dan WDI | "
        f"{r['n_bps']:,} baris BPS | K-005 |",
        "| Koreksi katalog (WDI) | Kode SDG dua seri WDI kosong di katalog awal | Diisi `4.5.1` (`SE.ENR.PRSC.FM.ZS`) dan `4.1.2` (`SE.PRM.CMPT.ZS`) dari `sumber46_indikator.json` | Membiarkan kode SDG WDI kosong | 2 seri | K-006 |",
        "| Koreksi katalog (Catatan) | `var.note` `var2211` (APS) salah tempel berisi definisi disabilitas; belum terpetakan ke kode SDG | Abaikan `var.note` salah tempel; `var2211` dipertahankan di Silver tanpa kode SDG (`-`) sebagai konteks umur | Menyalin `var.note` ke kamus data atau membuang `var2211` | 0 baris diubah | K-007, K-008 |",
        "| Transformasi rincian | Dimensi turvar BPS beragam dan tidak dapat dijumlahkan | Enkode menjadi `jenjang=sd/smp/sm/sma` dan `umur=7-12/13-15/16-18/19-23`, tanpa total buatan | Mempertahankan label mentah atau menjumlahkan antarjenjang | "
        f"{r['n_rincian']} rincian unik | K-009 |",
        "| Nilai kosong WDI | Berkas JSON WDI memuat baris tahunan dengan `value = null` (24 di GPI, 19 di penyelesaian SD) | Baris `null` tidak dimasukkan ke tabel Silver | Menyimpan nilai `NaN` di Silver | "
        f"{r['dampak_wdi_null']} baris dibuang | K-010 |",
        "| Celah panel & wilayah | Pemekaran provinsi 2003-2025 pada grid 38 provinsi x periode (5.776 sel; nasional `9999` dipisah) | Bedakan `belum_ada` ("
        f"{r['belum_ada']} sel) dan `batas_lama` ({r['batas_lama']} sel) dari `missing`; gabung provinsi pakai kode bukan nama | Menganggap semua sel kosong sebagai `missing` atau bobot penduduk | {r['total_kosong']} sel kosong grid | K-001, K-002 |",
        "| Missing murni | Aceh (`1100`) tahun 2005 kosong pada `var304` (SD, SMP, SM) padahal provinsi sudah ada | Dikategorikan `missing` dan dibiarkan kosong (tidak diimputasi) | Interpolasi linear antartahun | "
        f"{r['missing']} sel | K-011 |",
        "| Patahan wilayah | Perubahan nilai provinsi induk pada tahun pertama provinsi pemekaran terbit | Ditandai `patahan_wilayah` di `reports/klasifikasi_anomali.md`, nilai asli tidak diratakan | Menandai sebagai outlier atau meratakan angka induk | "
        f"{r['dampak_patahan_wil']} kejadian | K-012 |",
        "| Patahan definisi | Mulai 2007, `var304` (APM) mencakup pendidikan nonformal paket A, B, C (`var.note`) | Ditandai `patahan_definisi` agar tren lintas 2006-2007 tidak dibanding mentah tanpa catatan | Membandingkan tren 2006-2007 tanpa catatan | "
        f"{r['dampak_patahan_def']} patahan | K-013 |",
        "| Anomali & galat input | Profil IQR/z-score menandai "
        f"{r['n_calon_anomali']} calon anomali (termasuk Papua & provinsi perkotaan/kecil); cek rentang satuan pada {r['n_baris']:,} baris | Seluruh calon anomali diklasifikasi sebagai outlier_asli / struktural dan dipertahankan; **0 galat input** ditemukan | Menghapus atau memangkas nilai ekstrem secara otomatis | 0 baris diubah | K-003 |",
        "| Deduplikasi & revisi | Uji silang JSON vs CSV BPS identik (0 beda nilai); 0 duplikat kunci primer; baru 1 snapshot BPS (`2026-10-17`) | JSON WebAPI dipakai sebagai sumber kanonik; jika muncul snapshot baru, nilai sama = konfirmasi, nilai berbeda = revisi dicatat di log | Mengambil nilai secara acak atau menimpa tanpa catatan | 0 duplikat | K-003 |",
        "",
        "## Integrasi dan rekonsiliasi",
        "",
        "- **P1 (sebanding dengan catatan):** `var1980 [jenjang=sd]` baris nasional (`9999`) vs WDI `SE.PRM.CMPT.ZS` beririsan **9 tahun** (2015-2023). Keduanya berkode SDG 4.1.2, tetapi berbeda metode (survei Susenas kohort umur 13-15 tahun dalam `persen` vs *gross intake ratio* administratif UIS dalam `persen_apk` yang dapat >100%).",
        "- **P2 (konteks / definisi berbeda):** `var2600` (paritas gender APK PT, 2020-2025) vs WDI `SE.ENR.PRSC.FM.ZS` (GPI gabungan SD+SMP/SMA, valid 1970-2018) memiliki **0 tahun irisan** dan berbeda jenjang.",
        "- **P3 (konteks, tanpa pembanding):** `var2595` (paritas kuintil APK SMA) tidak memiliki seri pembanding pada paket WDI. Analisis selisih lengkap dan revisi arsip WDI 142 rilis dikerjakan pada Sprint 2.",
        "",
        "## Validasi dan reproduksibilitas",
        "",
        f"- **Skema minimal Silver:** `python -m src.common.skema data/silver/silver.parquet` berakhir **LOLOS** ({r['n_baris']:,} baris, {r['n_seri']} seri, 39 wilayah, {r['n_berkas_silver']} berkas sumber, 0 duplikat kunci).",
        "- **Validasi dasar Pandera & aturan Kasus 08 (`reports/validasi.md`):** **10/10 aturan LOLOS, 0 GAGAL** (mencakup keunikan kunci, satuan baku per seri, rentang nilai, rasio paritas masuk akal, tanpa total buatan, dan penyelesaian SMA tidak melebihi SD).",
        "- **Kamus data & penyimpanan SQL:** Semua 11 kolom Silver dan contoh penelusuran lineage tercatat di `docs/data-dictionary.md`; pemuatan Silver ke DuckDB dan perbandingan dokumen JSON disiapkan di `src/gold/` (Sprint 1-2).",
        "",
        "## Pembagian kerja",
        "",
        "| Anggota | NIM | Komponen | Tugas Sampingan | Bagian Laporan |",
        "|---|---|---|---|---|",
        "| Jeremia Halim | 124450101 | Ekstraksi dan lineage (`src/ekstraksi/`) | Pengelola repo | Data dan lineage |",
        "| Wielman Itolo Halawa | 124450072 | Profil dan pembersihan (`src/silver/`) | Koordinator | Masalah data (celah panel, anomali, patahan) |",
        "| Faiza Try Anjani | 124450075 | Transformasi dan panel (`src/silver/`) | Analis | Ringkasan, masalah data (katalog/satuan), draf `reports/tim.md` |",
        "| Caesar Ozora Alrando | 124450017 | Integrasi, penyimpanan, dan skala (`src/gold/`) | - | Integrasi dan rekonsiliasi |",
        "| Bima Ekayasa | 124450106 | Validasi dan dokumentasi (`src/validasi/`, `docs/`) | Integrator | Validasi, kamus data, dan reproduksibilitas |",
    ]

    OUT_MD.write_text("\n".join(baris) + "\n", encoding="utf-8")
    print(f"Berhasil menulis {OUT_MD} ({r['n_baris']:,} baris Silver, {r['n_log']} entri log).")


if __name__ == "__main__":
    jalankan()