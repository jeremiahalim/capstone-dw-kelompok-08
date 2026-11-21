# Persiapan Tahap 5 (Kartu #12): Memuat Silver ke DuckDB dengan kunci primer,
# foreign key, dan batasan CHECK, serta menulis draf reports/basis_data.md.
import sys
from pathlib import Path
import duckdb
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DB_PATH = BASE_DIR / "data" / "gold" / "gudang.duckdb"
DDL_PATH = Path(__file__).with_name("silver.sql")
DOCS_SERI_PATH = BASE_DIR / "docs" / "seri.csv"
SILVER_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"
REPORT_PATH = BASE_DIR / "reports" / "basis_data.md"

KOLOM_SILVER = [
    "sumber",
    "seri_kode",
    "wilayah_kode",
    "nama_wilayah",
    "periode",
    "jenis_periode",
    "rincian",
    "nilai",
    "satuan",
    "_berkas_raw",
    "_sha256_raw",
]


def muat_silver():
    if not SILVER_PATH.exists():
        from src.silver.bangun import jalankan as bangun_silver

        return bangun_silver()
    return pd.read_parquet(SILVER_PATH)


def muat_tabel_seri():
    df = pd.read_csv(DOCS_SERI_PATH)
    nama_kol = "nama_baku" if "nama_baku" in df.columns else "nama_seri"
    sdg_kol = "kode_sdg" if "kode_sdg" in df.columns else "sdg_kode"
    if "tingkat" in df.columns:
        tingkat = df["tingkat"].astype(str).str.strip()
    else:
        tingkat = (
            df["sumber"]
            .astype(str)
            .str.strip()
            .map(lambda s: "provinsi" if s == "bps" else "nasional")
        )
    return pd.DataFrame(
        {
            "seri_kode": df["seri_kode"].astype(str).str.strip(),
            "sumber": df["sumber"].astype(str).str.strip(),
            "tingkat": tingkat,
            "nama_baku": df[nama_kol].astype(str).str.strip(),
            "satuan": df["satuan"].astype(str).str.strip(),
            "sdg_kode": df[sdg_kol].fillna("—").astype(str).str.strip(),
        }
    )


