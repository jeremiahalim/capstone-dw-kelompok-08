"""Tahap 1 - Ekstraksi (pertemuan X). Milik tim.

Baca setiap berkas di data/raw/ (CSV, JSON WebAPI BPS, XLSX BNPB, SDMX ILO, JSON WDI) menjadi
DataFrame mentah yang setia pada sumbernya: jangan membersihkan di sini, cukup ratakan struktur
dan catat asal tiap baris (`_berkas_raw` relatif data/raw/, `_sha256_raw` dari src.common.manifest).
"""
from . import bps


def jalankan():
    """Kembalikan {nama_sumber: DataFrame mentah}."""
    hasil = {"bps": bps.baca_semua()}
    # TODO (kartu pembaca WDI): hasil["wdi"] = wdi.baca_semua()
    return hasil
