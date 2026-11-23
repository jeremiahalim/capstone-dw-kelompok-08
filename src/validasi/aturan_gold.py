# Tahap 8 Sprint 2 (Kartu #25): Validasi Gold (panel, lineage, nasional) dan
# rekonsiliasi.
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
SILVER_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"
GOLD_DIR = BASE_DIR / "data" / "gold"
PANEL_WIDE_PATH = GOLD_DIR / "panel_provinsi.parquet"
PANEL_LINEAGE_PATH = GOLD_DIR / "panel_lineage.parquet"
NASIONAL_PATH = GOLD_DIR / "tabel_nasional.parquet"
REKONSILIASI_PATH = GOLD_DIR / "rekonsiliasi.parquet"
OUT_MD = BASE_DIR / "reports" / "validasi_gold.md"

KATEGORI_SAH = {"definisi", "metode", "vintage", "cakupan", "belum_terjelaskan"}
ASAL_SAH = {"baris_indonesia", "agregat", "pembanding"}


def _df_ke_md(df):
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    return "\n".join(lines)


def _cek_kunci_panel_provinsi(wide):
    dup = int(wide.duplicated(["wilayah_kode", "periode"]).sum())
    ada_nas = int((wide["wilayah_kode"] == 9999).sum())
    ok = (dup == 0) and (ada_nas == 0)
    return ok, f"duplikat={dup}, baris_9999={ada_nas}, total={len(wide)}"


def _cek_kunci_panel_lineage(lineage):
    dup = int(
        lineage.duplicated(["wilayah_kode", "periode", "indikator_gold"]).sum()
    )
    return dup == 0, f"duplikat={dup}, total_sel={len(lineage)}"


def _cek_satu_satuan_per_indikator(wide, lineage):
    n_sat_asli = lineage.groupby("indikator_gold")["satuan_asli"].nunique()
    n_sat_gold = lineage.groupby("indikator_gold")["satuan_gold"].nunique()
    buruk_asli = int((n_sat_asli != 1).sum())
    buruk_gold = int((n_sat_gold != 1).sum())
    wajib_pisah = {
        "penyelesaian_sd", "penyelesaian_smp", "penyelesaian_sma",
        "paritas_kuintil_sma_x100", "paritas_kuintil_sma_rasio",
        "paritas_gender_pt_x100", "paritas_gender_pt_rasio",
    }
    kurang = sorted(wajib_pisah - set(wide.columns))
    ok = (buruk_asli == 0) and (buruk_gold == 0) and (len(kurang) == 0)
    return ok, (
        f"indikator_multi_satuan={buruk_asli + buruk_gold}, "
        f"kolom_kurang={len(kurang)}"
    )


def _cek_pasangan_silver(silver, lineage):
    kunci_cols = [
        "sumber", "seri_kode", "wilayah_kode", "periode", "rincian",
        "_berkas_raw",
    ]
    kunci_silver = set(zip(*(silver[c].astype(str) for c in kunci_cols)))
    kunci_gold = list(zip(*(lineage[c].astype(str) for c in kunci_cols)))
    yatim = sum(1 for k in kunci_gold if k not in kunci_silver)
    return yatim == 0, (
        f"sel_tanpa_pasangan_silver={yatim}, diperiksa={len(kunci_gold)}"
    )


def _cek_tabel_nasional(nas):
    dup = int(nas.duplicated(["periode", "seri_kode", "rincian"]).sum())
    asal_buruk = int((~nas["asal_angka"].isin(ASAL_SAH)).sum())
    raw_kosong = int(nas["_berkas_raw"].isna().sum())
    ok = (dup == 0) and (asal_buruk == 0) and (raw_kosong == 0)
    return ok, (
        f"duplikat={dup}, asal_tidak_sah={asal_buruk}, "
        f"berkas_raw_kosong={raw_kosong}"
    )


def _cek_rekonsiliasi(rek):
    dup = int(rek.duplicated(["id_pasangan", "periode"]).sum())
    berpasangan = rek[
        rek["nilai_utama"].notna() & rek["nilai_pembanding"].notna()
    ]
    kat_buruk = int(
        (~berpasangan["kategori_selisih"].isin(KATEGORI_SAH)).sum()
    )
    sel_kosong = int(berpasangan["selisih"].isna().sum())
    ket_kosong = int(
        (berpasangan["penjelasan"].fillna("").str.strip() == "").sum()
    )
    ok = (
        (dup == 0)
        and (len(berpasangan) > 0)
        and (kat_buruk == 0)
        and (sel_kosong == 0)
        and (ket_kosong == 0)
    )
    return ok, (
        f"duplikat={dup}, baris_berpasangan={len(berpasangan)}, "
        f"kategori_tidak_sah={kat_buruk}, selisih_kosong={sel_kosong}"
    )


