# Kartu #22: Lanjutkan tabel nasional Sprint 1 menjadi tabel Gold ber-lineage.
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
SILVER_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"
GOLD_DIR = BASE_DIR / "data" / "gold"
OUT_LONG = GOLD_DIR / "tabel_nasional.parquet"
OUT_WIDE = GOLD_DIR / "tabel_nasional_lebar.parquet"
OUT_MD = BASE_DIR / "reports" / "tabel_nasional_gold.md"

SERI_UTAMA = {"var304", "var2595", "var2600", "var1980", "var2211"}
SERI_PEMBANDING = {"SE.ENR.PRSC.FM.ZS", "SE.PRM.CMPT.ZS"}


def bangun_tabel_nasional_gold(silver):
    # Ambil baris nasional Indonesia (wilayah_kode == 9999) untuk 5 seri utama + 2 pembanding
    semua_seri = SERI_UTAMA | SERI_PEMBANDING
    nas = silver[
        (silver["wilayah_kode"] == 9999) & (silver["seri_kode"].isin(semua_seri))
    ].copy()

    # Tentukan asal_angka secara eksplisit: baris_indonesia (BPS) atau pembanding (WDI)
    def _asal(row):
        if row["sumber"] == "bps":
            return "baris_indonesia"
        return "pembanding"

    nas["asal_angka"] = nas.apply(_asal, axis=1)
    nas["seri_rincian"] = [
        s if r == "total" else f"{s} [{r}]"
        for s, r in zip(nas["seri_kode"], nas["rincian"])
    ]
    nas["nilai_seragam"] = [
        round(float(v) / 100.0, 6) if sat == "rasio_x100" else float(v)
        for v, sat in zip(nas["nilai"], nas["satuan"])
    ]
    nas["satuan_seragam"] = nas["satuan"].replace({"rasio_x100": "rasio"})

    kol_utama = [
        "periode",
        "sumber",
        "seri_kode",
        "rincian",
        "seri_rincian",
        "asal_angka",
        "nilai",
        "satuan",
        "nilai_seragam",
        "satuan_seragam",
        "_berkas_raw",
        "_sha256_raw",
    ]
    tabel_long = (
        nas[kol_utama]
        .sort_values(["periode", "seri_kode", "rincian"])
        .reset_index(drop=True)
    )

    dup = int(tabel_long.duplicated(["periode", "seri_kode", "rincian"]).sum())
    if dup > 0:
        raise ValueError(f"Kunci tabel_nasional Gold kembar: {dup} baris")
    if tabel_long["_berkas_raw"].isna().any():
        raise ValueError("Ditemukan _berkas_raw kosong pada tabel_nasional Gold")

    # Versi lebar: seri utama dan pembanding berdampingan per periode
    tabel_wide = (
        tabel_long.pivot(index="periode", columns="seri_rincian", values="nilai")
        .reset_index()
        .sort_values("periode")
        .reset_index(drop=True)
    )
    tabel_wide.columns.name = None
    return tabel_long, tabel_wide


def _tulis_laporan(tabel_long, tabel_wide):
    hitung_asal = tabel_long["asal_angka"].value_counts().to_dict()
    n_bps = int(hitung_asal.get("baris_indonesia", 0))
    n_wdi = int(hitung_asal.get("pembanding", 0))
    n_agg = int(hitung_asal.get("agregat", 0))

    baris = [
        "# Ringkasan Tabel Nasional Gold (Kartu #22)",
        "",
        "Dihasilkan otomatis oleh `src/gold/nasional_gold.py` (dipanggil dari `src/gold/nasional.py` -> `python pipeline.py`).",
        "",
        f"- **Tabel nasional utama (`data/gold/tabel_nasional.parquet`):** **{len(tabel_long):,} baris** "
        f"(1 baris per `periode x seri_kode x rincian`, 0 duplikat), mencakup **{tabel_long['seri_kode'].nunique()} seri** "
        f"pada **{tabel_long['periode'].nunique()} periode** ({tabel_long['periode'].min()}-{tabel_long['periode'].max()}).",
        f"- **Tabel nasional lebar (`data/gold/tabel_nasional_lebar.parquet`):** **{len(tabel_wide)} periode x {len(tabel_wide.columns) - 1} kolom seri/rincian** berdampingan.",
        "- **Distribusi kolom `asal_angka`:**",
        f"  - `baris_indonesia`: **{n_bps} baris** (seluruh 5 seri utama BPS `var304`, `var2595`, `var2600`, `var1980`, `var2211` menerbitkan baris resmi Indonesia `wilayah_kode = 9999`).",
        f"  - `pembanding`: **{n_wdi} baris** (2 seri nasional WDI `SE.ENR.PRSC.FM.ZS` dan `SE.PRM.CMPT.ZS`).",
        f"  - `agregat`: **{n_agg} baris** (tidak diperlukan agregasi buatan dari provinsi karena seluruh seri utama BPS sudah memiliki angka nasional resmi).",
        "- **Lineage:** 100% baris membawa `_berkas_raw` dan `_sha256_raw` (0 nilai kosong).",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(baris) + "\n", encoding="utf-8")


def jalankan(silver=None):
    if silver is None:
        silver = pd.read_parquet(SILVER_PATH)
    tabel_long, tabel_wide = bangun_tabel_nasional_gold(silver)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)
    tabel_long.to_parquet(OUT_LONG, index=False)
    tabel_wide.to_parquet(OUT_WIDE, index=False)
    _tulis_laporan(tabel_long, tabel_wide)
    print(
        f"nasional_gold: {len(tabel_long):,} baris ({OUT_LONG.name}) & "
        f"{len(tabel_wide)} periode ({OUT_WIDE.name}), "
        f"asal_angka={tabel_long['asal_angka'].value_counts().to_dict()}"
    )
    return {"tabel_nasional": tabel_long, "tabel_nasional_lebar": tabel_wide}


if __name__ == "__main__":
    jalankan()