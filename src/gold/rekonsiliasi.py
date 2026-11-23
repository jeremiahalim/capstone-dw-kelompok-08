# Tahap 6 (Kartu #24): Tabel rekonsiliasi seri utama vs pembanding nasional.
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
NASIONAL_GOLD_PATH = BASE_DIR / "data" / "gold" / "tabel_nasional.parquet"
SILVER_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"
OUT_PQ = BASE_DIR / "data" / "gold" / "rekonsiliasi.parquet"
OUT_MD = BASE_DIR / "reports" / "rekonsiliasi.md"

KOLOM_REKONSILIASI = [
    "id_pasangan", "periode", "seri_utama", "rincian_utama", "seri_pembanding",
    "nilai_utama", "satuan_utama", "nilai_pembanding", "satuan_pembanding",
    "selisih", "selisih_absolut", "selisih_persen", "kategori_selisih",
    "penjelasan", "_berkas_raw_utama", "_berkas_raw_pembanding",
]


def _muat_nasional():
    if NASIONAL_GOLD_PATH.exists():
        return pd.read_parquet(NASIONAL_GOLD_PATH)
    df = pd.read_parquet(SILVER_PATH)
    return df[df["wilayah_kode"] == 9999].copy()


def _df_ke_md(df):
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for row in df.itertuples(index=False):
        vals = ["—" if pd.isna(v) else str(v) for v in row]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def bangun_rekonsiliasi():
    nas = _muat_nasional()
    semua = []

    # P1: var1980 [jenjang=sd] vs SE.PRM.CMPT.ZS (outer join agar periode tanpa pasangan tetap tampil)
    u1 = nas[(nas["seri_kode"] == "var1980") & (nas["rincian"] == "jenjang=sd")][
        ["periode", "nilai", "satuan", "_berkas_raw"]
    ].rename(columns={"nilai": "nilai_utama", "satuan": "satuan_utama", "_berkas_raw": "berkas_raw_utama"})
    p1 = nas[nas["seri_kode"] == "SE.PRM.CMPT.ZS"][
        ["periode", "nilai", "satuan", "_berkas_raw"]
    ].rename(columns={"nilai": "nilai_pembanding", "satuan": "satuan_pembanding", "_berkas_raw": "berkas_raw_pembanding"})

    m1 = pd.merge(u1, p1, on="periode", how="outer").sort_values("periode")
    for r in m1.itertuples(index=False):
        ada_u = pd.notna(r.nilai_utama)
        ada_p = pd.notna(r.nilai_pembanding)
        if ada_u and ada_p:
            sel = round(float(r.nilai_utama) - float(r.nilai_pembanding), 4)
            sel_abs = round(abs(sel), 4)
            sel_pct = round(sel_abs / float(r.nilai_pembanding) * 100.0, 2)
            ket = (
                "definisi berbeda: BPS mengukur penyelesaian SD kohort umur 13-15 tahun (Susenas, persen 0-100%), "
                "sedangkan WDI mengukur gross intake ratio kelas terakhir SD tanpa batas umur (UIS, persen_apk dapat >100%)"
            )
        else:
            sel, sel_abs, sel_pct = None, None, None
            ket = "definisi berbeda (cakupan periode tidak beririsan: seri utama var1980 baru terbit mulai 2015)"
        semua.append({
            "id_pasangan": "P1", "periode": str(r.periode), "seri_utama": "var1980",
            "rincian_utama": "jenjang=sd", "seri_pembanding": "SE.PRM.CMPT.ZS",
            "nilai_utama": float(r.nilai_utama) if ada_u else None,
            "satuan_utama": str(r.satuan_utama) if ada_u else "persen",
            "nilai_pembanding": float(r.nilai_pembanding) if ada_p else None,
            "satuan_pembanding": str(r.satuan_pembanding) if ada_p else "persen_apk",
            "selisih": sel, "selisih_absolut": sel_abs, "selisih_persen": sel_pct,
            "kategori_selisih": "definisi", "penjelasan": ket,
            "_berkas_raw_utama": str(r.berkas_raw_utama) if ada_u else "—",
            "_berkas_raw_pembanding": str(r.berkas_raw_pembanding) if ada_p else "—",
        })

    # P2: var2600 (paritas gender PT) vs SE.ENR.PRSC.FM.ZS (GPI SD+menengah) -> definisi berbeda, 0 irisan
    u2 = nas[nas["seri_kode"] == "var2600"][["periode", "nilai", "satuan", "_berkas_raw"]].rename(
        columns={"nilai": "nilai_utama", "satuan": "satuan_utama", "_berkas_raw": "berkas_raw_utama"}
    )
    p2 = nas[nas["seri_kode"] == "SE.ENR.PRSC.FM.ZS"][["periode", "nilai", "satuan", "_berkas_raw"]].rename(
        columns={"nilai": "nilai_pembanding", "satuan": "satuan_pembanding", "_berkas_raw": "berkas_raw_pembanding"}
    )
    m2 = pd.merge(u2, p2, on="periode", how="outer").sort_values("periode")
    for r in m2.itertuples(index=False):
        ada_u = pd.notna(r.nilai_utama)
        ada_p = pd.notna(r.nilai_pembanding)
        semua.append({
            "id_pasangan": "P2", "periode": str(r.periode), "seri_utama": "var2600",
            "rincian_utama": "total", "seri_pembanding": "SE.ENR.PRSC.FM.ZS",
            "nilai_utama": float(r.nilai_utama) if ada_u else None,
            "satuan_utama": str(r.satuan_utama) if ada_u else "rasio_x100",
            "nilai_pembanding": float(r.nilai_pembanding) if ada_p else None,
            "satuan_pembanding": str(r.satuan_pembanding) if ada_p else "rasio",
            "selisih": None, "selisih_absolut": None, "selisih_persen": None,
            "kategori_selisih": "definisi",
            "penjelasan": "definisi berbeda: jenjang berbeda (PT BPS 2020-2025 vs SD+menengah WDI 1970-2018), skala x100 vs x1, dan 0 tahun beririsan",
            "_berkas_raw_utama": str(r.berkas_raw_utama) if ada_u else "—",
            "_berkas_raw_pembanding": str(r.berkas_raw_pembanding) if ada_p else "—",
        })

    # P3: var2595 (paritas kuintil SMA) -> tanpa pembanding di paket WDI
    u3 = (
        nas[nas["seri_kode"] == "var2595"][["periode", "nilai", "satuan", "_berkas_raw"]]
        .rename(columns={"_berkas_raw": "berkas_raw"})
        .sort_values("periode")
    )
    for r in u3.itertuples(index=False):
        semua.append({
            "id_pasangan": "P3", "periode": str(r.periode), "seri_utama": "var2595",
            "rincian_utama": "total", "seri_pembanding": "tidak_ada",
            "nilai_utama": float(r.nilai), "satuan_utama": str(r.satuan),
            "nilai_pembanding": None, "satuan_pembanding": "—",
            "selisih": None, "selisih_absolut": None, "selisih_persen": None,
            "kategori_selisih": "definisi",
            "penjelasan": "definisi berbeda: paritas kuintil pengeluaran jenjang SMA, tidak ada seri pembanding kuintil di paket WDI",
            "_berkas_raw_utama": str(r.berkas_raw), "_berkas_raw_pembanding": "—",
        })

    df_rek = pd.DataFrame(semua)[KOLOM_REKONSILIASI].sort_values(["id_pasangan", "periode"]).reset_index(drop=True)
    dup = int(df_rek.duplicated(["id_pasangan", "periode"]).sum())
    if dup > 0:
        raise ValueError(f"Kunci rekonsiliasi kembar: {dup} baris")
    return df_rek


