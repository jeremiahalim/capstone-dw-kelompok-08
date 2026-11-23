from src.validasi import aturan, aturan_gold, kamus_data


def jalankan(silver, gold=None):
    hasil_silver = aturan.jalankan(silver)
    hasil_gold = aturan_gold.jalankan(silver, gold)
    kamus_data.jalankan()
    return {"silver": hasil_silver, "gold": hasil_gold}