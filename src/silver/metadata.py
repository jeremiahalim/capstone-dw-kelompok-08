import html
import json
import re
import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

RAW_BPS_DIR = BASE_DIR / "data" / "raw" / "bps" / "2026-10-17" / "json"
RAW_WDI_DIR = BASE_DIR / "data" / "raw" / "wdi" / "2026-10-20"
DOCS_SERI_PATH = BASE_DIR / "docs" / "seri.csv"
REPORT_META_PATH = BASE_DIR / "reports" / "metadata.md"
TARGET_WDI = ["SE.ENR.PRSC.FM.ZS", "SE.PRM.CMPT.ZS"]


def _bersih_html(teks):
    if not teks:
        return ""
    t = html.unescape(str(teks))
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t).strip()


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


def ekstrak_metadata_bps():
    hasil_bps = {}
    for file_json in sorted(RAW_BPS_DIR.glob("*.json")):
        with open(file_json, "r", encoding="utf-8-sig") as f:
            raw = json.load(f)
        halaman = raw if isinstance(raw, list) else [raw]
        if not halaman or not isinstance(halaman[0], dict):
            continue
        info_var = halaman[0].get("var", [{}])[0]
        kode_var = f"var{info_var.get('val')}"
        judul_asli = str(info_var.get("label", "")).strip()
        unit_asli = str(info_var.get("unit", "")).strip()
        catatan_asli = _bersih_html(info_var.get("note", ""))
        semua_nilai = []
        semua_tahun = set()
        for hal in halaman:
            for v in (hal.get("datacontent") or {}).values():
                if v is not None and str(v).strip() != "":
                    try:
                        semua_nilai.append(float(v))
                    except ValueError:
                        pass
            for th in hal.get("tahun", []):
                semua_tahun.add(str(th.get("label", "")).strip())
        rentang = f"{min(semua_nilai):.2f} - {max(semua_nilai):.2f}" if semua_nilai else "kosong"
        periode_str = f"{min(semua_tahun)}-{max(semua_tahun)}" if semua_tahun else "-"
        rel_path = f"bps/2026-10-17/json/{file_json.name}"
        hasil_bps[kode_var] = {
            "berkas_raw": rel_path,
            "judul_metadata": judul_asli,
            "unit_metadata": unit_asli or "(kosong)",
            "note_metadata": catatan_asli,
            "rentang_nilai": rentang,
            "periode_rentang": periode_str,
        }
    return hasil_bps


def ekstrak_metadata_wdi():
    hasil_wdi = {}
    ganda = {k: [] for k in TARGET_WDI}
    meta_dir = RAW_WDI_DIR / "metadata"
    for file_meta in sorted(meta_dir.glob("*_indikator.json")):
        with open(file_meta, "r", encoding="utf-8") as f:
            konten = json.load(f)
        daftar = konten[1] if isinstance(konten, list) and len(konten) > 1 else []
        for item in daftar:
            kode = item.get("id")
            if kode in TARGET_WDI:
                entri = {
                    "berkas": file_meta.name,
                    "name": (item.get("name") or "").strip(),
                    "sourceNote": _bersih_html(item.get("sourceNote") or ""),
                    "sourceOrganization": (item.get("sourceOrganization") or "").strip(),
                }
                ganda[kode].append(entri)
                if kode not in hasil_wdi:
                    hasil_wdi[kode] = entri
    # Hitung rentang nilai aktual dari data JSON WDI
    data_path = RAW_WDI_DIR / "data" / "kelompok-03-hal-01.json"
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            isi = json.load(f)
        recs = isi[1] if isinstance(isi, list) and len(isi) > 1 else []
        for kode in TARGET_WDI:
            vals = [float(r["value"]) for r in recs if r.get("indicator", {}).get("id") == kode and r.get("value") is not None]
            yrs = sorted([str(r["date"]) for r in recs if r.get("indicator", {}).get("id") == kode and r.get("value") is not None])
            if kode in hasil_wdi:
                hasil_wdi[kode]["rentang_nilai"] = f"{min(vals):.2f} - {max(vals):.2f}" if vals else "kosong"
                hasil_wdi[kode]["periode_rentang"] = f"{yrs[0]}-{yrs[-1]}" if yrs else "-"
    ringkas_ganda = []
    for kode, daftar_entri in ganda.items():
        isi_unik = {(e["name"], e["sourceNote"]) for e in daftar_entri}
        ringkas_ganda.append({
            "seri_kode": kode,
            "jumlah_berkas": len(daftar_entri),
            "daftar_berkas": ", ".join(e["berkas"] for e in daftar_entri),
            "isi_sama": "ya" if len(isi_unik) <= 1 else "berbeda",
        })
    return hasil_wdi, pd.DataFrame(ringkas_ganda)


