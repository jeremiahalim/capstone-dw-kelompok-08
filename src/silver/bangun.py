from pathlib import Path
import pandas as pd

from src.common.manifest import RAW
from src.common.skema import KOLOM, KUNCI, periksa_silver
from src.ekstraksi.bps import baca_json
from src.ekstraksi.wdi import baca_berkas

BASE_DIR = Path(__file__).resolve().parents[2]
DOCS_SERI_PATH = BASE_DIR / "docs" / "seri.csv"
SILVER_OUT_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"

# Peta pembakuan rincian BPS (sesuai K-006)
PETA_RINCIAN = {
    "sd/sederajat": "jenjang=sd",
    "sd / sederajat": "jenjang=sd",
    "smp/sederajat": "jenjang=smp",
    "smp / sederajat": "jenjang=smp",
    "sm/sederajat": "jenjang=sm",
    "sm / sederajat": "jenjang=sm",
    "sma/sederajat": "jenjang=sma",
    "sma / sederajat": "jenjang=sma",
    "7-12": "umur=7-12",
    "13-15": "umur=13-15",
    "16-18": "umur=16-18",
    "19-23": "umur=19-23",
    "": "total",
    "tidak ada": "total",
}

def _muat_peta_seri():
    """Membaca satuan dan jenis_periode dari docs/seri.csv hasil tugas #9."""
    if not DOCS_SERI_PATH.exists():
        from src.silver.metadata import jalankan as jalankan_meta
        jalankan_meta()

    df_seri = pd.read_csv(DOCS_SERI_PATH)
    peta = {}
    for _, row in df_seri.iterrows():
        # Standarisasi 'tahunan' -> 'tahun' agar lolos src/common/skema.py
        jp = str(row["jenis_periode"]).strip().lower()
        if jp == "tahunan":
            jp = "tahun"
        peta[str(row["seri_kode"]).strip()] = {
            "satuan": str(row["satuan"]).strip(),
            "jenis_periode": jp,
        }
    return peta


def _proses_bps(peta_seri):
    """Membaca seluruh JSON WebAPI BPS dan membakukan ke skema Silver."""
    berkas_json = sorted(RAW.glob("bps/*/json/*.json"))
    if not berkas_json:
        raise FileNotFoundError("Tidak ditemukan berkas JSON BPS di data/raw/bps/*/json/")

    df_bps = pd.concat([baca_json(p) for p in berkas_json], ignore_index=True)

    # Standarisasi seri_kode dan wilayah_kode (sesuai K-001)
    df_bps["sumber"] = "bps"
    df_bps["seri_kode"] = "var" + df_bps["var_id"].astype(str).str.strip()

    def konversi_wilayah(wid):
        wid_int = int(str(wid).strip())
        if wid_int == 9999 or wid_int == 0:
            return 9999
        return wid_int * 100 if wid_int < 100 else wid_int

    df_bps["wilayah_kode"] = df_bps["wilayah_id"].apply(konversi_wilayah).astype("int64")
    df_bps["nama_wilayah"] = df_bps["wilayah"].astype(str).str.strip()
    df_bps["periode"] = df_bps["tahun"].astype(str).str.strip()

    # Rincian disimpan ringkas sesuai K-006, atau teks asli jika tidak ada di peta
    df_bps["rincian"] = (
        df_bps["turvar"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(lambda x: PETA_RINCIAN.get(x, x))
    )

    # Konversi nilai numerik dan buang observasi yang kosong/missing (sesuai K-005)
    df_bps["nilai"] = pd.to_numeric(df_bps["nilai"], errors="coerce")
    df_bps = df_bps.dropna(subset=["nilai"]).copy()

    # Terapkan satuan & jenis_periode dari metadata (#9)
    df_bps["satuan"] = df_bps["seri_kode"].map(lambda k: peta_seri[k]["satuan"])
    df_bps["jenis_periode"] = df_bps["seri_kode"].map(lambda k: peta_seri[k]["jenis_periode"])

    return df_bps[KOLOM]


def _proses_wdi(peta_seri):
    """Membaca berkas data WDI (mengabaikan folder metadata) dan membakukan ke skema Silver."""
    berkas_data_wdi = sorted((RAW / "wdi").rglob("data/*.json"))
    if not berkas_data_wdi:
        raise FileNotFoundError("Tidak ditemukan JSON data WDI di data/raw/wdi/*/data/")

    df_wdi = pd.concat([baca_berkas(p, RAW) for p in berkas_data_wdi], ignore_index=True)

    df_wdi["sumber"] = "wdi"
    df_wdi["seri_kode"] = df_wdi["indicator.id"].astype(str).str.strip()
    df_wdi["wilayah_kode"] = 9999
    df_wdi["nama_wilayah"] = "Indonesia"
    df_wdi["periode"] = df_wdi["date"].astype(str).str.strip()
    df_wdi["rincian"] = "total"

    # Buang baris WDI dengan value null (sesuai K-010)
    df_wdi["nilai"] = pd.to_numeric(df_wdi["value"], errors="coerce")
    df_wdi = df_wdi.dropna(subset=["nilai"]).copy()

    # Terapkan satuan & jenis_periode dari metadata (#9)
    df_wdi["satuan"] = df_wdi["seri_kode"].map(lambda k: peta_seri[k]["satuan"])
    df_wdi["jenis_periode"] = df_wdi["seri_kode"].map(lambda k: peta_seri[k]["jenis_periode"])

    return df_wdi[KOLOM]


def jalankan():
    peta_seri = _muat_peta_seri()

    df_bps = _proses_bps(peta_seri)
    df_wdi = _proses_wdi(peta_seri)

    df_silver = pd.concat([df_bps, df_wdi], ignore_index=True)

    # Pastikan tipe data sesuai aturan skema.py dan kunci primer unik
    df_silver["wilayah_kode"] = df_silver["wilayah_kode"].astype("int64")
    df_silver["nilai"] = df_silver["nilai"].astype("float64")
    for kol in ["sumber", "seri_kode", "nama_wilayah", "periode", "jenis_periode", "rincian", "satuan", "_berkas_raw", "_sha256_raw"]:
        df_silver[kol] = df_silver[kol].astype(str).str.strip()

    df_silver = df_silver.drop_duplicates(subset=KUNCI, keep="last").reset_index(drop=True)

    # Validasi otomatis sebelum simpan
    pelanggaran = periksa_silver(df_silver)
    if pelanggaran:
        raise ValueError(f"Tabel Silver gagal validasi skema: {pelanggaran}")

    SILVER_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_silver.to_parquet(SILVER_OUT_PATH, index=False)

    print(
        f"Berhasil membangun {SILVER_OUT_PATH}: "
        f"{len(df_silver):,} baris, {df_silver['seri_kode'].nunique()} seri, "
        f"{df_silver['rincian'].nunique()} rincian unik."
    )
    return df_silver


if __name__ == "__main__":
    jalankan()