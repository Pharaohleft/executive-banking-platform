SELECT
    t.transaction_id,
    t.account_id,
    t.created_at as transaction_date,   -- <--- FIX: Map created_at to transaction_date
    t.amount,
    CASE 
        WHEN t.operation = 'c' THEN 'credit'
        WHEN t.operation = 'd' THEN 'debit'
        ELSE t.operation 
    END AS operation
FROM {{ ref('stg_transactions') }} t