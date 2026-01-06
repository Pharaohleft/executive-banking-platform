FROM apache/airflow:2.7.1

USER root
RUN apt-get update && apt-get install -y git
USER airflow

# This installs the Snowflake tool correctly during the "Build" phase
RUN pip install apache-airflow-providers-snowflake apache-airflow-providers-amazon