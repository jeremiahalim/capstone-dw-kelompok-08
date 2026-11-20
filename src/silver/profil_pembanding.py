# Tahap 2 (Kartu #6): Profil seri pembanding nasional WDI.
import json
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.common.manifest import RAW
from src.ekstraksi.bps import baca_json
from src.ekstraksi.wdi import baca_berkas

TARGET_WDI = {
    "SE.ENR.PRSC.FM.ZS": {
        "rincian": "rasio_perempuan_laki_laki; jenjang=primer_sekunder (gross); wilayah nasional",
        "satuan": "rasio",
    },
    "SE.PRM.CMPT.ZS": {
        "rincian": "total; jenjang=sd_primer (gross_intake_last_grade); wilayah nasional",
        "satuan": "persen_apk",
    },
}


def _df_ke_markdown(df):
    # Konversi DataFrame ke tabel Markdown tanpa dependensi tabulate.
    kolom = list(df.columns)
    garis = [
        "| " + " | ".join(str(k) for k in kolom) + " |",
        "| " + " | ".join("---" for _ in kolom) + " |",
    ]
    for _, row in df.iterrows():
        sel = [str(row[k]).replace("|", "\\|").replace("\n", " ") for k in kolom]
        garis.append("| " + " | ".join(sel) + " |")
    return "\n".join(garis)


def muat_data_wdi():
    berkas = sorted((RAW / "wdi").rglob("data/*.json"))
    if not berkas:
        raise FileNotFoundError("Berkas data JSON WDI tidak ditemukan di data/raw/wdi/*/data/")
    df = pd.concat([baca_berkas(p, RAW) for p in berkas], ignore_index=True)
    df = df[df["indicator.id"].isin(TARGET_WDI)].copy()
    df["tahun"] = pd.to_numeric(df["date"], errors="coerce").astype("Int64")
    df["nilai"] = pd.to_numeric(df["value"], errors="coerce")
    return df.sort_values(["indicator.id", "tahun"]).reset_index(drop=True)


def muat_metadata_wdi():
    meta = {}
    meta_dir = sorted((RAW / "wdi").glob("*/metadata"))
    if not meta_dir:
        return meta
    for path in sorted(meta_dir[0].glob("*_indikator.json")):
        with open(path, encoding="utf-8") as f:
            isi = json.load(f)
        daftar = isi[1] if isinstance(isi, list) and len(isi) > 1 else []
        for item in daftar:
            kode = item.get("id")
            if kode in TARGET_WDI:
                prev = meta.get(kode, {})
                note_baru = (item.get("sourceNote") or "").strip()
                meta[kode] = {
                    "name": (item.get("name") or prev.get("name") or "").strip(),
                    "sourceNote": prev.get("sourceNote") or note_baru,
                    "sourceOrganization": prev.get("sourceOrganization")
                    or (item.get("sourceOrganization") or "").strip(),
                    "sumber_berkas": prev.get("sumber_berkas") or path.name,
                }
    return meta


def muat_ringkasan_bps():
    berkas = sorted((RAW / "bps").glob("*/json/*.json"))
    if not berkas:
        raise FileNotFoundError("Berkas JSON BPS tidak ditemukan di data/raw/bps/*/json/")
    info_bps = {}
    for p in berkas:
        with open(p, encoding="utf-8-sig") as f:
            raw_json = json.load(f)
        blok = raw_json[0] if isinstance(raw_json, list) else raw_json
        var_info = blok["var"][0]
        seri = f"var{var_info['val']}"
        df = baca_json(p)
        df["tahun_int"] = pd.to_numeric(df["tahun"], errors="coerce").astype("Int64")
        df["nilai_num"] = pd.to_numeric(df["nilai"], errors="coerce")
        df_valid = df.dropna(subset=["nilai_num", "tahun_int"]).copy()
        wid_str = df_valid["wilayah_id"].astype(str).str.strip()
        df_indo = df_valid[wid_str.isin(["9999", "0"])]
        info_bps[seri] = {
            "judul": (var_info.get("label") or "").strip(),
            "note": (var_info.get("note") or "").strip(),
            "rincian_unik": sorted(df_valid["turvar"].astype(str).str.strip().unique().tolist()),
            "tahun_semua": sorted(df_valid["tahun_int"].dropna().astype(int).unique().tolist()),
            "tahun_indonesia": sorted(df_indo["tahun_int"].dropna().astype(int).unique().tolist()),
            "berkas": p.name,
        }
    return info_bps


