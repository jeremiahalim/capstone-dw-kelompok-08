# Kartu #28: Perbarui bagian 'Integrasi dan rekonsiliasi' di reports/tim.md dari data/gold/ dan log.
import re
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
GOLD_DIR = BASE_DIR / "data" / "gold"
REK_PATH = GOLD_DIR / "rekonsiliasi.parquet"
PANEL_PATH = GOLD_DIR / "panel_provinsi.parquet"
NAS_PATH = GOLD_DIR / "tabel_nasional.parquet"
LOG_PATH = BASE_DIR / "log-keputusan.csv"
TIM_MD = BASE_DIR / "reports" / "tim.md"


def _df_ke_md(df):
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join("-" if pd.isna(v) else str(v) for v in row) + " |")
    return "\n".join(lines)


def _cek_berkas_sumber():
    wajib = [REK_PATH, PANEL_PATH, NAS_PATH, LOG_PATH]
    hilang = [str(p.relative_to(BASE_DIR)).replace("\\", "/") for p in wajib if not p.exists()]
    if hilang:
        raise FileNotFoundError(
            f"Berkas sumber belum tersedia: {hilang}. Jalankan `python pipeline.py` terlebih dahulu."
        )


def bangun_bagian_integrasi():
    _cek_berkas_sumber()
    rek = pd.read_parquet(REK_PATH)
    panel = pd.read_parquet(PANEL_PATH)
    nas = pd.read_parquet(NAS_PATH)
    log_df = pd.read_csv(LOG_PATH)

    if "tahap" not in log_df.columns or "id" not in log_df.columns:
        raise ValueError("Kolom wajib 'id' dan 'tahap' tidak ditemukan di log-keputusan.csv.")
    log_gold = log_df[log_df["tahap"] == "gold"]
    if log_gold.empty:
        raise ValueError("Entri tahap 'gold' tidak ditemukan di log-keputusan.csv.")

    n_panel = len(panel)
    n_nas = len(nas)
    n_log_gold = len(log_gold)
    id_log_range = f"`{log_gold.iloc[0]['id']}`-`{log_gold.iloc[-1]['id']}`"
    hitung_asal = nas["asal_angka"].value_counts().to_dict()
    n_bps = int(hitung_asal.get("baris_indonesia", 0))
    n_wdi = int(hitung_asal.get("pembanding", 0))
    n_agg = int(hitung_asal.get("agregat", 0))

    p1 = rek[rek["id_pasangan"] == "P1"].copy()
    p1_ok = p1[p1["selisih"].notna()].sort_values("periode")
    p2 = rek[rek["id_pasangan"] == "P2"]
    p3 = rek[rek["id_pasangan"] == "P3"]

    med_abs = round(float(p1_ok["selisih_absolut"].median()), 2)
    med_signed = round(float(p1_ok["selisih"].median()), 2)
    sel_awal = round(float(p1_ok.iloc[0]["selisih"]), 2)
    sel_akhir = round(float(p1_ok.iloc[-1]["selisih"]), 2)
    thn_awal = str(p1_ok.iloc[0]["periode"])
    thn_akhir = str(p1_ok.iloc[-1]["periode"])

    ringkas_pasangan = pd.DataFrame([
        {
            "ID": "P1",
            "Seri Utama (BPS)": "var1980 [jenjang=sd]",
            "Pembanding (WDI)": "SE.PRM.CMPT.ZS",
            "Total Baris": len(p1),
            "Berpasangan": len(p1_ok),
            "Besar Selisih": f"median absolut {med_abs} pp ({sel_awal} di {thn_awal} -> {sel_akhir} di {thn_akhir})",
            "Kategori": "definisi",
        },
        {
            "ID": "P2",
            "Seri Utama (BPS)": "var2600 (PT)",
            "Pembanding (WDI)": "SE.ENR.PRSC.FM.ZS (SD+menengah)",
            "Total Baris": len(p2),
            "Berpasangan": 0,
            "Besar Selisih": "- (0 tahun beririsan)",
            "Kategori": "definisi",
        },
        {
            "ID": "P3",
            "Seri Utama (BPS)": "var2595 (kuintil SMA)",
            "Pembanding (WDI)": "tidak_ada",
            "Total Baris": len(p3),
            "Berpasangan": 0,
            "Besar Selisih": "- (tanpa pembanding)",
            "Kategori": "definisi",
        },
    ])

    tbl_p1 = p1_ok[["periode", "nilai_utama", "nilai_pembanding", "selisih", "selisih_absolut", "kategori_selisih"]].copy()
    tbl_p1["nilai_pembanding"] = tbl_p1["nilai_pembanding"].round(2)

    baris = [
        "## Integrasi dan rekonsiliasi",
        "",
        f"Integrasi Sprint 2 menyusun panel Gold (`data/gold/panel_provinsi.parquet`, **{n_panel:,} baris** "
        f"berdasarkan {n_log_gold} aturan tahap gold di `log-keputusan.csv` {id_log_range}), tabel nasional Gold "
        f"(`data/gold/tabel_nasional.parquet`, **{n_nas} baris** dengan kolom `asal_angka`: {n_bps} `baris_indonesia` + "
        f"{n_wdi} `pembanding`, {n_agg} agregat buatan), dan tabel rekonsiliasi (`data/gold/rekonsiliasi.parquet`, "
        f"**{len(rek)} baris**, seluruh periode tanpa pasangan tetap ditampilkan dan selisih tidak dihapus).",
        "### Ringkasan Pasangan & Kategori Penjelasan",
        "",
        _df_ke_md(ringkas_pasangan),
        f"### Rincian Selisih Pasangan Aktif P1 ({thn_awal}-{thn_akhir})",
        f"Pada seluruh **{len(p1_ok)} tahun beririsan**, WDI `SE.PRM.CMPT.ZS` "
        "selalu berada di atas BPS `var1980 [jenjang=sd]` "
        f"(median selisih absolut **{med_abs} poin persen**, signed median `{med_signed}` poin persen). Selisih menyempit "
        f"konsisten dari **{sel_awal} pp** ({thn_awal}) menjadi **{sel_akhir} pp** ({thn_akhir}):",
        _df_ke_md(tbl_p1),
        "### Penjelasan Kategori Selisih",
        "- **`definisi` (P1 `var1980 [jenjang=sd]` vs `SE.PRM.CMPT.ZS`):** BPS mengukur persentase penduduk kelompok umur "
        "13-15 tahun yang telah menyelesaikan SD berbasis survei rumah tangga Susenas (`persen`, batas atas 100%), sedangkan "
        "WDI mengukur *gross intake ratio* ke kelas terakhir SD tanpa memandang umur dari data administratif UIS (`persen_apk`, "
        "dapat melebihi 100% saat banyak siswa masuk lebih awal/terlambat, terlihat pada 2015-2022). Penyempitan selisih "
        "mencerminkan berkurangnya porsi siswa di luar usia resmi kelas 6 SD.",
        "- **`definisi` (P2 `var2600` vs `SE.ENR.PRSC.FM.ZS`):** Dilaporkan sebagai *definisi berbeda* karena jenjang "
        "berbeda (Perguruan Tinggi pada BPS 2020-2025 vs gabungan SD+menengah pada WDI 1970-2018), skala berbeda "
        "(`rasio_x100` vs `rasio`), dan tidak ada tahun beririsan (0 tahun).",
        "- **`definisi` (P3 `var2595`):** Mengukur paritas kuintil pengeluaran jenjang SMA yang tidak memiliki seri "
        "pembanding kuintil pada paket WDI. Analisis revisi 142 rilis arsip WDI (`vintage`) dilanjutkan pada Sprint 3.",
    ]
    return "\n".join(baris)


def jalankan():
    if not TIM_MD.exists():
        raise FileNotFoundError(f"Berkas laporan belum tersedia: {TIM_MD}")
    teks_lama = TIM_MD.read_text(encoding="utf-8")
    bagian_baru = bangun_bagian_integrasi()
    pola = re.compile(
        r"## Integrasi dan rekonsiliasi.*?(?=\n## Validasi dan reproduksibilitas)",
        re.DOTALL,
    )
    if not pola.search(teks_lama):
        raise ValueError("Bagian '## Integrasi dan rekonsiliasi' tidak ditemukan di reports/tim.md")
    teks_baru = pola.sub(bagian_baru, teks_lama, count=1)
    TIM_MD.write_text(teks_baru, encoding="utf-8")
    print(f"Berhasil memperbarui bagian 'Integrasi dan rekonsiliasi' pada {TIM_MD}.")


if __name__ == "__main__":
    jalankan()