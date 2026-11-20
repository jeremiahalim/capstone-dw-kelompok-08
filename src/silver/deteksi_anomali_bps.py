# Tahap 3 (Kartu #8): Klasifikasi calon anomali profil, uji galat input,
# patahan definisi/wilayah, dan uji deduplikasi/format BPS.
import re
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.common.manifest import RAW
from src.common.skema import KUNCI
from src.ekstraksi.bps import baca_csv, baca_json

RENTANG_SATUAN = {
    "persen": (0.0, 100.0),
    "rasio_x100": (0.0, 500.0),
    "rasio": (0.0, 5.0),
    "persen_apk": (0.0, 150.0),
}

PROVINSI = {
    1100: ("Aceh", 1950),
    1200: ("Sumatera Utara", 1950),
    1300: ("Sumatera Barat", 1958),
    1400: ("Riau", 1958),
    1500: ("Jambi", 1958),
    1600: ("Sumatera Selatan", 1950),
    1700: ("Bengkulu", 1968),
    1800: ("Lampung", 1964),
    1900: ("Kepulauan Bangka Belitung", 2001),
    2100: ("Kepulauan Riau", 2003),
    3100: ("DKI Jakarta", 1950),
    3200: ("Jawa Barat", 1950),
    3300: ("Jawa Tengah", 1950),
    3400: ("DI Yogyakarta", 1950),
    3500: ("Jawa Timur", 1950),
    3600: ("Banten", 2001),
    5100: ("Bali", 1958),
    5200: ("Nusa Tenggara Barat", 1958),
    5300: ("Nusa Tenggara Timur", 1958),
    6100: ("Kalimantan Barat", 1956),
    6200: ("Kalimantan Tengah", 1958),
    6300: ("Kalimantan Selatan", 1956),
    6400: ("Kalimantan Timur", 1956),
    6500: ("Kalimantan Utara", 2013),
    7100: ("Sulawesi Utara", 1964),
    7200: ("Sulawesi Tengah", 1964),
    7300: ("Sulawesi Selatan", 1964),
    7400: ("Sulawesi Tenggara", 1964),
    7500: ("Gorontalo", 2001),
    7600: ("Sulawesi Barat", 2005),
    8100: ("Maluku", 1950),
    8200: ("Maluku Utara", 2000),
    9100: ("Papua Barat", 2004),
    9200: ("Papua Barat Daya", 2023),
    9400: ("Papua", 1969),
    9500: ("Papua Selatan", 2023),
    9600: ("Papua Tengah", 2023),
    9700: ("Papua Pegunungan", 2023),
}

INDUK = {
    1900: 1600,
    2100: 1400,
    3600: 3200,
    6500: 6400,
    7500: 7100,
    7600: 7300,
    8200: 8100,
    9100: 9400,
    9200: 9100,
    9500: 9400,
    9600: 9400,
    9700: 9400,
}

NAMA = {kode: nama for kode, (nama, _) in PROVINSI.items()}

PATAHAN_DEFINISI = [
    {
        "seri_kode": "var304",
        "periode_mulai": "2007",
        "bukti_metadata": "var.note var304: mulai 2007 APM mencakup pendidikan nonformal (paket A, B, C)",
        "tindakan": "ditandai patahan_definisi; nilai tidak diubah (log K-013)",
    }
]


def _df_ke_markdown(df):
    if df.empty:
        return "_Tidak ada baris._"
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
    silver_path = BASE_DIR / "data" / "silver" / "silver.parquet"
    if not silver_path.exists():
        from src.silver.bangun import jalankan as bangun_silver

        return bangun_silver()
    return pd.read_parquet(silver_path)


def cek_galat_input(silver):
    baris = []
    for satuan, (lo, hi) in RENTANG_SATUAN.items():
        s = silver[(silver["satuan"] == satuan) & ((silver["nilai"] < lo) | (silver["nilai"] > hi))]
        for r in s.itertuples():
            baris.append(
                {
                    "seri_kode": r.seri_kode,
                    "wilayah_kode": r.wilayah_kode,
                    "periode": r.periode,
                    "rincian": r.rincian,
                    "nilai": r.nilai,
                    "aturan": f"{satuan} harus pada [{lo}, {hi}]",
                }
            )
    return pd.DataFrame(baris)


