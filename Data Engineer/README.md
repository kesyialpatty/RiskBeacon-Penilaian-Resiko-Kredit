# Final Project From Excel (Airflow DAG + Local Excel)

Project ini mengadopsi struktur Streamlit dari `hck-037-final_project`, lalu konsep data pipeline diubah jadi lokal berbasis Excel.

- Input source lokal (`.csv` atau `.xlsx`)
- Output raw dari DAG: `data/raw_cs_training.xlsx`
- Output cleaned dari DAG: `data/cleaned_cs_training.xlsx`
- Validasi data dari DAG: `data/gx/cleaned_cs_training_validation.json`
- Serving: Streamlit app membaca cleaned Excel yang sama

Airflow tetap dipakai sebagai orkestrasi ETL, tetapi tidak ada koneksi SQL raw/datamart.

## Struktur Utama

- `dags/credit_risk_excel_etl.py` -> DAG Airflow `extract -> transform -> validate`
- `pipeline/airflow_tasks.py` -> callable Python task untuk DAG Airflow
- `pipeline/extract_excel.py` -> extract source tabular ke raw Excel
- `pipeline/transform_excel.py` -> cleaning, rename, dedup, feature engineering
- `pipeline/run_pipeline.py` -> runner manual (opsional, non-Airflow)
- `deployment/src/` -> halaman Streamlit (Home, Prediction, EDA, Pipeline)
- `deployment/artifacts/` -> model artifacts (`best_lgbm.pkl`, transformer, metadata)

## Setup

```bash
pip install -r requirements.txt
```

## Jalankan Dengan Airflow (Rekomendasi)

```bash
docker compose up -d
```

Lalu akses:

- Airflow: `http://localhost:8081` (`admin/admin`)
- Streamlit: `http://localhost:8501`

Di Airflow UI, trigger DAG:

- `credit_risk_excel_etl`

Setelah DAG selesai, file `data/cleaned_cs_training.xlsx` akan di-update oleh task DAG.

## Jalankan Pipeline Manual (Opsional)

Jika ingin tanpa Airflow, masih bisa:

```bash
python pipeline/run_pipeline.py
```

Jika source file berbeda:

```bash
python pipeline/run_pipeline.py --source path/to/source_file.csv
```

## Catatan Source Data

Source default untuk DAG ada di:

- `data/source/cs-training.csv`

Path ini bisa diubah via env var `SOURCE_FILE_PATH` pada service Airflow di `docker-compose.yml`.

## Jalankan Streamlit Saja (Opsional)

```bash
streamlit run deployment/src/streamlit_app.py
```

Lalu buka `http://localhost:8501`.
