# Kartu #20: Aturan satu nilai per sel Gold (provinsi x periode x indikator).
import re
from pathlib import Path

import pandas as pd

from src.silver.deteksi_anomali_bps import deteksi_patahan_wilayah

BASE_DIR = Path(__file__).resolve().parents[2]
SILVER_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"
ANOMALI_PATH = BASE_DIR / "reports" / "klasifikasi_anomali.csv"
OUT_MD = BASE_DIR / "reports" / "aturan_seleksi_gold.md"

# Pemetaan (seri_kode, rincian) -> (nama kolom indikator Gold, kelompok satuan/ukuran)
# Tingkat penyelesaian melebar per jenjang; rasio paritas dipisah dari angka partisipasi.
PETA_INDIKATOR = {
    ("var1980", "jenjang=sd"): ("penyelesaian_sd", "penyelesaian"),
    ("var1980", "jenjang=smp"): ("penyelesaian_smp", "penyelesaian"),
    ("var1980", "jenjang=sma"): ("penyelesaian_sma", "penyelesaian"),
    ("var304", "jenjang=sd"): ("apm_sd", "partisipasi"),
    ("var304", "jenjang=smp"): ("apm_smp", "partisipasi"),
    ("var304", "jenjang=sm"): ("apm_sm", "partisipasi"),
    ("var2211", "umur=7-12"): ("aps_7_12", "partisipasi"),
    ("var2211", "umur=13-15"): ("aps_13_15", "partisipasi"),
    ("var2211", "umur=16-18"): ("aps_16_18", "partisipasi"),
    ("var2211", "umur=19-23"): ("aps_19_23", "partisipasi"),
    ("var2595", "total"): ("paritas_kuintil_sma", "paritas"),
    ("var2600", "total"): ("paritas_gender_pt", "paritas"),
}


def _ekstrak_tgl_snapshot(berkas_raw):
    m = re.search(r"(\d{4}-\d{2}-\d{2})", str(berkas_raw))
    return m.group(1) if m else "0000-00-00"


def _norm_rincian_anomali(rc_raw):
    s = str(rc_raw).strip()
    lo = s.lower()
    if lo in ("tidak ada", "total", "nan", ""):
        return "total"
    peta = {
        "sd/sederajat": "jenjang=sd",
        "sd": "jenjang=sd",
        "smp/sederajat": "jenjang=smp",
        "smp": "jenjang=smp",
        "sm/sederajat": "jenjang=sm",
        "sm": "jenjang=sm",
        "sma/sederajat": "jenjang=sma",
        "sma": "jenjang=sma",
        "7-12": "umur=7-12",
        "13-15": "umur=13-15",
        "16-18": "umur=16-18",
        "19-23": "umur=19-23",
    }
    return peta.get(lo, s)


def pilih_sel_gold(silver):
    # Mengembalikan (df_terpilih, ringkasan_dict) dengan tepat 1 baris per
    # provinsi x periode x indikator.
    df = silver.copy()
    total_awal = len(df)

    # Aturan 1 (K-014): Pisahkan baris nasional (9999) dari panel provinsi Gold
    mask_prov = df["wilayah_kode"] != 9999
    d1 = df[mask_prov].copy()
    tidak_terpilih_nasional = total_awal - len(d1)
    nasional_bps = int(((df["wilayah_kode"] == 9999) & (df["sumber"] == "bps")).sum())
    nasional_wdi = int(((df["wilayah_kode"] == 9999) & (df["sumber"] == "wdi")).sum())

    # Aturan 2 (K-015): Pertahankan periode tahunan; sub-tahunan tidak dirata-rata paksa
    d2 = d1[d1["jenis_periode"] == "tahun"].copy()
    tidak_terpilih_periode = len(d1) - len(d2)

    # Aturan 3 (K-016): Pemetaan rincian sebanding ke 12 indikator panel Gold
    kunci_sr = list(zip(d2["seri_kode"], d2["rincian"]))
    mask_map = [k in PETA_INDIKATOR for k in kunci_sr]
    d3 = d2[mask_map].copy()
    tidak_terpilih_rincian = len(d2) - len(d3)
    d3["indikator_gold"] = [
        PETA_INDIKATOR[k][0] for k in zip(d3["seri_kode"], d3["rincian"])
    ]
    d3["kelompok_ukuran"] = [
        PETA_INDIKATOR[k][1] for k in zip(d3["seri_kode"], d3["rincian"])
    ]

    # Aturan 4 (K-017): Bila ada >1 snapshot pada sel sama, pilih snapshot terbaru & format JSON kanonik
    d3["_snapshot_tgl"] = d3["_berkas_raw"].map(_ekstrak_tgl_snapshot)
    d3["_prioritas_json"] = d3["_berkas_raw"].str.endswith(".json").astype(int)
    d3 = d3.sort_values(
        by=[
            "wilayah_kode",
            "periode",
            "indikator_gold",
            "_snapshot_tgl",
            "_prioritas_json",
            "_berkas_raw",
        ],
        ascending=[True, True, True, False, False, False],
    )
    sebelum_snap = len(d3)
    d4 = d3.drop_duplicates(
        subset=["wilayah_kode", "periode", "indikator_gold"], keep="first"
    ).copy()
    tidak_terpilih_snapshot = sebelum_snap - len(d4)
    d4 = d4.drop(columns=["_prioritas_json"])

    # Penanda Sprint 1 dibawa utuh ke Gold (nilai tidak dihapus)
    d4["flag_patahan_definisi"] = (d4["seri_kode"] == "var304") & (
        d4["periode"].astype(str) == "2007"
    )

    pw = deteksi_patahan_wilayah(df)
    pw_keys = set()
    for _, r in pw.iterrows():
        s_raw = str(r["seri_kode"])
        if "[" in s_raw:
            sk = s_raw.split("[")[0].strip()
            rc = s_raw.split("[")[1].replace("]", "").strip()
        else:
            sk, rc = s_raw.strip(), "total"
        pw_keys.add((sk, rc, int(r["wilayah_kode"]), str(r["periode"])))

    d4["flag_patahan_wilayah"] = [
        (r.seri_kode, r.rincian, int(r.wilayah_kode), str(r.periode)) in pw_keys
        for r in d4.itertuples(index=False)
    ]

    out_keys = set()
    if ANOMALI_PATH.exists():
        anom = pd.read_csv(ANOMALI_PATH)
        for _, r in anom.iterrows():
            sk = str(r["Seri"]).split()[0].strip()
            wil = str(r["Wilayah"]).strip().upper()
            rc = _norm_rincian_anomali(r["Rincian"])
            per = str(r["Periode"]).strip()
            out_keys.add((sk, wil, rc, per))

    d4["flag_outlier"] = [
        (
            r.seri_kode,
            str(r.nama_wilayah).strip().upper(),
            r.rincian,
            str(r.periode),
        )
        in out_keys
        for r in d4.itertuples(index=False)
    ]

    duplikat = int(
        d4.duplicated(subset=["wilayah_kode", "periode", "indikator_gold"]).sum()
    )
    if duplikat > 0:
        raise ValueError(f"Sel Gold tidak unik: ditemukan {duplikat} duplikat!")

    d4 = d4.reset_index(drop=True)
    ringkasan = {
        "total_silver": total_awal,
        "terpilih_gold": len(d4),
        "tidak_terpilih_total": total_awal - len(d4),
        "tidak_terpilih_nasional": tidak_terpilih_nasional,
        "nasional_bps": nasional_bps,
        "nasional_wdi": nasional_wdi,
        "tidak_terpilih_periode": tidak_terpilih_periode,
        "tidak_terpilih_rincian": tidak_terpilih_rincian,
        "tidak_terpilih_snapshot": tidak_terpilih_snapshot,
        "duplikat_sel_gold": duplikat,
        "flag_patahan_definisi": int(d4["flag_patahan_definisi"].sum()),
        "flag_patahan_wilayah": int(d4["flag_patahan_wilayah"].sum()),
        "flag_outlier": int(d4["flag_outlier"].sum()),
    }
    return d4, ringkasan


