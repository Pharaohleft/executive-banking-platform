 {% macro decode_debezium_decimal(column_name) %}
    /* Decodes Debezium 'Variable Scale Decimal' format.
       1. Decodes Base64 string to Binary.
       2. Converts Binary to Hex.
       3. Converts Hex to Integer.
       4. Divides by the Scale to get the final decimal.
    */
    (
        TO_NUMBER(
            HEX_ENCODE(BASE64_DECODE_BINARY({{ column_name }}:value::STRING)), 
            'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' -- Mask for large integers
        ) 
        / 
        POWER(10, {{ column_name }}:scale::INT)
    )::FLOAT
{% endmacro %}