def jalankan(silver=None, gold=None):
    if silver is None:
        silver = pd.read_parquet(SILVER_PATH)

    berkas_wajib = [
        PANEL_WIDE_PATH, PANEL_LINEAGE_PATH, NASIONAL_PATH, REKONSILIASI_PATH,
    ]
    belum_ada = [p.name for p in berkas_wajib if not p.exists()]
    if belum_ada:
        raise FileNotFoundError(
            f"Berkas Gold belum lengkap untuk validasi: {belum_ada}. "
            "Pastikan Kartu #21, #22, dan #24 sudah dijalankan."
        )

    wide = pd.read_parquet(PANEL_WIDE_PATH)
    lineage = pd.read_parquet(PANEL_LINEAGE_PATH)
    nas = pd.read_parquet(NASIONAL_PATH)
    rek = pd.read_parquet(REKONSILIASI_PATH)

    daftar_cek = [
        (
            "kunci_panel_provinsi_unik",
            "keras (gold)",
            "kunci (wilayah_kode, periode) unik & tanpa baris 9999",
            _cek_kunci_panel_provinsi(wide),
        ),
        (
            "kunci_panel_lineage_unik",
            "keras (gold)",
            "kunci (wilayah_kode, periode, indikator_gold) unik",
            _cek_kunci_panel_lineage(lineage),
        ),
        (
            "satu_satuan_per_indikator_gold",
            "keras (gold)",
            "tiap indikator punya 1 satuan; paritas terpisah dari partisipasi",
            _cek_satu_satuan_per_indikator(wide, lineage),
        ),
        (
            "setiap_sel_gold_punya_pasangan_di_silver",
            "keras (gold)",
            "100% sel panel_lineage cocok 1-ke-1 dengan kunci Silver",
            _cek_pasangan_silver(silver, lineage),
        ),
        (
            "tabel_nasional_gold_valid",
            "keras (gold)",
            "kunci nasional unik, asal_angka sah, _berkas_raw terisi",
            _cek_tabel_nasional(nas),
        ),
        (
            "rekonsiliasi_berpasangan_berkategori",
            "keras (rekonsiliasi)",
            "tiap baris berpasangan punya selisih & kategori sah",
            _cek_rekonsiliasi(rek),
        ),
    ]

    baris = []
    for nama, jenis, ket, (ok, detail) in daftar_cek:
        baris.append({
            "aturan": nama,
            "jenis": jenis,
            "keterangan": ket,
            "hasil": "LOLOS" if ok else "GAGAL",
            "detail": detail,
        })
    tabel = pd.DataFrame(baris)

    n_total = len(tabel)
    n_lolos = int((tabel["hasil"] == "LOLOS").sum())
    n_gagal = n_total - n_lolos

    md = [
        "# Hasil Validasi Gold & Rekonsiliasi (Kartu #25)",
        "",
        f"Dihasilkan otomatis oleh `src/validasi/aturan_gold.py` dari "
        f"`python pipeline.py`. "
        f"Ringkasan: **{n_lolos}/{n_total} aturan Gold LOLOS**, "
        f"**{n_gagal} GAGAL** "
        f"(gabungan bersama 10 aturan Silver: "
        f"**{10 + n_lolos}/{10 + n_total} LOLOS**).",
        "",
        _df_ke_md(tabel),
        "",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(
        f"validasi_gold: {n_lolos}/{n_total} aturan LOLOS "
        f"({n_gagal} GAGAL) -> {OUT_MD.name}"
    )
    if n_gagal > 0:
        gagal_nama = ", ".join(tabel.loc[tabel["hasil"] == "GAGAL", "aturan"])
        raise SystemExit(
            f"Validasi Gold gagal pada aturan: {gagal_nama}. "
            "Lihat reports/validasi_gold.md"
        )
    return tabel


if __name__ == "__main__":
    jalankan()
    