"""Pembaca data BPS (CSV dan JSON WebAPI) untuk Tahap 1 (Ekstraksi).

Tidak membersihkan apa pun: semua kolom dibaca sebagai teks apa adanya. Setiap baris diberi
`_berkas_raw` (jalur relatif terhadap data/raw/) dan `_sha256_raw` (dari src.common.manifest).
"""
import json

import pandas as pd

from src.common.manifest import RAW, sha256_raw

# Urutan kolom mengikuti CSV BPS, supaya hasil CSV dan JSON bisa digabung.
KOLOM = ["var_id", "wilayah_id", "wilayah", "turvar_id", "turvar",
         "tahun_id", "tahun", "periode_id", "periode", "nilai", "satuan"]


def _tambah_asal(df, path):
    rel = path.relative_to(RAW).as_posix()
    df["_berkas_raw"] = rel
    df["_sha256_raw"] = sha256_raw(rel)
    return df


def baca_csv(path):
    """CSV BPS: semua kolom tetap berupa teks (dtype=str), sel kosong tetap kosong."""
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    return _tambah_asal(df, path)


def _peta_kunci(var_id, vervar, turvar, tahun, periode, dengan_periode):
    """Kunci datacontent WebAPI BPS = vervar + var + turvar + tahun (+ periode)."""
    peta = {}
    for v in vervar:
        for t in turvar:
            for y in tahun:
                for p in (periode if dengan_periode else [None]):
                    kunci = f"{v}{var_id}{t}{y}" + ("" if p is None else str(p))
                    peta[kunci] = (v, t, y, p)
    return peta


def baca_json(path):
    """JSON WebAPI BPS (vervar, turvar, tahun, datacontent) diratakan jadi tabel panjang."""
    with open(path, encoding="utf-8-sig") as f:
        isi = json.load(f)
    blok = isi[0] if isinstance(isi, list) else isi
    if len(blok["var"]) != 1:
        raise ValueError(f"{path.name}: diharapkan satu var, ditemukan {len(blok['var'])}")
    var = blok["var"][0]
    var_id, satuan = var["val"], var.get("unit", "")

    vervar = {v["val"]: v["label"] for v in blok["vervar"]}
    turvar = {t["val"]: t["label"] for t in blok["turvar"]}
    tahun = {t["val"]: t["label"] for t in blok["tahun"]}
    periode = {p["val"]: p["label"] for p in blok.get("turtahun", [])} or {0: "Tahun"}
    data = blok.get("datacontent") or {}

    for dengan_periode in (True, False):
        peta = _peta_kunci(var_id, vervar, turvar, tahun, periode, dengan_periode)
        if all(k in peta for k in data):
            break
    else:
        raise ValueError(f"{path.name}: kunci datacontent tidak dikenali, contoh {list(data)[:3]}")

    pid_awal, plabel_awal = next(iter(periode.items()))
    baris = []
    for kunci, nilai in data.items():
        v, t, y, p = peta[kunci]
        pid, plabel = (pid_awal, plabel_awal) if p is None else (p, periode[p])
        baris.append([str(var_id), str(v), vervar[v], str(t), turvar[t], str(y), tahun[y],
                      str(pid), plabel, "" if nilai is None else str(nilai), satuan])
    return _tambah_asal(pd.DataFrame(baris, columns=KOLOM), path)


def berkas_bps():
    """CSV di bps/<snapshot>/ dan JSON di bps/<snapshot>/json/ (manifest_asal.json tidak ikut)."""
    return sorted(RAW.glob("bps/*/*.csv")) + sorted(RAW.glob("bps/*/json/*.json"))


def baca_semua():
    bagian = [(baca_csv if p.suffix == ".csv" else baca_json)(p) for p in berkas_bps()]
    return pd.concat(bagian, ignore_index=True)


def laporan():
    """Cetak jumlah baris per berkas, dan bandingkan dengan kolom `baris` di manifest_asal.json."""
    df = baca_semua()
    print(df.groupby("_berkas_raw").size().to_string())
    print("Total baris:", len(df))
    for path in sorted(RAW.glob("bps/*/manifest_asal.json")):
        with open(path, encoding="utf-8-sig") as f:
            tabel = json.load(f).get("tabel", {})
        print(f"\nBaris menurut {path.relative_to(RAW).as_posix()}:")
        for nama, info in tabel.items():
            print(f"  {nama}: {info.get('baris')}")
