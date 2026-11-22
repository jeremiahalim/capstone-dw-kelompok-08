from src.gold import aturan_seleksi, muat_sql, nasional


def jalankan(silver):
    sel_gold = aturan_seleksi.jalankan(silver)
    hasil_nasional = nasional.jalankan()
    hasil_sql = muat_sql.jalankan()
    return {
        "sel_gold": sel_gold,
        "nasional": hasil_nasional,
        "sql": hasil_sql,
    }