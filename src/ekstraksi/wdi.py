"""Pembaca WDI (JSON data dan metadata). Tidak membersihkan apa pun.

Keluaran: tabel panjang, kolom asal apa adanya (nama bertingkat diratakan
dengan titik, mis. 'indicator.id', 'country.value') + lineage
_berkas_raw dan _sha256_raw dari src.common.manifest.
"""
import json
from pathlib import Path

import pandas as pd

from src.common.manifest import RAW, sha256_raw

SERI = {"SE.ENR.PRSC.FM.ZS", "SE.PRM.CMPT.ZS"}


def _id_indikator(rec):
    """Data: rec['indicator']['id']; metadata: rec['id']."""
    ind = rec.get("indicator")
    if isinstance(ind, dict) and "id" in ind:
        return ind["id"]
    return rec.get("id")


def _daftar_record(isi):
    """Format API World Bank: [meta, [record, ...]]. Terima juga list datar."""
    if isinstance(isi, list) and len(isi) == 2 and isinstance(isi[1], list):
        return isi[1]
    if isinstance(isi, list):
        return isi
    raise ValueError("Struktur JSON WDI tidak dikenali")


def baca_berkas(path, raw=RAW):
    path = Path(path)
    rel = path.resolve().relative_to(Path(raw).resolve()).as_posix()
    with open(path, encoding="utf-8") as f:
        isi = json.load(f)
    semua = _daftar_record(isi)
    # saring menurut indicator.id hanya bila berkas memuat indikator
    ada_ind = any(_id_indikator(r) is not None and "." in str(_id_indikator(r)) for r in semua)
    rec = [r for r in semua if _id_indikator(r) in SERI] if ada_ind else semua
    df = pd.json_normalize(rec, sep=".")
    df["_berkas_raw"] = rel
    df["_sha256_raw"] = sha256_raw(rel, raw)
    return df


def baca_wdi(raw=RAW):
    """Baca semua JSON di data/raw/wdi/ -> satu DataFrame."""
    berkas = sorted((Path(raw) / "wdi").rglob("*.json"))
    if not berkas:
        raise FileNotFoundError(f"Tidak ada JSON WDI di {Path(raw) / 'wdi'}")
    return pd.concat([baca_berkas(b, raw) for b in berkas], ignore_index=True)