def _tulis_laporan(ringkasan):
    baris = [
        "# Audit Aturan Seleksi Satu Nilai per Sel Gold (Kartu #20)",
        "",
        "Dihasilkan otomatis oleh `src/gold/aturan_seleksi.py` (dipanggil dari `python pipeline.py`).",
        "",
        "## 1. Ringkasan Pemilihan Baris Silver ke Panel Provinsi Gold",
        "| Tahap / Aturan | Ref Log | Baris Silver Tidak Terpilih | Keterangan |",
        "| --- | --- | ---: | --- |",
        f"| Pemisahan wilayah nasional (`wilayah_kode = 9999`) | K-014 | {ringkasan['tidak_terpilih_nasional']} | {ringkasan['nasional_bps']} BPS nasional + {ringkasan['nasional_wdi']} WDI dialihkan ke tabel nasional Gold & rekonsiliasi |",
        f"| Saringan periode sub-tahunan (`jenis_periode != tahun`) | K-015 | {ringkasan['tidak_terpilih_periode']} | Seluruh baris Kasus 08 tahunan; sub-tahunan tidak dirata-rata paksa |",
        f"| Pemetaan rincian sebanding ke 12 indikator Gold | K-016 | {ringkasan['tidak_terpilih_rincian']} | Seluruh 12 kombinasi provinsi masuk panel lebar terpisah per satuan |",
        f"| Pemilihan snapshot terbaru & format JSON kanonik | K-017 | {ringkasan['tidak_terpilih_snapshot']} | Saat ini 1 snapshot BPS (2026-10-17); bila ada >1, tanggal terbaru menang |",
        f"| **Total baris Silver masuk** | - | **{ringkasan['total_silver']:,}** | **Terpilih ke sel Gold: {ringkasan['terpilih_gold']:,} baris (duplikat sel = {ringkasan['duplikat_sel_gold']})** |",
        "",
        "## 2. Penanda Patahan & Outlier Sprint 1 yang Terbawa Utuh",
        f"- `flag_patahan_definisi`: **{ringkasan['flag_patahan_definisi']} sel** (`var304` tahun 2007, `K-013`).",
        f"- `flag_patahan_wilayah`: **{ringkasan['flag_patahan_wilayah']} sel** (provinsi induk tahun pemekaran, `K-012`).",
        f"- `flag_outlier`: **{ringkasan['flag_outlier']} sel** (calon anomali IQR dipertahankan tanpa diubah, `K-003`).",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(baris) + "\n", encoding="utf-8")


def jalankan(silver=None):
    if silver is None:
        silver = pd.read_parquet(SILVER_PATH)
    df_sel, ringkasan = pilih_sel_gold(silver)
    _tulis_laporan(ringkasan)
    print(
        f"aturan_seleksi: {ringkasan['terpilih_gold']:,}/{ringkasan['total_silver']:,} baris terpilih "
        f"({ringkasan['tidak_terpilih_total']} nasional disisihkan, duplikat={ringkasan['duplikat_sel_gold']}, "
        f"patahan_def={ringkasan['flag_patahan_definisi']}, patahan_wil={ringkasan['flag_patahan_wilayah']}, "
        f"outlier={ringkasan['flag_outlier']})"
    )
    return df_sel


if __name__ == "__main__":
    jalankan()