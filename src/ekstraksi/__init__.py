"""Tahap 1 (Ekstraksi): satukan keluaran semua pembaca menjadi satu tabel mentah ber-lineage."""
import pandas as pd

from src.common.manifest import RAW, baca
from src.ekstraksi import bps, wdi

# Berkas pendamping unduhan (bukan data); ada di MANIFEST tapi tidak dibaca.
BUKAN_DATA = ("manifest_asal.json",)


def jalankan(raw=RAW):
    mentah = pd.concat(
        [bps.baca_semua().assign(_sumber="bps"),
         wdi.baca_wdi(raw).assign(_sumber="wdi")],
        ignore_index=True,
    )
    terbaca = set(mentah["_berkas_raw"].unique())
    terlewat = sorted(b for b in baca(raw)
                      if b not in terbaca and not b.endswith(BUKAN_DATA))
    if terlewat:
        raise RuntimeError(f"Berkas di MANIFEST.csv belum terbaca: {terlewat}")
    print(f"ekstraksi: {len(terbaca)} berkas dibaca, {len(mentah)} baris mentah")
    return mentah