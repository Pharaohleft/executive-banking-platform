#  Executive Banking Data Platform

An end-to-end data engineering pipeline that processes raw transaction data into an interactive executive dashboard.

##  Architecture
**Snowflake** (Data Warehouse) ➡️ **dbt** (Transformation & Testing) ➡️ **Streamlit** (Visualization)

##  Key Features
* **Medallion Architecture:** Raw data (Bronze) is cleaned and aggregated into Business-Ready tables (Gold).
* **Automated Data Quality:** Implemented `dbt test` to enforce unique keys, null checks, and valid transaction types.
* **Security:** Credentials managed via environment variables/secrets (no hardcoded passwords).
* **Business Intelligence:** Interactive dashboard tracking Real-time Transaction Volume and Credit/Debit splits.

##  Tech Stack
* **Language:** Python 3.10+, SQL
* **Transformation:** dbt (Data Build Tool)
* **Warehouse:** Snowflake
* **Frontend:** Streamlit

##  How to Run
1.  Clone the repo.
2.  Add your Snowflake credentials to `.streamlit/secrets.toml`.
3.  Run the pipeline: `dbt run`
4.  Launch the app: `streamlit run app.py`