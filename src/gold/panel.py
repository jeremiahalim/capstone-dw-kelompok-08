# Kartu #21: Bentuk panel Gold provinsi x periode x indikator dari Silver.
import re
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
SILVER_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"
GOLD_DIR = BASE_DIR / "data" / "gold"
PANEL_WIDE_PATH = GOLD_DIR / "panel_provinsi.parquet"
PANEL_LINEAGE_PATH = GOLD_DIR / "panel_lineage.parquet"
OUT_MD = BASE_DIR / "reports" / "panel_gold.md"

PETA_KOLOM = {
    ("var1980", "jenjang=sd"): ("penyelesaian_sd", "persen", "persen", 1.0),
    ("var1980", "jenjang=smp"): ("penyelesaian_smp", "persen", "persen", 1.0),
    ("var1980", "jenjang=sma"): ("penyelesaian_sma", "persen", "persen", 1.0),
    ("var304", "jenjang=sd"): ("apm_sd", "persen", "persen", 1.0),
    ("var304", "jenjang=smp"): ("apm_smp", "persen", "persen", 1.0),
    ("var304", "jenjang=sm"): ("apm_sm", "persen", "persen", 1.0),
    ("var2211", "umur=7-12"): ("aps_7_12", "persen", "persen", 1.0),
    ("var2211", "umur=13-15"): ("aps_13_15", "persen", "persen", 1.0),
    ("var2211", "umur=16-18"): ("aps_16_18", "persen", "persen", 1.0),
    ("var2211", "umur=19-23"): ("aps_19_23", "persen", "persen", 1.0),
    ("var2595", "total"): ("paritas_kuintil_sma_x100", "rasio_x100", "rasio", 0.01),
    ("var2600", "total"): ("paritas_gender_pt_x100", "rasio_x100", "rasio", 0.01),
}

URUTAN_KOLOM_WIDE = [
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "penyelesaian_sd",
    "penyelesaian_smp",
    "penyelesaian_sma",
    "apm_sd",
    "apm_smp",
    "apm_sm",
    "aps_7_12",
    "aps_13_15",
    "aps_16_18",
    "aps_19_23",
    "paritas_kuintil_sma_x100",
    "paritas_kuintil_sma_rasio",
    "paritas_gender_pt_x100",
    "paritas_gender_pt_rasio",
    "ada_patahan_definisi",
    "ada_patahan_wilayah",
    "ada_outlier",
    "jumlah_sumber_berkas",
    "sumber_berkas_raw",
]


def _seleksi_dengan_fallback(silver):
    # Pakai aturan_seleksi dari Kartu #20 bila tersedia; bila belum, jalankan aturan identik.
    try:
        from src.gold.aturan_seleksi import pilih_sel_gold
        df_sel, _ = pilih_sel_gold(silver)
        return df_sel
    except ImportError:
        d = silver[(silver["wilayah_kode"] != 9999) & (silver["jenis_periode"] == "tahun")].copy()
        d = d[[k in PETA_KOLOM for k in zip(d["seri_kode"], d["rincian"])]].copy()
        d["indikator_gold"] = [PETA_KOLOM[k][0] for k in zip(d["seri_kode"], d["rincian"])]
        d["_tgl"] = d["_berkas_raw"].map(
            lambda s: re.search(r"(\d{4}-\d{2}-\d{2})", str(s)).group(1)
            if re.search(r"(\d{4}-\d{2}-\d{2})", str(s))
            else "0000-00-00"
        )
        d["_json"] = d["_berkas_raw"].str.endswith(".json").astype(int)
        d = d.sort_values(
            ["wilayah_kode", "periode", "indikator_gold", "_tgl", "_json", "_berkas_raw"],
            ascending=[True, True, True, False, False, False],
        ).drop_duplicates(["wilayah_kode", "periode", "indikator_gold"], keep="first")
        d["flag_patahan_definisi"] = (d["seri_kode"] == "var304") & (d["periode"].astype(str) == "2007")
        d["flag_patahan_wilayah"] = False
        d["flag_outlier"] = False
        return d.drop(columns=["_tgl", "_json"]).reset_index(drop=True)


