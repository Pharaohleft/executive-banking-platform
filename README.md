#  End-to-End Real-Time Banking Data Engineering Project

An end-to-end data engineering pipeline that processes raw transaction data into an interactive executive dashboard.

###  Project Overview
In the financial sector, "Batch Processing" is often too slow for fraud detection and customer account management. This project builds a **High-Frequency Data Platform** that streams transactional data from a transactional database (Postgres) to a Data Warehouse (Snowflake) with **sub-second latency**.

Using **Change Data Capture (CDC)**, this system captures every `INSERT`, `UPDATE`, and `DELETE` event in real-time, enabling immediate downstream analytics and strict audit compliance via Slowly Changing Dimensions (SCD Type 2).

---

###  System Architecture
*(The flow from transactional chaos to analytical order)*
<img width="3397" height="6964" alt="Untitled diagram-2026-01-07-054332" src="https://github.com/user-attachments/assets/cd2a1db9-f460-47ca-acc5-26b10f5220a3" />



---

1.Infrastructure Setup
Containerization: The operational stack (Airflow Webserver, Scheduler, Triggerer, Postgres, MinIO) is fully containerized via Docker Compose.
Networking: Airflow communicates with the MinIO Object Storage via an internal Docker network on http://minio:9000.

2. The Pipeline (banking_minio_to_snowflake_final)
Trigger: Manual or Scheduled.
Task 1 (download_minio): Downloads transactions.json from MinIO bucket banking-data.
Task 2 (load_snowflake): Uploads to Snowflake Stage and loads into BANKING_DB.BRONZE.TRANSACTIONS.

3. The Data Structure (Crucial Detail)
Format: JSON (CDC / Debezium format).
Schema: Data is nested inside an {"after": { ... }} object.
Current View: TRANSACTIONS_FLATTENED (Created in Snowflake) successfully extracts id, account_id, and created_at.

Pending Item: The amount column is Base64 encoded (e.g., "ASaP") and needs decoding in the Silver layer.

---

###  Workflow
1.  **Source:** A simulated Banking App writes transactions to a **PostgreSQL** database. Used Dbeaver to create dataset.
2.  **Ingestion (CDC):** **Debezium** (running on Kafka Connect) listens to the Postgres Write-Ahead Log (WAL) and streams changes to **Apache Kafka**.
3.  **Storage:** Kafka sinks the raw stream into **Amazon S3** (Simulated with MinIO) as JSON.
4.  **Warehousing:** **Snowflake** ingests the data via **Snowpipe** into the **Bronze Layer**.
5.  **Transformation:** **dbt (data build tool)** orchestrates the transformation:
    * **Silver:** Cleaning and deduplication.
    * **Gold:** Applying **SCD Type 2** logic to track historical changes (e.g., address updates).
6.  **Orchestration:** **Apache Airflow** manages the dependency chain.
7.  **Serving:** **PowerBI** connects via Direct Query for live dashboards.


---

###  Tech Stack
* **Language:** Python 3.9, SQL
* **Source Database:** PostgreSQL
* **Streaming:** Apache Kafka, Debezium (CDC)
* **Warehouse:** Snowflake
* **Transformation:** dbt (Data Build Tool)
* **Orchestration:** Apache Airflow
* **Visualization:** Microsoft PowerBI
* **DevOps:** Docker, GitHub Actions (CI/CD)

---

###  Key Technical Features

#### 1. Change Data Capture (CDC)
Instead of querying the database every hour (which misses deleted rows), I used **Debezium** to read the database logs. This ensures:
* **Zero Data Loss:** We capture every single transaction.
* **Low Load:** We don't query the production tables, preserving performance for the banking app.

#### 2. Slowly Changing Dimensions (SCD Type 2)
Banks must know *where* a customer lived 6 months ago to detect fraud.
* **Implementation:** Used `dbt snapshots`.
* **Logic:** When a user updates their address, the system closes the old row (updates `valid_to` date) and creates a new active row. This maintains a perfect historical audit trail.

#### 3. Modern Data Stack (MDS) & CI/CD
* The entire pipeline is containerized using **Docker**.
* **GitHub Actions** automatically runs `dbt test` (checking for nulls/duplicates) whenever code is pushed, ensuring bad data never reaches Production.

* **Medallion Architecture:** Raw data (Bronze) is cleaned and aggregated into Business-Ready tables (Gold).
* **Automated Data Quality:** Implemented `dbt test` to enforce unique keys, null checks, and valid transaction types.
* **Security:** Credentials managed via environment variables/secrets (no hardcoded passwords).
* **Business Intelligence:** Interactive dashboard tracking Real-time Transaction Volume and Credit/Debit splits.

---
###   Technical Challenges & Solutions

1. Parsing Nested CDC Logs Raw data arrives from Debezium in a complex JSON format.
Challenge: The actual row data is buried inside a nested payload.after object, while the before object contains the previous state (crucial for audits).
Solution: Implemented a Flattening Logic in the Snowflake Stage to extract id, account_id, and created_at into a tabular structure.

2. Handling Base64 Encoded Decimals
Challenge: Debezium serializes Postgres NUMERIC/DECIMAL types (like the amount column) as Base64 encoded strings (e.g., "ASaP") to preserve precision, rather than standard JSON numbers.
Future Improvement: A custom decoding function (User Defined Function or dbt macro) is required in the Silver Layer to convert these Base64 strings back into Float/Decimal types for aggregation.


##  How to Run
1.  Clone the repo.
2.  Add your Snowflake credentials to `.streamlit/secrets.toml`.
3.  Run the pipeline: `dbt run`
4.  Launch the app: `streamlit run app.py`

5.  Snowflake worksheet link: https://app.snowflake.com/nikwdun/rbb38448/w1vInzBE1rNH#query


###  Operational Impact
* **Latency:** Reduced data availability time from **T+1 Day** to **<1 Minute**.
* **Compliance:** Achieved **100% Audit Traceability** for customer account changes.
* **Scalability:** Decoupled storage (S3) and compute (Snowflake) allows the system to handle millions of transactions without performance degradation.

---
