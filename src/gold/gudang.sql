-- Skema SQL Lengkap Silver & Gold (DuckDB) — Kartu #23.
-- Dimuat otomatis oleh src/gold/muat_sql.py dari python pipeline.py.

CREATE TABLE seri (
    seri_kode VARCHAR PRIMARY KEY,
    sumber VARCHAR NOT NULL,
    tingkat VARCHAR NOT NULL CHECK (tingkat IN ('provinsi', 'nasional')),
    nama_baku VARCHAR NOT NULL,
    satuan VARCHAR NOT NULL,
    sdg_kode VARCHAR
);

CREATE TABLE silver (
    sumber VARCHAR NOT NULL,
    seri_kode VARCHAR NOT NULL REFERENCES seri (seri_kode),
    wilayah_kode INTEGER NOT NULL CHECK (
        wilayah_kode = 9999 OR wilayah_kode BETWEEN 1100 AND 9799
    ),
    nama_wilayah VARCHAR NOT NULL,
    periode VARCHAR NOT NULL,
    jenis_periode VARCHAR NOT NULL CHECK (
        jenis_periode IN ('tahun', 'semester', 'triwulan', 'bulan')
    ),
    rincian VARCHAR NOT NULL,
    nilai DOUBLE NOT NULL,
    satuan VARCHAR NOT NULL,
    _berkas_raw VARCHAR NOT NULL,
    _sha256_raw VARCHAR NOT NULL CHECK (length(_sha256_raw) = 64),
    PRIMARY KEY (sumber, seri_kode, wilayah_kode, periode, rincian, _berkas_raw)
);

CREATE TABLE gold_panel_provinsi (
    wilayah_kode INTEGER NOT NULL CHECK (wilayah_kode BETWEEN 1100 AND 9799),
    nama_wilayah VARCHAR NOT NULL,
    periode VARCHAR NOT NULL,
    penyelesaian_sd DOUBLE,
    penyelesaian_smp DOUBLE,
    penyelesaian_sma DOUBLE,
    apm_sd DOUBLE,
    apm_smp DOUBLE,
    apm_sm DOUBLE,
    aps_7_12 DOUBLE,
    aps_13_15 DOUBLE,
    aps_16_18 DOUBLE,
    aps_19_23 DOUBLE,
    paritas_kuintil_sma_x100 DOUBLE,
    paritas_kuintil_sma_rasio DOUBLE,
    paritas_gender_pt_x100 DOUBLE,
    paritas_gender_pt_rasio DOUBLE,
    ada_patahan_definisi BOOLEAN NOT NULL,
    ada_patahan_wilayah BOOLEAN NOT NULL,
    ada_outlier BOOLEAN NOT NULL,
    jumlah_sumber_berkas INTEGER NOT NULL,
    sumber_berkas_raw VARCHAR NOT NULL,
    PRIMARY KEY (wilayah_kode, periode)
);

CREATE TABLE gold_tabel_nasional (
    periode VARCHAR NOT NULL,
    sumber VARCHAR NOT NULL,
    seri_kode VARCHAR NOT NULL REFERENCES seri (seri_kode),
    rincian VARCHAR NOT NULL,
    seri_rincian VARCHAR NOT NULL,
    asal_angka VARCHAR NOT NULL CHECK (
        asal_angka IN ('baris_indonesia', 'agregat', 'pembanding')
    ),
    nilai DOUBLE NOT NULL,
    satuan VARCHAR NOT NULL,
    nilai_seragam DOUBLE NOT NULL,
    satuan_seragam VARCHAR NOT NULL,
    _berkas_raw VARCHAR NOT NULL,
    _sha256_raw VARCHAR NOT NULL CHECK (length(_sha256_raw) = 64),
    PRIMARY KEY (periode, seri_kode, rincian)
);

CREATE TABLE gold_rekonsiliasi (
    id_pasangan VARCHAR NOT NULL,
    periode VARCHAR NOT NULL,
    seri_utama VARCHAR NOT NULL,
    rincian_utama VARCHAR NOT NULL,
    seri_pembanding VARCHAR NOT NULL,
    nilai_utama DOUBLE,
    satuan_utama VARCHAR NOT NULL,
    nilai_pembanding DOUBLE,
    satuan_pembanding VARCHAR NOT NULL,
    selisih DOUBLE,
    selisih_absolut DOUBLE,
    selisih_persen DOUBLE,
    kategori_selisih VARCHAR NOT NULL CHECK (
        kategori_selisih IN (
            'definisi',
            'metode',
            'vintage',
            'cakupan',
            'belum_terjelaskan'
        )
    ),
    penjelasan VARCHAR NOT NULL,
    _berkas_raw_utama VARCHAR NOT NULL,
    _berkas_raw_pembanding VARCHAR NOT NULL,
    PRIMARY KEY (id_pasangan, periode)
);