def jalankan():
    df_wdi = muat_data_wdi()
    meta_wdi = muat_metadata_wdi()
    info_bps = muat_ringkasan_bps()

    baris_ketersediaan = []
    ringkasan_seri = []

    for kode, cfg in TARGET_WDI.items():
        sub = df_wdi[df_wdi["indicator.id"] == kode].copy()
        valid = sub.dropna(subset=["nilai"]).copy()
        tahun_mentah = sorted(sub["tahun"].dropna().astype(int).unique().tolist())
        tahun_valid = sorted(valid["tahun"].dropna().astype(int).unique().tolist())
        min_valid = min(tahun_valid) if tahun_valid else None
        max_valid = max(tahun_valid) if tahun_valid else None
        tahun_bolong = (
            [t for t in range(min_valid, max_valid + 1) if t not in set(tahun_valid)]
            if min_valid is not None
            else []
        )
        nama = meta_wdi.get(kode, {}).get("name") or sub["indicator.value"].iloc[0]
        wilayah = sub["country.value"].iloc[0] if "country.value" in sub.columns else "Indonesia"

        ringkasan_seri.append(
            {
                "seri_kode": kode,
                "nama_indikator": nama,
                "wilayah": wilayah,
                "rincian": cfg["rincian"],
                "satuan": cfg["satuan"],
                "rentang_mentah_json": f"{min(tahun_mentah)}-{max(tahun_mentah)}" if tahun_mentah else "-",
                "rentang_valid": f"{min_valid}-{max_valid}" if min_valid is not None else "-",
                "total_baris_json": len(sub),
                "observasi_valid": len(valid),
                "observasi_null": int(sub["nilai"].isna().sum()),
                "tahun_bolong_dalam_rentang": ", ".join(map(str, tahun_bolong)) or "tidak ada",
                "nilai_min": round(float(valid["nilai"].min()), 4) if not valid.empty else None,
                "nilai_max": round(float(valid["nilai"].max()), 4) if not valid.empty else None,
                "tahun_valid_set": set(tahun_valid),
            }
        )

        for _, row in sub.iterrows():
            if pd.isna(row["tahun"]):
                continue
            th = int(row["tahun"])
            tersedia = pd.notna(row["nilai"])
            irisan = [
                seri_bps
                for seri_bps, detail in sorted(info_bps.items())
                if tersedia and th in set(detail["tahun_indonesia"] or detail["tahun_semua"])
            ]
            baris_ketersediaan.append(
                {
                    "seri_kode": kode,
                    "periode": th,
                    "wilayah": wilayah,
                    "rincian": cfg["rincian"],
                    "satuan": cfg["satuan"],
                    "tersedia": "ya" if tersedia else "tidak",
                    "nilai": round(float(row["nilai"]), 4) if tersedia else None,
                    "beririsan_seri_bps": "; ".join(irisan) if irisan else "-",
                    "_berkas_raw": row["_berkas_raw"] if "_berkas_raw" in row else "-",
                }
            )

    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    df_ketersediaan = pd.DataFrame(baris_ketersediaan)
    out_csv = reports_dir / "tabel_ketersediaan_wdi.csv"
    df_ketersediaan.to_csv(out_csv, index=False)

    baris_irisan = []
    for r in ringkasan_seri:
        for seri_bps, detail in sorted(info_bps.items()):
            th_bps = set(detail["tahun_indonesia"] or detail["tahun_semua"])
            irisan = sorted(r["tahun_valid_set"] & th_bps)
            baris_irisan.append(
                {
                    "Seri WDI": r["seri_kode"],
                    "Seri BPS": seri_bps,
                    "Rincian BPS": ", ".join(detail["rincian_unik"]),
                    "Periode Valid WDI": r["rentang_valid"],
                    "Periode BPS (Indonesia)": f"{min(th_bps)}-{max(th_bps)}" if th_bps else "-",
                    "Jumlah Tahun Irisan": len(irisan),
                    "Tahun Beririsan": (
                        f"{min(irisan)}-{max(irisan)} ({', '.join(map(str, irisan))})"
                        if irisan
                        else "Tidak ada irisan (0 tahun)"
                    ),
                }
            )

    df_irisan = pd.DataFrame(baris_irisan)
    note_gpi = meta_wdi.get("SE.ENR.PRSC.FM.ZS", {}).get(
        "sourceNote", "(tidak ditemukan di metadata)"
    )
    note_cmpt = meta_wdi.get("SE.PRM.CMPT.ZS", {}).get(
        "sourceNote", "(tidak ditemukan di metadata)"
    )
    note_var1980 = info_bps.get("var1980", {}).get(
        "note", "(tidak ditemukan di metadata JSON BPS)"
    )

    df_ringkas_md = pd.DataFrame(ringkasan_seri).drop(columns=["tahun_valid_set"])

    md = [
        "# Laporan Profil Seri Pembanding Nasional (WDI)",
        "",
        "## 1. Ringkasan Ketersediaan Data Valid (Non-Null)",
        "",
        "JSON World Bank mencantumkan seluruh deret tahun 1960-2025, tetapi nilai `null` berarti tidak ada pengamatan. "
        "Ringkasan berikut dihitung **hanya dari observasi valid (non-null)** yang benar-benar terbaca. "
        "Tabel lengkap seri x periode x rincian tersimpan di `reports/tabel_ketersediaan_wdi.csv`.",
        "",
        _df_ke_markdown(df_ringkas_md),
        "",
        "## 2. Irisan Tahun (Overlap) dengan Seri Utama BPS",
        "",
        _df_ke_markdown(df_irisan),
        "",
        "## 3. Evaluasi Kandidat Rincian Sebanding & Batasannya (untuk Tahap 6)",
        "",
        "### A. SE.PRM.CMPT.ZS vs `var1980` (Tingkat Penyelesaian Pendidikan BPS)",
        "",
        "- **Kandidat yang dapat dibandingkan:** `var1980` khusus rincian **SD/Sederajat (`jenjang=sd`)** pada baris nasional **Indonesia (`wilayah_kode = 9999`)**.",
        "- **Rincian yang TIDAK dapat dibandingkan:** `SMP/Sederajat` dan `SMA/Sederajat` pada `var1980` (karena `SE.PRM.CMPT.ZS` khusus jenjang pendidikan dasar/SD), serta seluruh baris tingkat provinsi (karena WDI hanya tersedia di tingkat nasional).",
        "- **Alasan & Batasan Definisi (TIDAK identik secara definisi/metode):**",
        f"  - **Definisi WDI (`SE.PRM.CMPT.ZS`, `sourceNote`):** {note_cmpt}",
        f"  - **Definisi BPS (`var1980`, `var.note`):** {note_var1980}",
        "- **Implikasi untuk Tahap 6:** Keduanya sama-sama memantau penyelesaian jenjang SD di tingkat nasional dan memiliki irisan periode (lihat tabel irisan di atas). "
        "Namun, secara metodologi keduanya **berbeda definisi dan metode**: "
        "`var1980` BPS adalah *completion rate* berbasis survei rumah tangga (Susenas) pada kohort umur 3-5 tahun di atas usia resmi kelulusan SD sehingga nilainya selalu di rentang **0-100%** (`persen`), "
        "sedangkan `SE.PRM.CMPT.ZS` WDI adalah *gross intake ratio to the last grade of primary* berbasis data administratif/estimasi populasi tanpa batas usia sehingga nilainya **dapat melebihi 100%** (`persen_apk`). "
        "Oleh karena itu, pada rekonsiliasi Tahap 6 keduanya tetap disandingkan sebagai pasangan utama, tetapi selisih yang muncul tidak dihapus dan dikategorikan sebagai **definisi berbeda** dan/atau **metode berbeda**.",
        "",
        "### B. SE.ENR.PRSC.FM.ZS vs Seri 4.5.1 dan Partisipasi BPS",
        "",
        f"- **Definisi WDI (`SE.ENR.PRSC.FM.ZS`, `sourceNote`):** {note_gpi}",
        "- **Kandidat yang dapat dibandingkan:** **Tidak ada rincian seri utama BPS yang sebanding langsung.**",
        "- **Batasan terhadap masing-masing seri BPS:**",
        "  - **`var2595` (Paritas Kuintil APK SMA, 2020-2025):** Tidak sebanding karena berbeda **jenis paritas** (kuintil ekonomi terendah/tertinggi vs jenis kelamin perempuan/laki-laki), berbeda **jenjang** (SMA saja vs gabungan Primer & Sekunder), berbeda **skala** (`rasio_x100` vs `rasio`), dan **tidak ada irisan tahun (0 tahun)** karena data valid WDI berakhir pada 2018.",
        "  - **`var2600` (Paritas Gender APK PT, 2020-2025):** Tidak sebanding karena meski sama-sama paritas gender (perempuan/laki-laki), **jenjangnya berbeda** (Perguruan Tinggi vs gabungan Primer & Sekunder), berbeda **skala** (`rasio_x100` vs `rasio`), dan **tidak ada irisan tahun (0 tahun)**.",
        "  - **`var304` (APM, 2003-2025) & `var2211` (APS, 2015-2025):** Meski memiliki irisan tahun dengan WDI, keduanya mengukur persentase partisipasi total per jenjang/kelompok umur tanpa rincian jenis kelamin (bukan rasio paritas gender APK).",
        "- **Implikasi untuk Tahap 6:** Pasangan seri paritas BPS (`var2595`/`var2600`) terhadap `SE.ENR.PRSC.FM.ZS` harus dilaporkan secara eksplisit sebagai **definisi berbeda** disertai catatan keterbatasan **tidak adanya irisan periode**.",
        "",
    ]

    out_md = reports_dir / "profil_seri_pembanding.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"Tersimpan: {out_csv} ({len(df_ketersediaan)} baris)")
    print(f"Tersimpan: {out_md}")


if __name__ == "__main__":
    jalankan()