import sys
from datetime import datetime

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


if "/opt/airflow" not in sys.path:
    sys.path.append("/opt/airflow")

from pipeline.airflow_tasks import (  # noqa: E402
    check_source_or_raw_ready,
    extract_raw_excel_task,
    transform_cleaned_excel_task,
    validate_cleaned_excel_task,
)


local_tz = pendulum.timezone("Asia/Jakarta")


with DAG(
    dag_id="credit_risk_excel_etl",
    start_date=datetime(2024, 1, 1, tzinfo=local_tz),
    schedule=None,
    catchup=False,
    tags=["excel", "etl", "airflow", "local-storage"],
) as dag:
    check_data_task = PythonOperator(
        task_id="check_source_or_raw_ready",
        python_callable=check_source_or_raw_ready,
    )

    extract_task = PythonOperator(
        task_id="extract_raw_excel",
        python_callable=extract_raw_excel_task,
    )

    transform_task = PythonOperator(
        task_id="transform_cleaned_excel",
        python_callable=transform_cleaned_excel_task,
    )

    validate_task = PythonOperator(
        task_id="validate_cleaned_excel",
        python_callable=validate_cleaned_excel_task,
    )

    check_data_task >> extract_task >> transform_task >> validate_task