def _tulis_laporan(df_rek):
    p1_berpasangan = df_rek[(df_rek["id_pasangan"] == "P1") & (df_rek["selisih"].notna())].copy()
    med_abs = round(float(p1_berpasangan["selisih_absolut"].median()), 2)
    med_signed = round(float(p1_berpasangan["selisih"].median()), 2)
    tbl_p1 = p1_berpasangan[["periode", "nilai_utama", "nilai_pembanding", "selisih", "selisih_absolut", "kategori_selisih"]].copy()
    tbl_p1["nilai_pembanding"] = tbl_p1["nilai_pembanding"].round(2)

    md = [
        "# Hasil Rekonsiliasi Seri Utama vs Pembanding Nasional (Kartu #24)",
        "",
        "Dihasilkan otomatis oleh `src/gold/rekonsiliasi.py` ke `data/gold/rekonsiliasi.parquet` "
        f"(**{len(df_rek)} baris**, termasuk seluruh periode tanpa pasangan; selisih tidak dihapus).",
        "",
        "## 1. Pasangan Aktif P1: `var1980 [jenjang=sd]` vs `SE.PRM.CMPT.ZS` (2015-2023)",
        "",
        f"- Jumlah tahun beririsan: **{len(p1_berpasangan)} tahun** (2015-2023); periode WDI tanpa pasangan: 38 tahun (1972-2014).",
        f"- Median selisih absolut: **{med_abs} poin persen** (signed median: `{med_signed}` poin persen; WDI selalu lebih tinggi).",
        "- **Kategori penjelasan:** `definisi` (*definisi berbeda* — Susenas kohort umur 13-15 tahun dalam `persen` 0-100% vs *gross intake ratio* administratif UIS dalam `persen_apk` yang dapat >100%).",
        "",
        _df_ke_md(tbl_p1),
        "",
        "## 2. Pasangan Konteks P2 & P3 (Dilaporkan sebagai Definisi Berbeda)",
        "",
        "- **P2 (`var2600` vs `SE.ENR.PRSC.FM.ZS`, 48 baris):** 0 tahun beririsan (BPS PT 2020-2025 vs WDI SD+menengah 1970-2018), jenjang dan skala berbeda -> kategori `definisi`.",
        "- **P3 (`var2595`, 6 baris):** paritas kuintil SMA tanpa seri pembanding kuintil di paket WDI -> kategori `definisi`.",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    return med_abs


def jalankan():
    df_rek = bangun_rekonsiliasi()
    OUT_PQ.parent.mkdir(parents=True, exist_ok=True)
    df_rek.to_parquet(OUT_PQ, index=False)
    med_abs = _tulis_laporan(df_rek)
    print(f"rekonsiliasi: {len(df_rek)} baris tersimpan ({OUT_PQ.name}), pasangan_rekonsiliasi=1, selisih_median={med_abs}")
    return df_rek


if __name__ == "__main__":
    jalankan()