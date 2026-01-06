import os
import boto3
import snowflake.connector
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Config
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET = 'banking-data'
LOCAL_DIR = os.getenv("MINIO_LOCAL_DIR", "/tmp/minio_downloads")

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
SNOWFLAKE_DB = os.getenv("SNOWFLAKE_DB", "BANKING_DB")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "BRONZE")

# EXACT table name we created in Snowflake
TABLES = ["TRANSACTIONS"]

def download_from_minio():
    """Task 1: Downloads files from MinIO to local Airflow temp folder"""
    os.makedirs(LOCAL_DIR, exist_ok=True)
    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY
    )
    
    local_files = {}
    for table in TABLES:
        # Assuming files are in the bucket root or a folder named after the table
        # We list the whole bucket to be safe based on your previous success
        resp = s3.list_objects_v2(Bucket=BUCKET)
        objects = resp.get("Contents", [])
        
        local_files[table] = []
        if not objects:
            print(f"No objects found in bucket {BUCKET}")
        
        for obj in objects:
            key = obj["Key"]
            # Filter for .json files if your source is JSON
            if key.endswith(".json"):
                local_file = os.path.join(LOCAL_DIR, os.path.basename(key))
                s3.download_file(BUCKET, key, local_file)
                print(f"Downloaded {key} -> {local_file}")
                local_files[table].append(local_file)
    
    return local_files

def load_to_snowflake(**kwargs):
    """Task 2: Uploads from local temp folder to Snowflake Table"""
    local_files = kwargs["ti"].xcom_pull(task_ids="download_minio")
    if not local_files:
        print("No files received from Task 1.")
        return

    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DB,
        schema=SNOWFLAKE_SCHEMA
    )
    cur = conn.cursor()

    for table, files in local_files.items():
        if not files:
            print(f"No files to load for {table}")
            continue

        # 1. Upload to the Named Stage we created
        for f in files:
            # PUT file://... @MINIO_STAGE
            put_cmd = f"PUT file://{f} @MINIO_STAGE AUTO_COMPRESS=FALSE"
            print(f"Running: {put_cmd}")
            cur.execute(put_cmd)

        # 2. Copy into the Table using the logic that worked manually
        # This uses the (raw_data) column and the $1 selector for JSON
        copy_sql = f"""
        COPY INTO {table} (raw_data)
        FROM (SELECT $1 FROM @MINIO_STAGE)
        FILE_FORMAT = (TYPE = 'JSON')
        ON_ERROR = 'CONTINUE';
        """
        print(f"Running COPY for {table}")
        cur.execute(copy_sql)

    cur.close()
    conn.close()

# DAG Definition
default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="banking_minio_to_snowflake_final",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    task1 = PythonOperator(
        task_id="download_minio",
        python_callable=download_from_minio,
    )

    task2 = PythonOperator(
        task_id="load_snowflake",
        python_callable=load_to_snowflake,
        provide_context=True,
    )

    task1 >> task2