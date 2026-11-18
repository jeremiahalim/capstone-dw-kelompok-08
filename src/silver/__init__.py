from src.silver.bangun import jalankan as bangun_silver
from src.silver.metadata import jalankan as jalankan_metadata


def jalankan(data_ekstraksi=None):
    """Menjalankan tahap penyusunan metadata dan tabel Silver."""
    jalankan_metadata()
    return bangun_silver()