def bangun_panel(silver):
    sel = _seleksi_dengan_fallback(silver).copy()

    # Standardisasi nama kolom indikator & nilai seragam (simpan asli + normalisasi rasio)
    info = [PETA_KOLOM[(s, r)] for s, r in zip(sel["seri_kode"], sel["rincian"])]
    sel["indikator_gold"] = [x[0] for x in info]
    sel["satuan_asli"] = [x[1] for x in info]
    sel["satuan_gold"] = [x[2] for x in info]
    faktor = [x[3] for x in info]
    sel["nilai_asli"] = sel["nilai"].astype("float64")
    sel["nilai_seragam"] = (sel["nilai_asli"] * pd.Series(faktor, index=sel.index)).round(6)

    # 1. Tabel lineage 1-ke-1 sel Gold -> baris Silver
    kol_lin = [
        "wilayah_kode", "nama_wilayah", "periode", "indikator_gold",
        "sumber", "seri_kode", "rincian",
        "nilai_asli", "satuan_asli", "nilai_seragam", "satuan_gold",
        "flag_patahan_definisi", "flag_patahan_wilayah", "flag_outlier",
        "_berkas_raw", "_sha256_raw",
    ]
    lineage = sel[kol_lin].sort_values(["wilayah_kode", "periode", "indikator_gold"]).reset_index(drop=True)
    dup_lin = int(lineage.duplicated(["wilayah_kode", "periode", "indikator_gold"]).sum())
    if dup_lin > 0:
        raise ValueError(f"Kunci panel_lineage kembar: {dup_lin} baris")

    # 2. Panel lebar provinsi x periode
    nama_map = (
        lineage.sort_values(["wilayah_kode", "periode"])
        .drop_duplicates("wilayah_kode", keep="last")
        .set_index("wilayah_kode")["nama_wilayah"]
        .to_dict()
    )
    wide = lineage.pivot(
        index=["wilayah_kode", "periode"], columns="indikator_gold", values="nilai_asli"
    ).reset_index()
    wide.columns.name = None
    wide["nama_wilayah"] = wide["wilayah_kode"].map(nama_map)

    # Tambah versi ternormalisasi rasio (/100) berdampingan dengan versi asli x100
    wide["paritas_kuintil_sma_rasio"] = (wide["paritas_kuintil_sma_x100"] / 100.0).round(6)
    wide["paritas_gender_pt_rasio"] = (wide["paritas_gender_pt_x100"] / 100.0).round(6)

    # Gabungkan penanda Sprint 1 dan daftar berkas asal per baris panel
    agg_flag = lineage.groupby(["wilayah_kode", "periode"], as_index=False).agg(
        ada_patahan_definisi=("flag_patahan_definisi", "any"),
        ada_patahan_wilayah=("flag_patahan_wilayah", "any"),
        ada_outlier=("flag_outlier", "any"),
        jumlah_sumber_berkas=("_berkas_raw", "nunique"),
        sumber_berkas_raw=("_berkas_raw", lambda s: "; ".join(sorted(set(s)))),
    )
    wide = wide.merge(agg_flag, on=["wilayah_kode", "periode"], how="left")
    wide = wide[URUTAN_KOLOM_WIDE].sort_values(["wilayah_kode", "periode"]).reset_index(drop=True)

    dup_wide = int(wide.duplicated(["wilayah_kode", "periode"]).sum())
    if dup_wide > 0:
        raise ValueError(f"Kunci panel_provinsi kembar: {dup_wide} baris")

    return wide, lineage


def _tulis_ringkasan(wide, lineage):
    seri_unik = sorted(lineage["seri_kode"].unique())
    baris = [
        "# Ringkasan Panel Gold Provinsi x Periode x Indikator (Kartu #21)",
        "",
        "Dihasilkan otomatis oleh `src/gold/panel.py` dari `data/silver/silver.parquet`.",
        "",
        f"- **Panel lebar (`data/gold/panel_provinsi.parquet`):** **{len(wide):,} baris** "
        f"({wide['wilayah_kode'].nunique()} provinsi, periode {wide['periode'].min()}-{wide['periode'].max()}, "
        f"0 duplikat kunci `wilayah_kode, periode`).",
        f"- **Lineage sel Gold (`data/gold/panel_lineage.parquet`):** **{len(lineage):,} sel** "
        f"({len(seri_unik)} seri utama: `{', '.join(seri_unik)}`, 0 duplikat kunci `wilayah_kode, periode, indikator_gold`).",
        "- **Pemisahan satuan & versi asli:** tingkat penyelesaian melebar per jenjang (`penyelesaian_sd/smp/sma`, `persen`), "
        "partisipasi dalam kolom terpisah (`apm_*`, `aps_*`, `persen`), dan rasio paritas terpisah dengan versi asli "
        "`rasio_x100` (`paritas_*_x100`) berdampingan dengan versi normalisasi `rasio` (`paritas_*_rasio` = nilai / 100).",
        "- **Penanda Sprint 1 terbawa:** "
        f"`ada_patahan_definisi`={int(wide['ada_patahan_definisi'].sum())} baris, "
        f"`ada_patahan_wilayah`={int(wide['ada_patahan_wilayah'].sum())} baris, "
        f"`ada_outlier`={int(wide['ada_outlier'].sum())} baris.",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(baris) + "\n", encoding="utf-8")


def jalankan(silver=None):
    if silver is None:
        silver = pd.read_parquet(SILVER_PATH)
    wide, lineage = bangun_panel(silver)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    wide.to_parquet(PANEL_WIDE_PATH, index=False)
    lineage.to_parquet(PANEL_LINEAGE_PATH, index=False)
    _tulis_ringkasan(wide, lineage)
    print(
        f"panel_gold: {len(wide):,} baris panel lebar ({PANEL_WIDE_PATH.name}), "
        f"{len(lineage):,} sel lineage ({PANEL_LINEAGE_PATH.name}), "
        f"seri_panel={lineage['seri_kode'].nunique()}"
    )
    return {"panel_provinsi": wide, "panel_lineage": lineage}


if __name__ == "__main__":
    jalankan()