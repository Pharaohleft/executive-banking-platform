#  Executive Banking Data Platform

An end-to-end data engineering pipeline that processes raw transaction data into an interactive executive dashboard.

##  Architecture
**Snowflake** (Data Warehouse) ➡️ **dbt** (Transformation & Testing) ➡️ **Streamlit** (Visualization)
<img width="3397" height="6964" alt="Untitled diagram-2026-01-07-054332" src="https://github.com/user-attachments/assets/50701288-08b4-4738-a5d9-e0af5944d675" />

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

5.  Snowflake worksheet link: https://app.snowflake.com/nikwdun/rbb38448/w1vInzBE1rNH#query
