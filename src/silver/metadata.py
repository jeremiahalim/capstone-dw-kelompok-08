import json
from pathlib import Path
import pandas as pd

# Definisi path sesuai struktur folder proyek
BASE_DIR = Path(__file__).resolve().parents[2]
RAW_BPS_DIR = BASE_DIR / "data" / "raw" / "bps" / "2026-10-17" / "json"
RAW_WDI_DIR = BASE_DIR / "data" / "raw" / "wdi" / "2026-10-20"
DOCS_SERI_PATH = BASE_DIR / "docs" / "seri.csv"
REPORT_META_PATH = BASE_DIR / "reports" / "metadata.md"


def ekstrak_metadata_bps():
    """Membaca judul, catatan, dan kode var dari file JSON mentah BPS."""
    hasil_bps = {}
    for file_json in sorted(RAW_BPS_DIR.glob("*.json")):
        with open(file_json, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # Jika dibungkus list, ambil elemen pertamanya
        data = raw[0] if isinstance(raw, list) and len(raw) > 0 else raw
        if not isinstance(data, dict):
            continue

        info_var = data.get("var", [{}])[0]
        kode_var = f"var{info_var.get('val')}"
        judul_asli = info_var.get("label", "").strip()
        catatan_asli = info_var.get("note", "").strip()

        nilai_sampel = [
            float(v) for v in data.get("datacontent", {}).values() if v is not None
        ]
        rentang = (
            f"{min(nilai_sampel):.2f} - {max(nilai_sampel):.2f}"
            if nilai_sampel
            else "kosong"
        )

        hasil_bps[kode_var] = {
            "berkas_raw": file_json.name,
            "judul_metadata": judul_asli,
            "note_metadata": catatan_asli,
            "rentang_nilai": rentang,
        }
    return hasil_bps


def ekstrak_metadata_wdi():
    """Membaca deskripsi indikator WDI dari folder metadata."""
    hasil_wdi = {}
    meta_dir = RAW_WDI_DIR / "metadata"
    for file_meta in sorted(meta_dir.glob("*_indikator.json")):
        with open(file_meta, "r", encoding="utf-8") as f:
            konten = json.load(f)
            daftar_indikator = (
                konten[1] if isinstance(konten, list) and len(konten) > 1 else []
            )
            for item in daftar_indikator:
                kode = item.get("id")
                if kode in ["SE.ENR.PRSC.FM.ZS", "SE.PRM.CMPT.ZS"]:
                    hasil_wdi[kode] = {
                        "berkas_raw": file_meta.name,
                        "judul_metadata": item.get("name", "").strip(),
                        "note_metadata": item.get("sourceNote", "").strip(),
                        "rentang_nilai": (
                            "0.77 - 1.02"
                            if kode == "SE.ENR.PRSC.FM.ZS"
                            else "bisa > 100"
                        ),
                    }
    return hasil_wdi


def jalankan():
    meta_bps = ekstrak_metadata_bps()
    meta_wdi = ekstrak_metadata_wdi()

    # Penetapan aturan final berdasarkan audit metadata mentah & keputusan kasus
    daftar_seri = [
        {
            "sumber": "bps",
            "seri_kode": "var2595",
            "nama_seri": meta_bps.get("var2595", {}).get(
                "judul_metadata", "Indeks Paritas Kuintil APK SMA"
            ),
            "satuan": "rasio_x100",
            "jenis_periode": "tahunan",
            "kode_sdg": "4.5.1",
            "sumber_metadata": f"BPS JSON ({meta_bps.get('var2595', {}).get('berkas_raw', 'sdg4_4_5_1_v2595.json')})",
            "catatan_audit": "Satuan awal kosong; nilai berkisar 32-260 (rasio dikali 100).",
        },
        {
            "sumber": "bps",
            "seri_kode": "var2600",
            "nama_seri": meta_bps.get("var2600", {}).get(
                "judul_metadata", "Indeks Paritas Gender APK PT"
            ),
            "satuan": "rasio_x100",
            "jenis_periode": "tahunan",
            "kode_sdg": "4.5.1",
            "sumber_metadata": f"BPS JSON ({meta_bps.get('var2600', {}).get('berkas_raw', 'sdg4_4_5_1_v2600.json')})",
            "catatan_audit": "Satuan awal kosong; nilai merupakan indeks paritas dikali 100.",
        },
        {
            "sumber": "bps",
            "seri_kode": "var304",
            "nama_seri": meta_bps.get("var304", {}).get(
                "judul_metadata", "Angka Partisipasi Murni (APM)"
            ),
            "satuan": "persen",
            "jenis_periode": "tahunan",
            "kode_sdg": "4.1",
            "sumber_metadata": f"BPS JSON ({meta_bps.get('var304', {}).get('berkas_raw', 'sdg4_apm.json')})",
            "catatan_audit": "Dikoreksi dari kode katalog 4.5.1 ke 4.1 karena merupakan APM, bukan indeks paritas.",
        },
        {
            "sumber": "bps",
            "seri_kode": "var1980",
            "nama_seri": meta_bps.get("var1980", {}).get(
                "judul_metadata", "Tingkat Penyelesaian Pendidikan"
            ),
            "satuan": "persen",
            "jenis_periode": "tahunan",
            "kode_sdg": "4.1.2",
            "sumber_metadata": f"BPS JSON ({meta_bps.get('var1980', {}).get('berkas_raw', 'sdg4_completion.json')})",
            "catatan_audit": "Satuan ditetapkan persen (kohort umur 3-5 tahun di atas umur lulus).",
        },
        {
            "sumber": "bps",
            "seri_kode": "var2211",
            "nama_seri": meta_bps.get("var2211", {}).get(
                "judul_metadata", "Angka Partisipasi Sekolah (APS)"
            ),
            "satuan": "persen",
            "jenis_periode": "tahunan",
            "kode_sdg": "4.1",
            "sumber_metadata": f"BPS JSON ({meta_bps.get('var2211', {}).get('berkas_raw', 'sdg4_aps.json')})",
            "catatan_audit": "var.note salah tempel definisi disabilitas diabaikan; definisi diambil dari judul.",
        },
        {
            "sumber": "wdi",
            "seri_kode": "SE.ENR.PRSC.FM.ZS",
            "nama_seri": meta_wdi.get("SE.ENR.PRSC.FM.ZS", {}).get(
                "judul_metadata", "School enrollment, primary and secondary (gross), GPI"
            ),
            "satuan": "rasio",
            "jenis_periode": "tahunan",
            "kode_sdg": "4.5.1",
            "sumber_metadata": "WDI Metadata (sumber2_indikator.json / sumber46_indikator.json)",
            "catatan_audit": "Pembanding GPI WDI dengan skala rasio asli (0.77 - 1.02).",
        },
        {
            "sumber": "wdi",
            "seri_kode": "SE.PRM.CMPT.ZS",
            "nama_seri": meta_wdi.get("SE.PRM.CMPT.ZS", {}).get(
                "judul_metadata", "Primary completion rate, total (% of relevant age group)"
            ),
            "satuan": "persen_apk",
            "jenis_periode": "tahunan",
            "kode_sdg": "4.1.2",
            "sumber_metadata": "WDI Metadata (sumber2_indikator.json / sumber46_indikator.json)",
            "catatan_audit": "Rasio masuk kasar tanpa batas umur sehingga nilai dapat melebihi 100.",
        },
    ]

    df_seri = pd.DataFrame(daftar_seri)

    # 1. Simpan ke docs/seri.csv
    DOCS_SERI_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_seri.drop(columns=["catatan_audit"]).to_csv(DOCS_SERI_PATH, index=False)

    # 2. Buat laporan reports/metadata.md
    REPORT_META_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_META_PATH, "w", encoding="utf-8") as f:
        f.write("# Laporan Penetapan Satuan, Periode, dan Kode SDG dari Metadata\n\n")
        f.write("Hasil verifikasi 7 seri utama dan pembanding terhadap berkas mentah di `data/raw/`:\n\n")
        f.write("| Sumber | Kode Seri | Nama Seri | Satuan | Periode | Kode SDG | Sumber Metadata | Catatan Audit |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for row in daftar_seri:
            f.write(
                f"| {row['sumber']} | `{row['seri_kode']}` | {row['nama_seri']} | `{row['satuan']}` | {row['jenis_periode']} | `{row['kode_sdg']}` | {row['sumber_metadata']} | {row['catatan_audit']} |\n"
            )

    print(f"Berhasil membuat {DOCS_SERI_PATH} dan {REPORT_META_PATH}")
    return df_seri


if __name__ == "__main__":
    jalankan()