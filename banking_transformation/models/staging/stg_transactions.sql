with raw_source as (
    
    select * from {{ source('banking_source', 'transactions') }}

),

final as (

    select
        -- Extract ID from the 'after' nesting
        raw_data:after:id::INT as transaction_id,
        
        -- Extract Account ID
        raw_data:after:account_id::INT as account_id,
        
        -- USE OUR CUSTOM MACRO HERE to decode the amount
        {{ decode_debezium_decimal('raw_data:after:amount') }} as amount,
        
        -- Convert microsecond timestamp to regular timestamp
        TO_TIMESTAMP(raw_data:after:created_at::INT / 1000000) as created_at,
        
        -- Metadata
        raw_data:op::STRING as operation,
        raw_data:source:table::STRING as source_table

    from raw_source
    -- Only keep valid rows (not deletes or nulls)
    where raw_data:after:id is not null

)

select * from final