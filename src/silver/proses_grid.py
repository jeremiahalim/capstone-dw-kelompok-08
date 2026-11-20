# Tahap 3 (Kartu #7): Grid 38 provinsi x periode, kelengkapan panel, dan
# kategori sel kosong.
import json
import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.common.manifest import RAW

INDONESIA = 9999

# Susunan 38 provinsi 2025: kode -> (nama baku, tahun pertama data setahun penuh)
PROVINSI = {
    1100: ("Aceh", 1950), 1200: ("Sumatera Utara", 1950), 1300: ("Sumatera Barat", 1958),
    1400: ("Riau", 1958), 1500: ("Jambi", 1958), 1600: ("Sumatera Selatan", 1950),
    1700: ("Bengkulu", 1968), 1800: ("Lampung", 1964), 1900: ("Kepulauan Bangka Belitung", 2001),
    2100: ("Kepulauan Riau", 2003), 3100: ("DKI Jakarta", 1950), 3200: ("Jawa Barat", 1950),
    3300: ("Jawa Tengah", 1950), 3400: ("DI Yogyakarta", 1950), 3500: ("Jawa Timur", 1950),
    3600: ("Banten", 2001), 5100: ("Bali", 1958), 5200: ("Nusa Tenggara Barat", 1958),
    5300: ("Nusa Tenggara Timur", 1958), 6100: ("Kalimantan Barat", 1956),
    6200: ("Kalimantan Tengah", 1958),
    6300: ("Kalimantan Selatan", 1956), 6400: ("Kalimantan Timur", 1956),
    6500: ("Kalimantan Utara", 2013),
    7100: ("Sulawesi Utara", 1964), 7200: ("Sulawesi Tengah", 1964), 7300: ("Sulawesi Selatan", 1964),
    7400: ("Sulawesi Tenggara", 1964), 7500: ("Gorontalo", 2001), 7600: ("Sulawesi Barat", 2005),
    8100: ("Maluku", 1950), 8200: ("Maluku Utara", 2000), 9100: ("Papua Barat", 2004),
    9200: ("Papua Barat Daya", 2023), 9400: ("Papua", 1969), 9500: ("Papua Selatan", 2023),
    9600: ("Papua Tengah", 2023), 9700: ("Papua Pegunungan", 2023),
}

INDUK = {
    1900: 1600, 2100: 1400, 3600: 3200, 6500: 6400,
    7500: 7100, 7600: 7300, 8200: 8100, 9100: 9400,
    9200: 9100, 9500: 9400, 9600: 9400, 9700: 9400,
}

NAMA = {kode: nama for kode, (nama, _) in PROVINSI.items()} | {INDONESIA: "Indonesia"}

SERI_PROVINSI = ["var304", "var1980", "var2211", "var2595", "var2600"]


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


def sudah_ada(kode, tahun):
    if kode == INDONESIA:
        return True
    return int(str(tahun)[:4]) >= PROVINSI[kode][1]


def muat_tahun_terbit_bps():
    tahun_map = {}
    for p in sorted((RAW / "bps").glob("*/json/*.json")):
        with open(p, encoding="utf-8-sig") as f:
            isi = json.load(f)
        halaman = isi if isinstance(isi, list) else [isi]
        for blok in halaman:
            var_id = blok["var"][0]["val"]
            seri = f"var{var_id}"
            th = {str(t["label"]).strip() for t in blok.get("tahun", [])}
            tahun_map.setdefault(seri, set()).update(th)
    return {k: sorted(v) for k, v in tahun_map.items()}


def muat_silver():
    silver_path = BASE_DIR / "data" / "silver" / "silver.parquet"
    if not silver_path.exists():
        from src.silver.bangun import jalankan as bangun_silver
        return bangun_silver()
    return pd.read_parquet(silver_path)


def bentuk_grid(silver, tahun_terbit):
    bps = silver[(silver["sumber"] == "bps") & (silver["seri_kode"].isin(SERI_PROVINSI))].copy()
    baris = []
    for (seri, rinci), g in bps.groupby(["seri_kode", "rincian"], sort=True):
        label = seri if rinci == "total" else f"{seri} [{rinci}]"
        terisi = set(zip(g["wilayah_kode"].astype(int), g["periode"].astype(str)))
        daftar_per = sorted(set(tahun_terbit.get(seri, [])) | set(g["periode"].astype(str).unique()))
        for per in daftar_per:
            for kode in list(PROVINSI) + [INDONESIA]:
                tingkat = "nasional" if kode == INDONESIA else "provinsi"
                if (kode, per) in terisi:
                    kat, bukti = "terisi", ""
                elif not sudah_ada(kode, per):
                    kat = "belum_ada"
                    bukti = f"provinsi belum dibentuk; data penuh mulai {PROVINSI[kode][1]}"
                elif (
                    kode in INDUK
                    and (INDUK[kode], per) in terisi
                    and not any(w == kode and p < per for w, p in terisi)
                    and not any(
                        INDUK.get(k) == INDUK[kode]
                        and PROVINSI[k][1] == PROVINSI[kode][1]
                        and (k, per) in terisi
                        for k in PROVINSI
                    )
                ):
                    kat = "batas_lama"
                    bukti = f"{NAMA[INDUK[kode]]} masih diterbitkan dengan batas lama pada {per}; angka tidak dipecah"
                else:
                    kat = "missing"
                    bukti = "provinsi sudah ada dan penerbit tidak menyatakan angka itu tidak ada"
                baris.append(
                    {
                        "seri_kode": label,
                        "seri_dasar": seri,
                        "rincian": rinci,
                        "periode": per,
                        "wilayah_kode": kode,
                        "nama_wilayah": NAMA[kode],
                        "tingkat": tingkat,
                        "kategori": kat,
                        "bukti": bukti,
                    }
                )
    return pd.DataFrame(baris)


