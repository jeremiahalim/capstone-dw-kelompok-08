# Persiapan Tahap 6 (Kartu #11): Tabel nasional (periode x seri) dan daftar pasangan rekonsiliasi.
import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

INDONESIA = 9999

PASANGAN = [
    {
        "id": "P1",
        "judul": "Penyelesaian SD: BPS (kohort umur) vs WDI (rasio masuk kasar kelas terakhir)",
        "utama": "var1980",
        "rincian_utama": "jenjang=sd",
        "pembanding": [("SE.PRM.CMPT.ZS", "total")],
        "jenis": "selisih",
        "kategori": "definisi berbeda: umur 3-5 tahun di atas umur lulus (BPS) vs siswa baru kelas terakhir tanpa memandang umur (WDI)",
        "pertanyaan": [
            (
                "Definisi BPS?",
                "var.note: persentase anak dan remaja yang menyelesaikan jenjang pendidikan pada rentang umur 1-3 tahun (standar SDG 3-5 tahun) di atas usia lulus normal, berbasis Susenas KOR (0-100%).",
            ),
            (
                "Definisi WDI?",
                "sourceNote: gross intake ratio to the last grade of primary education, tanpa memandang usia, dibagi populasi usia resmi kelas terakhir SD; nilai dapat melebihi 100%.",
            ),
        ],
    },
    {
        "id": "P2",
        "judul": "Paritas: BPS APK PT perempuan/laki-laki vs WDI GPI SD+menengah",
        "utama": "var2600",
        "rincian_utama": "total",
        "pembanding": [("SE.ENR.PRSC.FM.ZS", "total")],
        "jenis": "konteks",
        "kategori": "definisi berbeda: jenjang berbeda (PT vs SD dan menengah); skala BPS x100, WDI x1",
        "pertanyaan": [
            (
                "Jenis paritas sama?",
                "Ya, sama-sama jenis kelamin (perempuan/laki-laki). Namun jenjangnya berbeda (Perguruan Tinggi vs Primer & Sekunder), skala berbeda (rasio_x100 vs rasio), dan tidak ada tahun beririsan karena WDI berakhir 2018 sedangkan BPS mulai 2020.",
            ),
        ],
    },
    {
        "id": "P3",
        "judul": "Paritas kuintil APK SMA (BPS): tanpa pembanding di paket",
        "utama": "var2595",
        "rincian_utama": "total",
        "pembanding": [],
        "jenis": "konteks",
        "kategori": "tidak ada seri paritas kuintil di paket pembanding",
        "pertanyaan": [
            (
                "Apa jenis rasionya?",
                "Rasio APK jenjang SMA untuk kuintil pengeluaran terendah dibagi kuintil tertinggi (judul JSON), bukan paritas jenis kelamin.",
            ),
        ],
    },
]


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
    silver_path = BASE_DIR / "data" / "silver" / "silver.parquet"
    if not silver_path.exists():
        from src.silver.bangun import jalankan as bangun_silver

        return bangun_silver()
    return pd.read_parquet(silver_path)


def _norm_rincian(s):
    t = str(s).strip().lower()
    peta = {
        "sd/sederajat": "jenjang=sd",
        "sd / sederajat": "jenjang=sd",
        "smp/sederajat": "jenjang=smp",
        "smp / sederajat": "jenjang=smp",
        "sm/sederajat": "jenjang=sm",
        "sm / sederajat": "jenjang=sm",
        "sma/sederajat": "jenjang=sma",
        "sma / sederajat": "jenjang=sma",
        "tidak ada": "total",
        "nasional": "total",
        "": "total",
    }
    return peta.get(t, t)


def tabel_nasional(silver):
    nas = silver[silver["wilayah_kode"] == INDONESIA].copy()
    nas["rincian_baku"] = nas["rincian"].map(_norm_rincian)
    nas["kolom"] = nas["seri_kode"] + nas["rincian_baku"].map(
        lambda r: "" if r == "total" else f" [{r}]"
    )
    lebar = nas.pivot_table(
        index="periode", columns="kolom", values="nilai", aggfunc="first"
    ).sort_index()
    return nas, lebar


