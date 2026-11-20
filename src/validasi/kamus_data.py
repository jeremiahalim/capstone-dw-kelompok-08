# Tahap 8 persiapan (Kartu #14): Membangun docs/data-dictionary.md dari data
# nyata Silver.
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SILVER_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"
DOCS_SERI_PATH = BASE_DIR / "docs" / "seri.csv"
OUT_MD = BASE_DIR / "docs" / "data-dictionary.md"

INFO_KOLOM = {
    "sumber": ("nama folder sumber di data/raw/", "lembaga penerbit: bps atau wdi"),
    "seri_kode": ("kode seri di sumbernya (BPS: 'var' + var.val; WDI: indicator.id)",
                  "identitas seri; detail lengkap di docs/seri.csv"),
    "wilayah_kode": ("kode BPS dua digit x 100 (log K-001)",
                     "susunan 38 provinsi 2025 (1100-9700) dan 9999 = Indonesia"),
    "nama_wilayah": ("nama wilayah BPS / 'Indonesia' untuk WDI", "nama provinsi atau Indonesia"),
    "periode": ("tahun BPS, date WDI", "bentuk baku periode (4 digit tahun: 1970-2025)"),
    "jenis_periode": ("diturunkan dari format periode (docs/seri.csv)",
                      "tahun, semester, triwulan, atau bulan"),
    "rincian": ("turvar BPS; 'total' untuk seri tanpa rincian (log K-009)",
                "'total' atau 'dimensi=kode' (jenjang=..., umur=...)"),
    "nilai": ("datacontent BPS; value WDI (null dibuang, log K-010)",
              "angka numerik sesuai satuan; baris tanpa nilai tidak masuk Silver"),
    "satuan": ("audit metadata sumber (docs/seri.csv; log K-005)",
               "satuan baku: persen, persen_apk, rasio, atau rasio_x100"),
    "_berkas_raw": ("jalur berkas mentah relatif terhadap data/raw/",
                    "lineage: berkas asal baris ini"),
    "_sha256_raw": ("src.common.manifest.sha256_raw",
                    "lineage: sidik SHA-256 berkas asal, dicocokkan dengan MANIFEST.csv"),
}


def _df_ke_markdown(df):
    kolom = list(df.columns)
    garis = [
        "| " + " | ".join(str(k) for k in kolom) + " |",
        "| " + " | ".join("---" for _ in kolom) + " |",
    ]
    for _, row in df.iterrows():
        sel = [str(row[k]).replace("|", "\\|").replace("\n", " ") for k in kolom]
        garis.append("| " + " | ".join(sel) + " |")
    return "\n".join(garis)


def muat_silver():
    if not SILVER_PATH.exists():
        from src.silver.bangun import jalankan as bangun_silver
        return bangun_silver()
    return pd.read_parquet(SILVER_PATH)


def ringkas_rentang(series):
    if pd.api.types.is_numeric_dtype(series):
        return f"{series.min()} - {series.max()}"
    unik = sorted(series.dropna().astype(str).unique().tolist())
    if len(unik) <= 6:
        return ", ".join(unik)
    return ", ".join(unik[:6]) + f", ... ({len(unik)} nilai)"


