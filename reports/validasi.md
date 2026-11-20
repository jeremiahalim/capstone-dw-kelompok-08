# Hasil Validasi Dasar Silver (Pandera & Aturan Kasus 08)

Dihasilkan oleh `src/validasi/aturan.py` pada `5,418` baris `data/silver/silver.parquet`. Ringkasan: **10/10 aturan LOLOS**, **0 GAGAL**.

| aturan | jenis | keterangan | hasil |
| --- | --- | --- | --- |
| kolom_dan_tipe | keras (umum) | 11 kolom wajib Silver ada dengan tipe benar dan nilai tidak kosong | LOLOS |
| kunci_unik | keras (umum) | kombinasi 6 kolom kunci primer Silver tidak kembar | LOLOS |
| wilayah_dan_periode | keras (umum) | wilayah_kode dari 38 provinsi + 9999; periode berbentuk baku | LOLOS |
| sha256_valid | keras (umum) | panjang _sha256_raw tepat 64 karakter hex | LOLOS |
| satu_satuan_per_seri | keras (umum) | setiap seri hanya memiliki satu satuan baku | LOLOS |
| nilai_dalam_rentang_satuan | keras (umum) | nilai berada dalam rentang sah satuannya (persen 0-100, dll.) | LOLOS |
| rasio_paritas_masuk_akal | keras (kasus) | rasio paritas positif di rentang 0,2-3 setelah skala disamakan | LOLOS |
| satu_satuan_per_jenis | keras (kasus) | rasio BPS rasio_x100, WDI rasio/persen_apk, partisipasi persen | LOLOS |
| apm_tanpa_total | keras (kasus) | APM, penyelesaian, dan APS tidak punya total buatan | LOLOS |
| penyelesaian_sma_tidak_melebihi_sd | peringatan (kasus) | tingkat penyelesaian SMA tidak melebihi SD pada provinsi & tahun sama | LOLOS |

## Detail Pelanggaran

Tidak ada pelanggaran aturan keras maupun peringatan.