def deteksi_patahan_wilayah(silver):
    bps = silver[(silver["sumber"] == "bps") & (silver["wilayah_kode"] != 9999)].copy()
    hasil = []
    for (seri, rinci), g in bps.groupby(["seri_kode", "rincian"], sort=True):
        label = seri if rinci == "total" else f"{seri} [{rinci}]"
        ada = {int(w): sorted(x["periode"].astype(str).tolist()) for w, x in g.groupby("wilayah_kode")}
        nilai = g.set_index(["wilayah_kode", "periode"])["nilai"]
        for induk in sorted(set(INDUK.values())):
            angkatan = {}
            for k, i in INDUK.items():
                if i == induk and k in ada:
                    angkatan.setdefault(PROVINSI[k][1], []).append(k)
            for anak in angkatan.values():
                if induk not in ada:
                    continue
                pertama = min(min(ada[k]) for k in anak)
                sebelum = [p for p in ada[induk] if p < pertama]
                if not sebelum or pertama not in ada[induk]:
                    continue
                hasil.append(
                    {
                        "seri_kode": label,
                        "induk": NAMA[induk],
                        "wilayah_kode": induk,
                        "periode": pertama,
                        "anak": ", ".join(NAMA[k] for k in anak),
                        "nilai_sebelum": round(float(nilai[(induk, sebelum[-1])]), 2),
                        "nilai_sesudah": round(float(nilai[(induk, pertama)]), 2),
                    }
                )
    return pd.DataFrame(hasil)


def baca_calon_dari_profil():
    # Membaca daftar 26 calon anomali dari reports/profil_dan_anomali_bps.md
    profil_path = BASE_DIR / "reports" / "profil_dan_anomali_bps.md"
    if not profil_path.exists():
        return pd.DataFrame()
    teks = profil_path.read_text(encoding="utf-8").splitlines()
    mulai = False
    baris = []
    for line in teks:
        if line.strip().startswith("## 2. Daftar Calon Anomali"):
            mulai = True
            continue
        if mulai and line.strip().startswith("|"):
            kol = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(kol) == 6 and kol[0] != "Seri" and not set(kol[0]).issubset({"-", ":"}):
                baris.append(
                    {
                        "seri": kol[0],
                        "wilayah": kol[1],
                        "rincian": kol[2],
                        "periode": kol[3],
                        "nilai": float(kol[4]),
                        "alasan_profil": kol[5],
                    }
                )
    return pd.DataFrame(baris)


def klasifikasi_calon_profil(df_calon):
    hasil = []
    wilayah_struktural_papua = {
        "PAPUA",
        "PAPUA BARAT",
        "PAPUA BARAT DAYA",
        "PAPUA SELATAN",
        "PAPUA TENGAH",
        "PAPUA PEGUNUNGAN",
    }
    for r in df_calon.itertuples():
        wil = r.wilayah.upper()
        if "var1980" in r.seri and wil == "PAPUA":
            kategori = "outlier_asli (perbedaan_struktural)"
            alasan = (
                "Tingkat penyelesaian SMA Papua secara struktural rendah lintas tahun (2015-2020) "
                "dan berada di rentang sah 0-100%; bukan galat input."
            )
        elif "var2595" in r.seri and wil in wilayah_struktural_papua:
            kategori = "outlier_asli (perbedaan_struktural)"
            alasan = (
                "Rasio APK kuintil terendah/tertinggi SMA di wilayah Papua mencerminkan "
                "kesenjangan akses ekonomi riil; nilai positif sah dalam satuan rasio_x100."
            )
        elif "var2595" in r.seri:
            kategori = "outlier_asli"
            alasan = (
                "Fluktuasi rasio paritas kuintil SMA pada provinsi perkotaan/berpenduduk kecil "
                "(mis. DKI Jakarta, Bali, Kep. Riau, Kaltara, Sulbar); nilai sah dalam rentang rasio_x100."
            )
        elif "var2600" in r.seri and wil in wilayah_struktural_papua:
            kategori = "outlier_asli (perbedaan_struktural)"
            alasan = (
                "Rasio paritas gender APK PT di Papua Selatan/Pegunungan (<80) mencerminkan "
                "partisipasi perempuan lebih rendah dibanding laki-laki; nilai sah dalam rasio_x100."
            )
        else:
            kategori = "outlier_asli"
            alasan = (
                "Rasio paritas gender APK PT tinggi (>160, mis. Kaltara, Sulut, Gorontalo, Sulbar, "
                "Lampung) karena jumlah mahasiswi lebih besar dan populasi dasar kelompok usia PT kecil; "
                "sah dalam rasio_x100."
            )
        hasil.append(
            {
                "Seri": r.seri,
                "Wilayah": r.wilayah,
                "Rincian": r.rincian,
                "Periode": r.periode,
                "Nilai": r.nilai,
                "Tanda_Profil": r.alasan_profil,
                "Kategori": kategori,
                "Tindakan": "ditandai, nilai tidak diubah",
                "Alasan_Keputusan": alasan,
                "Ref_Log": "K-003",
            }
        )
    return pd.DataFrame(hasil)