def jalankan():
    silver = muat_silver()
    tahun_terbit = muat_tahun_terbit_bps()
    g = bentuk_grid(silver, tahun_terbit)

    prov = g[g["tingkat"] == "provinsi"].copy()
    kel = (
        prov.assign(
            terisi=prov["kategori"] == "terisi",
            seharusnya=prov["kategori"].isin(["terisi", "missing"]),
        )
        .groupby(["seri_kode", "periode"], as_index=False)
        .agg(sel=("kategori", "size"), terisi=("terisi", "sum"), seharusnya_ada=("seharusnya", "sum"))
    )
    kel["persen_dari_38"] = (100 * kel["terisi"] / kel["sel"]).round(1)
    kel["persen_dari_seharusnya"] = (
        100 * kel["terisi"] / kel["seharusnya_ada"].where(kel["seharusnya_ada"] > 0)
    ).round(1)

    kat = (
        prov.pivot_table(
            index="seri_kode",
            columns="kategori",
            values="wilayah_kode",
            aggfunc="size",
            fill_value=0,
        )
        .reset_index()
    )

    nas = g[g["tingkat"] == "nasional"][["seri_kode", "periode", "kategori", "bukti"]]
    kosong = g[g["kategori"] != "terisi"].copy()
    batas = (
        g[g["kategori"] == "terisi"]
        .groupby(["seri_kode", "tingkat"], as_index=False)["periode"]
        .agg(periode_pertama="min", periode_terakhir="max", jumlah_periode="nunique")
    )

    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_csv = reports_dir / "grid_sel_kosong.csv"
    kosong.to_csv(out_csv, index=False)

    sel_grid = len(prov)
    sel_kosong_grid = int((prov["kategori"] != "terisi").sum())
    sel_missing = int((prov["kategori"] == "missing").sum())
    sel_belum_ada = int((prov["kategori"] == "belum_ada").sum())
    sel_batas_lama = int((prov["kategori"] == "batas_lama").sum())

    md = [
        "# Kelengkapan Panel 38 Provinsi x Periode dan Kategori Sel Kosong",
        "",
        "Dihasilkan oleh `src/silver/proses_grid.py` dari `data/silver/silver.parquet`. "
        "Grid menggunakan susunan **38 provinsi tahun 2025** x **periode terbit** per seri; "
        "baris nasional **Indonesia (`9999`)** dipisahkan dari baris provinsi.",
        "",
        "- `belum_ada`: provinsi belum dibentuk pada tahun tersebut (bukan missing).",
        "- `batas_lama`: provinsi baru sudah dibentuk, tetapi BPS masih menerbitkan provinsi induk dengan batas lama (angka tidak dipecah).",
        "- `missing`: provinsi sudah ada dan seharusnya terbit, tetapi nilainya kosong (strategi: dibiarkan kosong / tidak diimputasi, dicatat di `log-keputusan.csv`).",
        "",
        "## 1. Rekap Jumlah Sel per Kategori (Tingkat Provinsi)",
        "",
        _df_ke_markdown(kat),
        "",
        "## 2. Persen Sel Terisi per Seri per Periode (Tingkat Provinsi)",
        "",
        _df_ke_markdown(kel),
        "",
        "## 3. Kelengkapan Baris Indonesia (wilayah_kode = 9999)",
        "",
        _df_ke_markdown(nas[nas["kategori"] != "terisi"] if (nas["kategori"] != "terisi").any() else nas.head(10)),
        "",
        "## 4. Batas Pemakaian Panel",
        "",
        _df_ke_markdown(batas),
        "",
        f"Daftar lengkap seluruh sel kosong beserta buktinya tersimpan di `reports/grid_sel_kosong.csv` ({len(kosong)} baris).",
        "",
    ]
    out_md = reports_dir / "kelengkapan_panel.md"
    out_md.write_text("\n".join(md), encoding="utf-8")

    print(f"Tersimpan: {out_md}")
    print(f"Tersimpan: {out_csv} ({len(kosong)} sel kosong total)")
    print("\n=== Ringkasan Metrik untuk results/124450072/metrics.json ===")
    print(
        f"baris_silver={len(silver)} sel_grid={sel_grid} "
        f"sel_kosong_grid={sel_kosong_grid} sel_missing={sel_missing} "
        f"sel_belum_ada={sel_belum_ada} sel_batas_lama={sel_batas_lama}"
    )
    return g


if __name__ == "__main__":
    jalankan()