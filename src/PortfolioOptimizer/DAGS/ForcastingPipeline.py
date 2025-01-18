from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import subprocess
import os
from datetime import timedelta
from PortfolioOptimizer.logging import logger

current_dir = os.path.dirname(os.path.abspath(__file__))

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def run_pipeline(**context):
    """
    Execute the forecasting pipeline script with proper path handling and error logging.
    
    Args:
        **context: Airflow context variables
    """
    pipeline_script_path = os.path.join(current_dir, "..", "pipeline", "pipeline.py")
    abs_script_path = os.path.abspath(pipeline_script_path)
    
    logger.info(f"Starting pipeline execution")
    logger.info(f"Pipeline script path: {abs_script_path}")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    try:
        if not os.path.exists(abs_script_path):
            raise FileNotFoundError(f"Pipeline script not found at: {abs_script_path}")
        
        result = subprocess.run(
            ["python", abs_script_path],
            check=True,
            text=True,
            capture_output=True,
        )
        
        logger.info("Pipeline execution completed successfully")
        logger.info("Pipeline output:")
        logger.info(result.stdout)
        
        return {
            "status": "success",
            "output": result.stdout
        }
        
    except FileNotFoundError as e:
        error_msg = f"Pipeline script not found: {str(e)}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
        
    except subprocess.CalledProcessError as e:
        error_msg = (
            f"Pipeline execution failed with exit code {e.returncode}\n"
            f"Error output: {e.stderr}\n"
            f"Standard output: {e.stdout}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during pipeline execution: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)

dag = DAG(
    dag_id="ForecastingPipeline",
    default_args=default_args,
    description="Run the Forecasting Pipeline with improved error handling and path resolution.",
    schedule_interval=None,  
    start_date=days_ago(1),
    catchup=False,
    tags=['forecasting', 'crypto', 'portfolio'],
)

run_pipeline_task = PythonOperator(
    task_id="Task_ForecastingPipeline",
    python_callable=run_pipeline,
    provide_context=True,
    dag=dag,
)

run_pipeline_task