def tulis_laporan_basis_data(n_baris, n_seri):
    baris_md = [
        "# Pilihan Basis Data dan Rancangan Skema SQL Silver (Draf Laporan Tim)",
        "",
        "**Pilihan: DuckDB** (`data/gold/gudang.duckdb`, dibuat ulang oleh "
        "`src/gold/muat_sql.py`; tidak di-commit karena `*.duckdb` masuk "
        "`.gitignore`).",
        "",
        "## 1. Alasan Pemilihan DuckDB",
        "- **Satu berkas tanpa server:** seluruh anggota tim dan dosen penguji "
        "dapat menjalankan skrip pemuat langsung dari klon repositori tanpa memasang "
        "layanan server tambahan.",
        "- **Dirancang untuk kueri analitik (OLAP):** sangat cepat untuk "
        "agregasi, *pivot*, dan penggabungan panel yang menjadi pekerjaan utama Gold di "
        "Sprint 2.",
        "- **Terintegrasi langsung dengan Parquet & Tahap 7:** dapat membaca "
        "`data/silver/silver.parquet` secara native dan dipakai kembali untuk tolok ukur "
        "perbandingan `pandas` vs `DuckDB` pada arsip WDI di Sprint 3.",
        "",
        "Alternatif yang dipertimbangkan:",
        "- **SQLite:** paling sederhana dan tersedia di pustaka standar Python, "
        "tetapi kalah cepat untuk kueri analitik/pivot skala besar di Tahap 7.",
        "- **PostgreSQL:** dekat dengan lingkungan produksi, tetapi membutuhkan "
        "instalasi dan konfigurasi server lokal di setiap laptop anggota dan penguji.",
        "",
        "## 2. Rancangan Skema SQL (`src/gold/silver.sql`)",
        f"- **Tabel `seri` ({n_seri} baris):** memuat katalog seri dari "
        "`docs/seri.csv` dengan `PRIMARY KEY (seri_kode)` dan `CHECK (tingkat IN "
        "('provinsi', 'nasional'))`.",
        f"- **Tabel `silver` ({n_baris:,} baris):** memuat seluruh baris "
        "`data/silver/silver.parquet` dengan `PRIMARY KEY (sumber, seri_kode, "
        "wilayah_kode, periode, rincian, _berkas_raw)`, `FOREIGN KEY (seri_kode) "
        "REFERENCES seri (seri_kode)`, serta `CHECK` untuk `wilayah_kode`, "
        "`jenis_periode`, dan panjang `_sha256_raw` (= 64).",
        "- Basis data berperan sebagai lapis validasi terakhir: baris yang "
        "melanggar kunci primer, rujukan seri, atau aturan `CHECK` otomatis ditolak saat "
        "dimuat.",
        "",
        "## 3. Perbandingan Tabel SQL vs Menyimpan Respons JSON Mentah sebagai Dokumen",
        "Respons JSON WebAPI BPS dan WDI berbentuk dokumen bersarang (*nested "
        "document*): satu berkas berisi beberapa halaman tahun, daftar kamus label "
        "(`vervar`, `turvar`, `tahun`), metadata seri (`var.note` yang memuat tag HTML), "
        "serta objek `datacontent` dengan kunci gabungan.",
        "- **Penyimpanan dokumen (JSON mentah di `data/raw/`):** unggul untuk "
        "arsip lapis Bronze karena mempertahankan seluruh metadata, struktur asli, dan "
        "sidik SHA-256 tanpa perubahan apa pun.",
        "- **Penyimpanan relasional/tabel (Silver di DuckDB):** jauh lebih "
        "tepat untuk analisis dan integrasi karena setiap observasi sudah terurai "
        "menjadi kolom datar (`wilayah_kode`, `periode`, `rincian`, `nilai`, `satuan`) "
        "yang dapat dikueri dengan SQL, digabung antarsumber, serta ditegakkan kunci "
        "primer dan integritas referensialnya.",
        "Tim mempertahankan keduanya sesuai fungsi lapisannya: respons JSON "
        "mentah tetap sebagai dokumen arsip di `data/raw/` (Bronze), sedangkan data "
        "terstruktur dimuat sebagai tabel relasional di DuckDB (Silver/Gold).",
    ]
    isi = "\n".join(baris_md) + "\n"
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(isi, encoding="utf-8")


def jalankan():
    silver = muat_silver()[KOLOM_SILVER].copy()
    seri = muat_tabel_seri()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    DB_PATH.unlink(missing_ok=True)
    with duckdb.connect(str(DB_PATH)) as con:
        con.execute(DDL_PATH.read_text(encoding="utf-8"))
        con.register("seri_df", seri)
        con.execute("INSERT INTO seri SELECT * FROM seri_df")
        con.register("silver_df", silver)
        kolom_sql = ", ".join(KOLOM_SILVER)
        con.execute(
            f"INSERT INTO silver ({kolom_sql}) SELECT {kolom_sql} FROM silver_df"
        )
        n_seri = con.execute("SELECT count(*) FROM seri").fetchone()[0]
        n_silver = con.execute("SELECT count(*) FROM silver").fetchone()[0]
    if n_silver != len(silver):
        raise AssertionError(
            f"DuckDB memuat {n_silver} baris, sedangkan Silver {len(silver)} baris"
        )
    tulis_laporan_basis_data(n_silver, n_seri)
    print(
        f"Berhasil memuat {n_silver:,} baris Silver dan {n_seri} seri ke {DB_PATH}"
    )
    print(f"Laporan tersimpan: {REPORT_PATH}")
    return n_silver


if __name__ == "__main__":
    jalankan()