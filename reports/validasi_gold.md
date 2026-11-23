# Hasil Validasi Gold & Rekonsiliasi (Kartu #25)

Dihasilkan otomatis oleh `src/validasi/aturan_gold.py` dari `python pipeline.py`. Ringkasan: **6/6 aturan Gold LOLOS**, **0 GAGAL** (gabungan bersama 10 aturan Silver: **16/16 LOLOS**).

| aturan | jenis | keterangan | hasil | detail |
| --- | --- | --- | --- | --- |
| kunci_panel_provinsi_unik | keras (gold) | kunci (wilayah_kode, periode) unik & tanpa baris 9999 | LOLOS | duplikat=0, baris_9999=0, total=769 |
| kunci_panel_lineage_unik | keras (gold) | kunci (wilayah_kode, periode, indikator_gold) unik | LOLOS | duplikat=0, total_sel=5177 |
| satu_satuan_per_indikator_gold | keras (gold) | tiap indikator punya 1 satuan; paritas terpisah dari partisipasi | LOLOS | indikator_multi_satuan=0, kolom_kurang=0 |
| setiap_sel_gold_punya_pasangan_di_silver | keras (gold) | 100% sel panel_lineage cocok 1-ke-1 dengan kunci Silver | LOLOS | sel_tanpa_pasangan_silver=0, diperiksa=5177 |
| tabel_nasional_gold_valid | keras (gold) | kunci nasional unik, asal_angka sah, _berkas_raw terisi | LOLOS | duplikat=0, asal_tidak_sah=0, berkas_raw_kosong=0 |
| rekonsiliasi_berpasangan_berkategori | keras (rekonsiliasi) | tiap baris berpasangan punya selisih & kategori sah | LOLOS | duplikat=0, baris_berpasangan=9, kategori_tidak_sah=0, selisih_kosong=0 |