def hitung_irisan(nas, utama, rinci_utama, pembanding):
    if not pembanding:
        return []

    def per(seri, rinci):
        s = nas[(nas["seri_kode"] == seri) & (nas["rincian_baku"] == rinci)]
        return set(s["periode"].astype(str))

    a = per(utama, rinci_utama)
    return sorted(set.intersection(a, *[per(s, r) for s, r in pembanding]))


def jalankan():
    silver = muat_silver()
    nas, lebar = tabel_nasional(silver)
    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_csv = reports_dir / "tabel_nasional.csv"
    lebar.to_csv(out_csv)

    baris = []
    bagian = []
    for p in PASANGAN:
        bersama = hitung_irisan(nas, p["utama"], p["rincian_utama"], p["pembanding"])
        pembanding_str = (
            ", ".join(f"{s} [{r}]" for s, r in p["pembanding"]) or "—"
        )
        baris.append(
            {
                "id": p["id"],
                "seri_utama": f"{p['utama']} [{p['rincian_utama']}]",
                "pembanding": pembanding_str,
                "jenis": p["jenis"],
                "periode_beririsan": len(bersama),
                "tahun": ", ".join(bersama) or "—",
                "dugaan_kategori": p["kategori"],
            }
        )
        teks = [
            f"### {p['id']}: {p['judul']}",
            f"- Seri utama: `{p['utama']}` (rincian `{p['rincian_utama']}`)",
            "- Pembanding: "
            + (
                ", ".join(f"`{s}` (rincian `{r}`)" for s, r in p["pembanding"])
                or "tidak ada di paket"
            ),
            f"- Jenis: **{p['jenis']}**; tahun beririsan: {', '.join(bersama) or '—'}",
            f"- Dugaan kategori selisih (diuji di Sprint 2): {p['kategori']}",
            "",
            "Pertanyaan keterbandingan dan jawabannya:",
            "",
        ]
        teks += [
            f"{i}. **{q}** {a}" for i, (q, a) in enumerate(p["pertanyaan"], 1)
        ]
        bagian.append("\n".join(teks))

    daftar = pd.DataFrame(baris)

    n_selisih = int((daftar["jenis"] == "selisih").sum())
    n_konteks = int((daftar["jenis"] != "selisih").sum())
    tot_irisan = int(
        daftar.loc[daftar["jenis"] == "selisih", "periode_beririsan"].sum()
    )

    md = [
        "# Tabel Nasional dan Daftar Pasangan Rekonsiliasi (Persiapan Tahap 6)",
        "",
        "Dihasilkan oleh `src/gold/nasional.py` dari baris nasional Indonesia "
        "(`wilayah_kode = 9999`) pada `data/silver/silver.parquet`. "
        "Selisih dihitung penuh pada Sprint 2; Sprint 1 memastikan "
        "keterbandingan tiap pasangan dan mencatat tahun yang beririsan.",
        "",
        f"Tabel nasional lebar (`periode x seri`): `reports/tabel_nasional.csv` "
        f"({len(lebar)} periode, {len(lebar.columns)} kolom seri/rincian).",
        "",
        "## 1. Ringkasan Pasangan Rekonsiliasi",
        "",
        _df_ke_markdown(daftar),
        "",
        "## 2. Rincian Keterbandingan per Pasangan",
        "",
        "\n\n".join(bagian),
        "",
    ]

    out_md = reports_dir / "pasangan_rekonsiliasi.md"
    out_md.write_text("\n".join(md), encoding="utf-8")

    print(
        f"Tersimpan: {out_csv} ({len(lebar)} periode x {len(lebar.columns)} kolom)"
    )
    print(f"Tersimpan: {out_md}")
    print(
        f"Ringkasan metrik: pasangan_rekonsiliasi={n_selisih} "
        f"pasangan_konteks={n_konteks} periode_beririsan={tot_irisan}"
    )
    from src.gold import nasional_gold
    nasional_gold.jalankan()
    from src.gold import rekonsiliasi
    rekonsiliasi.jalankan()

if __name__ == "__main__":
    jalankan()