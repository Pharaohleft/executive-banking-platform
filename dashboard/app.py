import streamlit as st
import snowflake.connector
import pandas as pd

# Page Config
st.set_page_config(page_title="Executive Banking Dashboard", layout="wide")

# Connect to Snowflake
@st.cache_resource
def init_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"]
    )

conn = init_connection()

# Title
st.title(" Executive Banking Dashboard")
st.markdown("Real-time view of transaction processing and customer activity.")

# Fetch Data (Using your clean Gold tables!)
query = """
    SELECT 
        t.transaction_date,
        t.amount,
        t.operation,
        c.customer_name
    FROM fact_transactions t
    JOIN dim_customers c ON t.account_id = c.account_id
    ORDER BY t.transaction_date DESC
"""
df = pd.read_sql(query, conn)

# 1. KPI Section (The "Business Value")
col1, col2, col3 = st.columns(3)

with col1:
    total_vol = df['AMOUNT'].sum()
    st.metric(label=" Total Transaction Volume", value=f"${total_vol:,.2f}")

with col2:
    tx_count = df.shape[0]
    st.metric(label=" Total Transactions", value=tx_count)

with col3:
    # Calculate simple Credit vs Debit ratio
    credit_only = df[df['OPERATION'] == 'credit']['AMOUNT'].sum()
    st.metric(label=" Credit Volume", value=f"${credit_only:,.2f}")

st.divider()

# 2. Charts Section
st.subheader("Transaction Trends")
# Aggregate by date for the chart
daily_data = df.groupby('TRANSACTION_DATE')['AMOUNT'].sum()
st.bar_chart(daily_data)

# 3. Raw Data Section
st.subheader("Detailed Transaction Log")
st.dataframe(df.head(100), use_container_width=True)