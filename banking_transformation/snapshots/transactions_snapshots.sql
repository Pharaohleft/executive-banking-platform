{% snapshot transactions_snapshot %}

{{
    config(
      target_database='BANKING_DB',
      target_schema='SILVER',
      unique_key='transaction_id',

      strategy='check',
      check_cols=['amount', 'operation']
    )
}}

select * from {{ ref('stg_transactions') }}

{% endsnapshot %}