from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import subprocess
from PortfolioOptimizer.logging import logger

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
}

dag = DAG(
    dag_id="ForecastingPipeline",
    default_args=default_args,
    description="Run the Forecasting Pipeline.",
    schedule_interval=None,  # Trigger manually or set a CRON schedule
    start_date=days_ago(1),
    catchup=False,
)

def run_pipeline():
    pipeline_script_path = "PortfolioOptimizer/pipeline/pipeline.py"  
    try:
        result = subprocess.run(
            ["python", pipeline_script_path],
            check=True,
            text=True,
            capture_output=True,
        )
        logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"Pipeline script failed: {e.stderr}")
        raise e


run_pipeline_task = PythonOperator(
    task_id="Task_ForecastingPipeline",
    python_callable=run_pipeline,
    dag=dag,
)


# Set task dependencies
run_pipeline_task
