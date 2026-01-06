select distinct
    account_id,
    -- In a real scenario, we would join with a separate customer table here.
    -- Since we only have one stream, we derive it.
    'Customer_' || account_id as customer_name
from {{ ref('transactions_snapshot') }}
where dbt_valid_to is null -- Get only the current active records