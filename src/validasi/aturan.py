# Tahap 8 persiapan (Kartu #13): Aturan validasi dasar Silver (Pandera) +
# aturan khas Kasus 08.
import sys
from pathlib import Path

import pandas as pd

try:
    import pandera.pandas as pa
except ImportError:
    import pandera as pa

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.common.skema import KUNCI

WILAYAH_SAH = [
    1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2100,
    3100, 3200, 3300, 3400, 3500, 3600, 5100, 5200, 5300, 6100,
    6200, 6300, 6400, 6500, 7100, 7200, 7300, 7400, 7500, 7600,
    8100, 8200, 9100, 9200, 9400, 9500, 9600, 9700, 9999,
]

SERI_SAH = ["var304", "var2595", "var2600", "var1980", "var2211",
            "SE.ENR.PRSC.FM.ZS", "SE.PRM.CMPT.ZS"]

RENTANG_SATUAN = {
    "persen": (0.0, 100.0),
    "rasio_x100": (0.0, 500.0),
    "rasio": (0.0, 5.0),
    "persen_apk": (0.0, 150.0),
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


def satu_satuan_per_seri(df):
    return df.groupby("seri_kode")["satuan"].transform("nunique") == 1


def dalam_rentang_satuan(df):
    lo = df["satuan"].map(lambda s: RENTANG_SATUAN[s][0])
    hi = df["satuan"].map(lambda s: RENTANG_SATUAN[s][1])
    return (df["nilai"] >= lo) & (df["nilai"] <= hi)


def skema_silver():
    return pa.DataFrameSchema(
        {
            "sumber": pa.Column(str, pa.Check.isin(["bps", "wdi"])),
            "seri_kode": pa.Column(str, pa.Check.isin(SERI_SAH)),
            "wilayah_kode": pa.Column(int, pa.Check.isin(WILAYAH_SAH)),
            "nama_wilayah": pa.Column(str),
            "periode": pa.Column(str, pa.Check.str_matches(r"^\d{4}(-S[12]|-Q[1-4]|-(0[1-9]|1[0-2]))?$")),
            "jenis_periode": pa.Column(str, pa.Check.isin(["tahun", "semester", "triwulan", "bulan"])),
            "rincian": pa.Column(str),
            "nilai": pa.Column(float, nullable=False),
            "satuan": pa.Column(str, pa.Check.isin(list(RENTANG_SATUAN))),
            "_berkas_raw": pa.Column(str),
            "_sha256_raw": pa.Column(str, pa.Check.str_length(64, 64)),
        },
        checks=[
            pa.Check(satu_satuan_per_seri, name="satu_satuan_per_seri"),
            pa.Check(dalam_rentang_satuan, name="nilai_dalam_rentang_satuan"),
        ],
        unique=KUNCI,
        strict=False,
    )


def _norm_rincian(s):
    t = str(s).strip().lower()
    peta = {
        "sd/sederajat": "jenjang=sd", "sd / sederajat": "jenjang=sd",
        "smp/sederajat": "jenjang=smp", "smp / sederajat": "jenjang=smp",
        "sm/sederajat": "jenjang=sm", "sm / sederajat": "jenjang=sm",
        "sma/sederajat": "jenjang=sma", "sma / sederajat": "jenjang=sma",
        "tidak ada": "total", "nasional": "total", "": "total",
    }
    return peta.get(t, t)


def cek_rasio_paritas_masuk_akal(silver):
    s = silver[silver["seri_kode"].isin(["var2595", "var2600", "SE.ENR.PRSC.FM.ZS"])].copy()
    s["paritas"] = s["nilai"].where(s["satuan"] != "rasio_x100", s["nilai"] / 100.0)
    return s[(s["paritas"] <= 0.2) | (s["paritas"] > 3.0)][["seri_kode", "wilayah_kode", "periode", "nilai"]]


def cek_satu_satuan_per_jenis(silver):
    harus = {
        "var2595": "rasio_x100", "var2600": "rasio_x100", "SE.ENR.PRSC.FM.ZS": "rasio",
        "var304": "persen", "var1980": "persen", "var2211": "persen",
        "SE.PRM.CMPT.ZS": "persen_apk",
    }
    s = silver[silver["seri_kode"].isin(harus)]
    return s[s["satuan"] != s["seri_kode"].map(harus)][["seri_kode", "periode", "satuan"]]


def cek_apm_tanpa_total(silver):
    s = silver[silver["seri_kode"].isin(["var304", "var1980", "var2211"])].copy()
    s["rinci_baku"] = s["rincian"].map(_norm_rincian)
    return s[s["rinci_baku"] == "total"][["seri_kode", "wilayah_kode", "periode"]]


def cek_penyelesaian_sma_le_sd(silver):
    s = silver[silver["seri_kode"] == "var1980"].copy()
    s["rinci_baku"] = s["rincian"].map(_norm_rincian)
    lebar = s.pivot_table(index=["wilayah_kode", "periode"], columns="rinci_baku", values="nilai").dropna()
    if lebar.empty or "jenjang=sma" not in lebar.columns or "jenjang=sd" not in lebar.columns:
        return pd.DataFrame()
    return lebar[lebar["jenjang=sma"] > lebar["jenjang=sd"]].reset_index()


def jalankan(silver=None):
    if silver is None:
        silver_path = BASE_DIR / "data" / "silver" / "silver.parquet"
        if not silver_path.exists():
            from src.silver.bangun import jalankan as bangun_silver
            silver = bangun_silver()
        else:
            silver = pd.read_parquet(silver_path)

    gagal_pa = pd.DataFrame()
    try:
        skema_silver().validate(silver, lazy=True)
    except pa.errors.SchemaErrors as err:
        gagal_pa = err.failure_cases

    def cek_pa_kena(kata_kunci, kolom_target=None):
        if gagal_pa.empty:
            return False
        cek = gagal_pa["check"].astype(str)
        if kolom_target is not None:
            return gagal_pa["column"].astype(str).isin(kolom_target).any()
        return cek.str.contains(kata_kunci, case=False, regex=False).any()

    hasil_aturan = [
        ("kolom_dan_tipe", "keras (umum)",
         "11 kolom wajib Silver ada dengan tipe benar dan nilai tidak kosong",
         "GAGAL" if cek_pa_kena("dtype") or cek_pa_kena("nullable") else "LOLOS"),
        ("kunci_unik", "keras (umum)",
         "kombinasi 6 kolom kunci primer Silver tidak kembar",
         "GAGAL" if cek_pa_kena("unique") else "LOLOS"),
        ("wilayah_dan_periode", "keras (umum)",
         "wilayah_kode dari 38 provinsi + 9999; periode berbentuk baku",
         "GAGAL" if cek_pa_kena("", ["wilayah_kode", "periode", "jenis_periode"]) else "LOLOS"),
        ("sha256_valid", "keras (umum)",
         "panjang _sha256_raw tepat 64 karakter hex",
         "GAGAL" if cek_pa_kena("", ["_sha256_raw"]) else "LOLOS"),
        ("satu_satuan_per_seri", "keras (umum)",
         "setiap seri hanya memiliki satu satuan baku",
         "GAGAL" if cek_pa_kena("satu_satuan_per_seri") else "LOLOS"),
        ("nilai_dalam_rentang_satuan", "keras (umum)",
         "nilai berada dalam rentang sah satuannya (persen 0-100, dll.)",
         "GAGAL" if cek_pa_kena("nilai_dalam_rentang_satuan") else "LOLOS"),
    ]

    aturan_kasus = [
        ("rasio_paritas_masuk_akal", "keras (kasus)",
         "rasio paritas positif di rentang 0,2-3 setelah skala disamakan",
         True, cek_rasio_paritas_masuk_akal),
        ("satu_satuan_per_jenis", "keras (kasus)",
         "rasio BPS rasio_x100, WDI rasio/persen_apk, partisipasi persen",
         True, cek_satu_satuan_per_jenis),
        ("apm_tanpa_total", "keras (kasus)",
         "APM, penyelesaian, dan APS tidak punya total buatan",
         True, cek_apm_tanpa_total),
        ("penyelesaian_sma_tidak_melebihi_sd", "peringatan (kasus)",
         "tingkat penyelesaian SMA tidak melebihi SD pada provinsi & tahun sama",
         False, cek_penyelesaian_sma_le_sd),
    ]

    pelanggaran_kasus = []
    for nama, jenis, ket, keras, fn in aturan_kasus:
        df_langgar = fn(silver)
        status = "LOLOS" if df_langgar.empty else ("GAGAL" if keras else f"PERINGATAN ({len(df_langgar)} baris)")
        hasil_aturan.append((nama, jenis, ket, status))
        if not df_langgar.empty:
            pelanggaran_kasus.append((nama, df_langgar))

    df_hasil = pd.DataFrame(hasil_aturan, columns=["aturan", "jenis", "keterangan", "hasil"])
    n_total = len(df_hasil)
    n_lolos = int((df_hasil["hasil"] == "LOLOS").sum())
    n_gagal = int((df_hasil["hasil"] == "GAGAL").sum())

    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_md = reports_dir / "validasi.md"
    md = [
        "# Hasil Validasi Dasar Silver (Pandera & Aturan Kasus 08)",
        "",
        f"Dihasilkan oleh `src/validasi/aturan.py` pada `{len(silver):,}` baris `data/silver/silver.parquet`. "
        f"Ringkasan: **{n_lolos}/{n_total} aturan LOLOS**, **{n_gagal} GAGAL**.",
        "",
        _df_ke_markdown(df_hasil),
        "",
        "## Detail Pelanggaran",
        "",
        "Tidak ada pelanggaran aturan keras maupun peringatan."
        if not pelanggaran_kasus and gagal_pa.empty
        else "Lihat detail pelanggaran di output terminal.",
        "",
    ]
    out_md.write_text("\n".join(md), encoding="utf-8")

    print(f"Tersimpan: {out_md}")
    print(f"Ringkasan validasi: aturan_validasi={n_total} aturan_lolos={n_lolos} aturan_gagal={n_gagal}")
    if n_gagal > 0:
        raise ValueError(f"Validasi Silver GAGAL pada {n_gagal} aturan keras. Lihat {out_md}.")
    return df_hasil


if __name__ == "__main__":
    jalankan()