def jalankan():
    meta_bps = ekstrak_metadata_bps()
    meta_wdi, df_ganda = ekstrak_metadata_wdi()
    daftar_seri = [
        {
            "sumber": "bps", "seri_kode": "var304", "tingkat": "provinsi",
            "nama_seri": meta_bps["var304"]["judul_metadata"],
            "asal_metadata": f"{meta_bps['var304']['berkas_raw']} (var.label, var.note)",
            "nama_baku": "Angka Partisipasi Murni (APM) menurut jenjang SD, SMP, SM",
            "katalog_satuan": "tidak_ada", "satuan": "persen",
            "rentang_aktual": meta_bps["var304"]["rentang_nilai"],
            "bukti_satuan": "judul 'Angka Partisipasi Murni'; var.unit kosong; nilai <= 100%",
            "jenis_periode": "tahunan", "periode_aktual": meta_bps["var304"]["periode_rentang"],
            "katalog_sdg": "4.5.1", "kode_sdg": "4.1",
            "bukti_sdg": "APM per jenjang bukan indeks paritas (4.5.1), melainkan partisipasi jenjang dasar-menengah (target 4.1)",
            "koreksi_katalog": "satuan tidak_ada -> persen; kode SDG 4.5.1 -> 4.1",
            "ref_log": "K-004, K-005",
        },
        {
            "sumber": "bps", "seri_kode": "var2595", "tingkat": "provinsi",
            "nama_seri": meta_bps["var2595"]["judul_metadata"],
            "asal_metadata": f"{meta_bps['var2595']['berkas_raw']} (var.label)",
            "nama_baku": "Rasio APK SMA/sederajat kuintil terendah terhadap kuintil tertinggi",
            "katalog_satuan": "tidak_ada", "satuan": "rasio_x100",
            "rentang_aktual": meta_bps["var2595"]["rentang_nilai"],
            "bukti_satuan": "judul 'Rasio APK ... kuintil terendah/tertinggi'; var.unit kosong; nilai 32-124 (rasio dikali 100)",
            "jenis_periode": "tahunan", "periode_aktual": meta_bps["var2595"]["periode_rentang"],
            "katalog_sdg": "4.5.1", "kode_sdg": "4.5.1",
            "bukti_sdg": "var.label diawali '4.5.1*'; indeks paritas kuintil pengeluaran jenjang SMA",
            "koreksi_katalog": "satuan tidak_ada -> rasio_x100",
            "ref_log": "K-004, K-005",
        },
        {
            "sumber": "bps", "seri_kode": "var2600", "tingkat": "provinsi",
            "nama_seri": meta_bps["var2600"]["judul_metadata"],
            "asal_metadata": f"{meta_bps['var2600']['berkas_raw']} (var.label)",
            "nama_baku": "Rasio APK perguruan tinggi perempuan terhadap laki-laki",
            "katalog_satuan": "tidak_ada", "satuan": "rasio_x100",
            "rentang_aktual": meta_bps["var2600"]["rentang_nilai"],
            "bukti_satuan": "judul 'Rasio APK ... perempuan/laki-laki'; var.unit kosong; nilai 62-260 (rasio dikali 100)",
            "jenis_periode": "tahunan", "periode_aktual": meta_bps["var2600"]["periode_rentang"],
            "katalog_sdg": "4.5.1", "kode_sdg": "4.5.1",
            "bukti_sdg": "var.label diawali '4.5.1*'; indeks paritas jenis kelamin jenjang perguruan tinggi",
            "koreksi_katalog": "satuan tidak_ada -> rasio_x100",
            "ref_log": "K-004, K-005",
        },
        {
            "sumber": "bps", "seri_kode": "var1980", "tingkat": "provinsi",
            "nama_seri": meta_bps["var1980"]["judul_metadata"],
            "asal_metadata": f"{meta_bps['var1980']['berkas_raw']} (var.label, var.note)",
            "nama_baku": "Tingkat penyelesaian pendidikan menurut jenjang (SD, SMP, SMA)",
            "katalog_satuan": "tidak_ada", "satuan": "persen",
            "rentang_aktual": meta_bps["var1980"]["rentang_nilai"],
            "bukti_satuan": "var.note: persentase anak dan remaja yang menyelesaikan jenjang pendidikan (0-100%)",
            "jenis_periode": "tahunan", "periode_aktual": meta_bps["var1980"]["periode_rentang"],
            "katalog_sdg": "4.1.2", "kode_sdg": "4.1.2",
            "bukti_sdg": "definisi var.note sesuai SDG 4.1.2 completion rate berbasis Susenas",
            "koreksi_katalog": "satuan tidak_ada -> persen",
            "ref_log": "K-005",
        },
        {
            "sumber": "bps", "seri_kode": "var2211", "tingkat": "provinsi",
            "nama_seri": meta_bps["var2211"]["judul_metadata"],
            "asal_metadata": f"{meta_bps['var2211']['berkas_raw']} (var.label)",
            "nama_baku": "Angka Partisipasi Sekolah (APS) menurut kelompok umur",
            "katalog_satuan": "tidak_ada", "satuan": "persen",
            "rentang_aktual": meta_bps["var2211"]["rentang_nilai"],
            "bukti_satuan": "judul 'Angka Partisipasi Sekolah'; var.unit kosong; nilai <= 100%",
            "jenis_periode": "tahunan", "periode_aktual": meta_bps["var2211"]["periode_rentang"],
            "katalog_sdg": "—", "kode_sdg": "—",
            "bukti_sdg": "tidak terpetakan ke kode SDG; dipertahankan sebagai konteks partisipasi umur (K-008)",
            "koreksi_katalog": "satuan tidak_ada -> persen; var.note salah tempel (disabilitas) diabaikan",
            "ref_log": "K-005, K-007, K-008",
        },
        {
            "sumber": "wdi", "seri_kode": "SE.ENR.PRSC.FM.ZS", "tingkat": "nasional",
            "nama_seri": meta_wdi["SE.ENR.PRSC.FM.ZS"]["name"],
            "asal_metadata": "wdi/2026-10-20/metadata/sumber2_indikator.json & sumber46_indikator.json",
            "nama_baku": meta_wdi["SE.ENR.PRSC.FM.ZS"]["name"],
            "katalog_satuan": "—", "satuan": "rasio",
            "rentang_aktual": meta_wdi["SE.ENR.PRSC.FM.ZS"]["rentang_nilai"],
            "bukti_satuan": "name menyebut 'gender parity index (GPI)'; skala rasio asli (0.77-1.02)",
            "jenis_periode": "tahunan", "periode_aktual": meta_wdi["SE.ENR.PRSC.FM.ZS"]["periode_rentang"],
            "katalog_sdg": "—", "kode_sdg": "4.5.1",
            "bukti_sdg": "tercantum pada metadata/sumber46_indikator.json (SDG 4.5.1)",
            "koreksi_katalog": "kode SDG kosong -> 4.5.1; satuan ditetapkan rasio",
            "ref_log": "K-005, K-006",
        },
        {
            "sumber": "wdi", "seri_kode": "SE.PRM.CMPT.ZS", "tingkat": "nasional",
            "nama_seri": meta_wdi["SE.PRM.CMPT.ZS"]["name"],
            "asal_metadata": "wdi/2026-10-20/metadata/sumber2_indikator.json & sumber46_indikator.json",
            "nama_baku": meta_wdi["SE.PRM.CMPT.ZS"]["name"],
            "katalog_satuan": "—", "satuan": "persen_apk",
            "rentang_aktual": meta_wdi["SE.PRM.CMPT.ZS"]["rentang_nilai"],
            "bukti_satuan": "sourceNote: gross intake ratio to last grade of primary tanpa batas umur sehingga dapat > 100%",
            "jenis_periode": "tahunan", "periode_aktual": meta_wdi["SE.PRM.CMPT.ZS"]["periode_rentang"],
            "katalog_sdg": "—", "kode_sdg": "4.1.2",
            "bukti_sdg": "tercantum pada metadata/sumber46_indikator.json (SDG 4.1.2)",
            "koreksi_katalog": "kode SDG kosong -> 4.1.2; satuan ditetapkan persen_apk",
            "ref_log": "K-005, K-006",
        },
    ]
    df_seri = pd.DataFrame(daftar_seri)
    DOCS_SERI_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_seri.to_csv(DOCS_SERI_PATH, index=False)
    t_nama = df_seri[["seri_kode", "nama_seri", "asal_metadata", "nama_baku"]]
    t_sat = df_seri[["seri_kode", "katalog_satuan", "satuan", "rentang_aktual", "bukti_satuan", "katalog_sdg", "kode_sdg", "bukti_sdg"]]
    t_kor = df_seri[["seri_kode", "periode_aktual", "jenis_periode", "koreksi_katalog", "ref_log"]]
    catatan_bps = pd.DataFrame([
        {"seri_kode": k, "berkas": v["berkas_raw"], "var_note_bersih": v["note_metadata"] or "(kosong)"}
        for k, v in sorted(meta_bps.items())
    ])
    catatan_wdi = pd.DataFrame([
        {"seri_kode": k, "berkas": v["berkas"], "sourceNote": v["sourceNote"] or "(kosong)"}
        for k, v in sorted(meta_wdi.items())
    ])
    md = [
        "# Laporan Audit Metadata Seri: Nama, Satuan, Periode, dan Kode SDG",
        "",
        "Dihasilkan oleh `src/silver/metadata.py` langsung dari berkas mentah di `data/raw/`. "
        "Tabel referensi lengkap tersimpan di `docs/seri.csv` dan setiap koreksi katalog tercatat di `log-keputusan.csv` (`K-004` s.d. `K-008`). "
        "Seluruh 7 seri berjenis periode tahunan (`tahun` di Silver); tidak ada perata-rataan periode semesteran/bulanan.",
        "",
        "## 1. Judul di Berkas Mentah, Sumber Metadata, dan Nama Baku",
        "",
        _df_ke_markdown(t_nama),
        "",
        "## 2. Perbandingan Katalog Awal vs Satuan & Kode SDG Final (beserta Bukti)",
        "",
        _df_ke_markdown(t_sat),
        "",
        "## 3. Ringkasan Koreksi Katalog, Periode, dan Rujukan Log Keputusan",
        "",
        _df_ke_markdown(t_kor),
        "",
        "## 4. Kutipan Catatan Metadata Sumber — BPS (`var.note`, tanpa tag HTML)",
        "",
        _df_ke_markdown(catatan_bps),
        "",
        "## 5. Kutipan Catatan Metadata Sumber — WDI (`sourceNote`) & Cek Berkas Ganda",
        "",
        _df_ke_markdown(catatan_wdi),
        "",
        "### Pemeriksaan Metadata WDI yang Muncul di Lebih dari Satu Berkas",
        "",
        _df_ke_markdown(df_ganda),
        "",
    ]
    REPORT_META_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_META_PATH.write_text("\n".join(md), encoding="utf-8")
    print(f"Tersimpan: {DOCS_SERI_PATH} dan {REPORT_META_PATH} ({len(df_seri)} seri teraudit)")
    return df_seri


if __name__ == "__main__":
    jalankan()