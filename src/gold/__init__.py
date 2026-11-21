from src.gold import muat_sql, nasional


def jalankan(silver):
    hasil_nasional = nasional.jalankan()
    hasil_sql = muat_sql.jalankan()
    return {
        "nasional": hasil_nasional,
        "sql": hasil_sql,
    }