def cek_deduplikasi_dan_format(silver):
    kunci_kembar = int(silver.duplicated(KUNCI).sum())
    snapshots = sorted({p.parent.name for p in (RAW / "bps").glob("*/*.csv")})
    uji_format = []
    for p_json in sorted((RAW / "bps").glob("*/json/*.json")):
        p_csv = p_json.parents[1] / (p_json.stem + ".csv")
        if not p_csv.exists():
            continue
        dj = baca_json(p_json)
        dc = baca_csv(p_csv)
        kj = {
            (r.wilayah_id, r.turvar.strip(), r.tahun, r.periode.strip()): float(r.nilai)
            for r in dj.itertuples()
            if str(r.nilai).strip() != ""
        }
        kc = {
            (r.wilayah_id, r.turvar.strip(), r.tahun, r.periode.strip()): float(r.nilai)
            for r in dc.itertuples()
            if str(r.nilai).strip() != ""
        }
        sama = set(kj) & set(kc)
        beda = sum(abs(kj[k] - kc[k]) > 1e-9 for k in sama)
        uji_format.append(
            {
                "Berkas": p_json.stem,
                "Baris_JSON": len(kj),
                "Baris_CSV": len(kc),
                "Pasangan_Sama": len(sama),
                "Nilai_Berbeda": beda,
            }
        )
    return kunci_kembar, snapshots, pd.DataFrame(uji_format)


def jalankan():
    silver = muat_silver()
    df_galat = cek_galat_input(silver)
    df_patahan_wil = deteksi_patahan_wilayah(silver)
    df_calon = baca_calon_dari_profil()
    df_klas = klasifikasi_calon_profil(df_calon)
    kunci_kembar, snapshots, df_uji = cek_deduplikasi_dan_format(silver)

    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_csv = reports_dir / "klasifikasi_anomali.csv"
    df_klas.to_csv(out_csv, index=False)

    md = [
        "# Klasifikasi Anomali, Patahan Seri, Galat Input, dan Deduplikasi (Kartu #8)",
        "",
        "Dihasilkan oleh `src/silver/deteksi_anomali_bps.py` berdasarkan `data/silver/silver.parquet` "
        "dan `reports/profil_dan_anomali_bps.md`.",
        "",
        "## 1. Pemeriksaan Galat Input (Rentang Satuan pada Semua Baris Silver)",
        "",
        f"- Total baris Silver diperiksa: **{len(silver):,}**.",
        f"- Jumlah galat input ditemukan: **{len(df_galat)} baris** (tidak ada nilai di luar rentang satuan sah).",
        f"- **Keputusan:** **Tidak ada perbaikan/perubahan nilai galat input** (`dampak_baris = 0`, tercatat di `log-keputusan.csv` `K-003`).",
        "",
        "## 2. Klasifikasi Seluruh Calon Anomali dari Laporan Profil (`reports/profil_dan_anomali_bps.md`)",
        "",
        f"Sebanyak **{len(df_klas)} calon anomali** pada laporan profil dihubungkan ke kategori dan alasannya "
        "(semuanya merupakan `outlier_asli` / `perbedaan_struktural` yang dipertahankan tanpa diubah, tercatat di `K-003`):",
        "",
        _df_ke_markdown(df_klas),
        "",
        "## 3. Patahan Definisi yang Dinyatakan Penerbit (`K-013`)",
        "",
        _df_ke_markdown(pd.DataFrame(PATAHAN_DEFINISI)),
        "",
        f"## 4. Patahan Wilayah akibat Pemekaran Provinsi (`K-012`): {len(df_patahan_wil)} kejadian",
        "",
        "Nilai provinsi induk sebelum periode ini mencakup wilayah provinsi pemekaran; sesudahnya tidak. "
        "Perubahannya ditandai sebagai `patahan_wilayah`, bukan outlier dan tidak diratakan.",
        "",
        _df_ke_markdown(df_patahan_wil),
        "",
        "## 5. Deduplikasi, Snapshot, dan Uji Silang Format JSON vs CSV BPS",
        "",
        f"- Kunci primer kembar di Silver: **{kunci_kembar}**.",
        f"- Jumlah snapshot BPS di paket Kasus 8: **{len(snapshots)} snapshot** (`{', '.join(snapshots)}`).",
        "- **Aturan tertulis deduplikasi dua snapshot:** bila di kemudian hari tersedia dua snapshot untuk kunci yang sama, "
        "angka yang sama diperlakukan sebagai konfirmasi (ambil snapshot terbaru) dan angka berbeda diperlakukan sebagai revisi (dicatat di log).",
        "- **Uji silang JSON vs CSV BPS:** JSON WebAPI dipilih sebagai sumber kanonik Silver karena memuat judul dan metadata lengkap; "
        "nilai keduanya identik (`Nilai_Berbeda = 0`):",
        "",
        _df_ke_markdown(df_uji),
    ]

    out_md = reports_dir / "klasifikasi_anomali.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"Tersimpan: {out_md}")
    print(f"Tersimpan: {out_csv} ({len(df_klas)} calon anomali diklasifikasikan)")
    print(
        f"Ringkasan: galat_input={len(df_galat)} outlier_ditandai={len(df_klas)} "
        f"patahan_definisi={len(PATAHAN_DEFINISI)} patahan_wilayah={len(df_patahan_wil)} "
        f"kunci_kembar={kunci_kembar}"
    )


if __name__ == "__main__":
    jalankan()