from src.silver import bangun, metadata


def jalankan(data_ekstraksi=None):
    metadata.jalankan()
    df_silver = bangun.jalankan()

    try:
        from src.silver import proses_grid
        proses_grid.jalankan()
    except Exception as exc:
        print(f"[peringatan] proses_grid dilewati: {exc}")

    try:
        from src.silver import deteksi_anomali_bps
        deteksi_anomali_bps.jalankan()
    except Exception as exc:
        print(f"[peringatan] deteksi_anomali_bps dilewati: {exc}")

    return df_silver