from src.validasi import aturan, kamus_data


def jalankan(silver, gold=None):
    hasil_aturan = aturan.jalankan(silver)
    kamus_data.jalankan()
    return hasil_aturan