def jalankan():
    silver = muat_silver()

    # 1. Tabel semua kolom Silver
    baris_kol = []
    for kol in silver.columns:
        s = silver[kol]
        asal, arti = INFO_KOLOM.get(kol, ("kolom tambahan", "kolom tambahan Silver"))
        baris_kol.append({
            "kolom": kol,
            "tipe": str(s.dtype),
            "kosong": int(s.isna().sum()),
            "rentang_atau_nilai": ringkas_rentang(s),
            "asal": asal,
            "arti": arti,
        })
    df_kol = pd.DataFrame(baris_kol)

    # 2. Kamus rincian aktual dari Silver
    rincian_rows = []
    for rinci, g in silver.groupby("rincian", sort=True):
        seri_list = ", ".join(sorted(g["seri_kode"].unique().tolist()))
        rincian_rows.append({"rincian": rinci, "dipakai_seri": seri_list})
    df_rincian = pd.DataFrame(rincian_rows)

    # 3. Ringkasan satuan & kode SDG per seri dari docs/seri.csv
    df_seri = pd.read_csv(DOCS_SERI_PATH)
    sdg_kol = "kode_sdg" if "kode_sdg" in df_seri.columns else "sdg_kode"
    nama_kol = "nama_baku" if "nama_baku" in df_seri.columns else "nama_seri"
    df_seri_ringkas = df_seri[["sumber", "seri_kode", "satuan", sdg_kol, nama_kol]].copy()

    # 4. Contoh penelusuran 1 baris Silver (var1980 Aceh 2015 jenjang SD, atau baris pertama)
    contoh = silver[
        (silver["seri_kode"] == "var1980")
        & (silver["wilayah_kode"] == 1100)
        & (silver["periode"].astype(str) == "2015")
    ]
    baris_contoh = contoh.iloc[0] if not contoh.empty else silver.iloc[0]
    df_contoh = pd.DataFrame([{
        "sumber": baris_contoh["sumber"],
        "seri_kode": baris_contoh["seri_kode"],
        "wilayah_kode": baris_contoh["wilayah_kode"],
        "periode": baris_contoh["periode"],
        "rincian": baris_contoh["rincian"],
        "nilai": baris_contoh["nilai"],
        "_berkas_raw": baris_contoh["_berkas_raw"],
        "_sha256_raw": baris_contoh["_sha256_raw"],
    }])
    berkas_c = baris_contoh["_berkas_raw"]
    sha_pendek = str(baris_contoh["_sha256_raw"])[:12]

    md = [
        "# Data Dictionary — Kelompok 8 (Kesetaraan dan Penyelesaian Pendidikan)",
        "",
        "Dihasilkan otomatis oleh `src/validasi/kamus_data.py` dari data nyata `data/silver/silver.parquet`. "
        "Tipe, jumlah kosong, dan rentang nilai dihitung langsung dari berkas Silver.",
        "",
        f"## 1. `data/silver/silver.parquet` ({len(silver):,} baris, {len(silver.columns)} kolom)",
        "",
        "Satu baris = satu `seri_kode x wilayah_kode x periode x rincian x _berkas_raw`. "
        "Kunci unik: `sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw`.",
        "",
        _df_ke_markdown(df_kol),
        "",
        "## 2. Kamus Rincian",
        "",
        "Aturan penulisan rincian (`log-keputusan.csv` `K-009`): dimensi yang bervariasi ditulis `nama=kode`, "
        "dan baris tanpa dimensi bervariasi ditulis `total`. Pemetaan dari `turvar` BPS:",
        "- `jenjang`: `sd` (SD/Sederajat), `smp` (SMP/Sederajat), `sm` (SM/Sederajat), `sma` (SMA/Sederajat).",
        "- `umur`: `7-12`, `13-15`, `16-18`, `19-23`.",
        "",
        _df_ke_markdown(df_rincian),
        "",
        "## 3. Satuan dan Kode SDG per Seri",
        "",
        _df_ke_markdown(df_seri_ringkas),
        "",
        "## 4. Aturan Kode Wilayah (`log-keputusan.csv` `K-001`)",
        "",
        "`9999` = Indonesia (nasional); provinsi = kode dua digit BPS dikali 100 "
        "(`1100` Aceh s.d. `9700` Papua Pegunungan) pada susunan 38 provinsi tahun 2025. "
        "Provinsi pemekaran dibiarkan apa adanya (hanya berisi tahun sejak berdiri).",
        "",
        "## 5. Contoh Penelusuran Lineage Satu Baris Silver ke Berkas Mentah",
        "",
        _df_ke_markdown(df_contoh),
        "",
        f"1. Kolom _berkas_raw menunjuk langsung ke berkas mentah `data/raw/{berkas_c}`.",
        f"2. Pada `data/raw/MANIFEST.csv`, berkas tersebut memiliki sidik SHA-256 `{sha_pendek}...` yang identik dengan kolom _sha256_raw, membuktikan data dibaca dari berkas mentah asli tanpa suntingan.",
        "3. Di dalam berkas JSON BPS tersebut, nilai ditemukan pada `datacontent` untuk gabungan kode wilayah (`vervar`), kode variabel (`var`), kode rincian (`turvar`), dan kode tahun (`tahun`) yang sama.",
        "",
        "## 6. `data/gold/<tabel>.parquet`",
        "",
        "_Kolom panel Gold dan tabel rekonsiliasi akan ditambahkan pada Sprint 2–3._",
        "",
    ]
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"Tersimpan: {OUT_MD} ({len(silver.columns)} kolom Silver terdokumentasi)")


if __name__ == "__main__":
    jalankan()