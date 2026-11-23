# Tahap 5 (Kartu #23): Muat Silver & Gold ke DuckDB dengan kunci primer dan cek jumlah baris.
import sys
from pathlib import Path
import duckdb
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DB_PATH = BASE_DIR / "data" / "gold" / "gudang.duckdb"
DDL_PATH = Path(__file__).with_name("gudang.sql")
DOCS_SERI_PATH = BASE_DIR / "docs" / "seri.csv"
SILVER_PATH = BASE_DIR / "data" / "silver" / "silver.parquet"
GOLD_DIR = BASE_DIR / "data" / "gold"
REPORT_PATH = BASE_DIR / "reports" / "basis_data.md"

TABEL_GOLD = [
    ("gold_panel_provinsi", GOLD_DIR / "panel_provinsi.parquet"),
    ("gold_tabel_nasional", GOLD_DIR / "tabel_nasional.parquet"),
    ("gold_rekonsiliasi", GOLD_DIR / "rekonsiliasi.parquet"),
]

KOLOM_SILVER = [
    "sumber", "seri_kode", "wilayah_kode", "nama_wilayah", "periode",
    "jenis_periode", "rincian", "nilai", "satuan", "_berkas_raw", "_sha256_raw",
]


def _muat_tabel(con, nama_tabel, df_src):
    cur = con.cursor()
    cur.register("_tmp_df", df_src)
    cols = ", ".join(df_src.columns)
    cur.execute(f"INSERT INTO {nama_tabel} ({cols}) SELECT {cols} FROM _tmp_df")
    cur.unregister("_tmp_df")
    n_sql = int(cur.execute(f"SELECT COUNT(*) FROM {nama_tabel}").fetchall()[0][0])
    cur.close()
    if n_sql != len(df_src):
        raise ValueError(
            f"Jumlah baris {nama_tabel} tidak cocok: SQL={n_sql}, Parquet={len(df_src)}"
        )
    return n_sql

def _tulis_laporan(rekap):
    baris_tbl = [
        "| Tabel SQL | Berkas Parquet | Baris Parquet | Baris SQL | Status |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for r in rekap:
        baris_tbl.append(
            f"| `{r['tabel']}` | `{r['berkas']}` | {r['parquet']} | {r['sql']} | {r['status']} |"
        )

    md = [
        "# Pilihan Basis Data & Skema SQL Silver-Gold (Kartu #23)",
        "",
        "**Pilihan: DuckDB** (`data/gold/gudang.duckdb`, dibuat ulang oleh `src/gold/muat_sql.py` dari `python pipeline.py`; tidak di-commit karena `*.duckdb` masuk `.gitignore`).",
        "",
        "## 1. Alasan Pemilihan DuckDB untuk Lapis Silver & Gold",
        "- **Tanpa server, satu berkas:** seluruh anggota tim dan dosen penguji cukup menjalankan `python pipeline.py` tanpa memasang server PostgreSQL.",
        "- **Mesin analitik kolumnar (OLAP):** jauh lebih cepat daripada SQLite untuk agregasi, join panel 38 provinsi, dan tolok ukur skala 142 rilis WDI di Sprint 3.",
        "- **Menegakkan integritas skema:** DDL `src/gold/gudang.sql` menegakkan kunci primer, foreign key (`REFERENCES seri`), tipe kolom, serta batasan `CHECK`.",
        "",
        "## 2. Perbandingan dengan Menyimpan Respons JSON Mentah sebagai Dokumen",
        "- **Dokumen JSON mentah (tepat untuk lapis Bronze / `data/raw/`):** unggul menjaga struktur bersarang WebAPI BPS/WDI dan seluruh metadata asli (`var.note`, `sourceNote`) secara utuh tanpa kehilangan konteks untuk audit.",
        "- **SQL relasional kolumnar DuckDB (tepat untuk lapis Silver & Gold):** unggul untuk kueri analitik lintas seri, penegakan kunci primer agar tidak ada sel ganda, tipe numerik ketat, dan pembacaan langsung berkas Parquet.",
        "",
        "## 3. Verifikasi Jumlah Baris Parquet vs SQL",
        "",
        *baris_tbl,
    ]
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(md) + "\n", encoding="utf-8")


def jalankan():
    if not SILVER_PATH.exists():
        from src.silver.bangun import jalankan as bangun_silver
        bangun_silver()

    df_silver = pd.read_parquet(SILVER_PATH)[KOLOM_SILVER]
    df_seri = pd.read_csv(DOCS_SERI_PATH)
    df_seri_sql = df_seri[
        ["seri_kode", "sumber", "tingkat", "nama_baku", "satuan", "kode_sdg"]
    ].rename(columns={"kode_sdg": "sdg_kode"})

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    con = duckdb.connect(str(DB_PATH))
    con.execute(DDL_PATH.read_text(encoding="utf-8"))

    n_seri = _muat_tabel(con, "seri", df_seri_sql)
    n_silver = _muat_tabel(con, "silver", df_silver)
    rekap = [
        {
            "tabel": "seri",
            "berkas": "docs/seri.csv",
            "parquet": len(df_seri_sql),
            "sql": n_seri,
            "status": "COCOK",
        },
        {
            "tabel": "silver",
            "berkas": "data/silver/silver.parquet",
            "parquet": len(df_silver),
            "sql": n_silver,
            "status": "COCOK",
        },
    ]

    for nama_tabel, path_pq in TABEL_GOLD:
        if path_pq.exists():
            df_g = pd.read_parquet(path_pq)
            n_g = _muat_tabel(con, nama_tabel, df_g)
            rekap.append(
                {
                    "tabel": nama_tabel,
                    "berkas": str(path_pq.relative_to(BASE_DIR)).replace("\\", "/"),
                    "parquet": len(df_g),
                    "sql": n_g,
                    "status": "COCOK",
                }
            )
        else:
            rekap.append(
                {
                    "tabel": nama_tabel,
                    "berkas": str(path_pq.relative_to(BASE_DIR)).replace("\\", "/"),
                    "parquet": "-",
                    "sql": 0,
                    "status": "menunggu berkas",
                }
            )

    con.close()
    _tulis_laporan(rekap)
    ringkas = ", ".join(f"{r['tabel']}={r['sql']}" for r in rekap)
    print(f"muat_sql: berhasil memuat ke {DB_PATH.name} ({ringkas})")
    return rekap


if __name__ == "__main__":
    jalankan()