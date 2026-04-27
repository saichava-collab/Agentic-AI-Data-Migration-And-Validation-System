from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/airflow/project"
PYTHONPATH_PREFIX = f"cd {PROJECT_DIR} && export PYTHONPATH={PROJECT_DIR} &&"

with DAG(
    dag_id="agentic_data_migration_validation",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["data-migration", "spark", "validation", "kafka", "llm"],
) as dag:
    setup_demo = BashOperator(
        task_id="setup_demo_data",
        bash_command=f"{PYTHONPATH_PREFIX} python scripts/setup_demo.py",
    )

    run_migration = BashOperator(
        task_id="run_batch_migration",
        bash_command=f"{PYTHONPATH_PREFIX} python jobs/batch_migration.py",
    )

    run_validation = BashOperator(
        task_id="run_agentic_validation",
        bash_command=f"{PYTHONPATH_PREFIX} python validators/run_validation.py",
    )

    generate_outputs = BashOperator(
        task_id="generate_expected_outputs",
        bash_command=f"{PYTHONPATH_PREFIX} python scripts/generate_expected_outputs.py",
    )

    setup_demo >> run_migration >> run_validation >> generate_outputs
