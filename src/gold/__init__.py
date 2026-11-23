from src.gold import muat_sql, nasional, panel


def jalankan(silver):
    try:
        from src.gold import aturan_seleksi
        aturan_seleksi.jalankan(silver)
    except ImportError:
        pass
    hasil_panel = panel.jalankan(silver)
    hasil_nasional = nasional.jalankan()
    hasil_sql = muat_sql.jalankan()
    return {
        "panel_provinsi": hasil_panel["panel_provinsi"],
        "panel_lineage": hasil_panel["panel_lineage"],
        "nasional": hasil_nasional,
        "sql": hasil_sql,
    }