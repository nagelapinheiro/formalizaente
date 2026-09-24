{{ config(location='data/silver/stg_listas_normativas.parquet') }}

-- Limpa e tipa a amostra normativa sem decidir o ente responsável.
-- A normalização elimina diferenças de caixa, acentuação e espaços que impediriam
-- uma comparação determinística entre fontes equivalentes.

select
    cast(source_row_number as integer) as source_row_number,
    nullif({{ normalize_text('lista') }}, '') as lista,
    nullif({{ normalize_text('codigo') }}, '') as codigo,
    item as item_original,
    nullif({{ normalize_text('item') }}, '') as item_normalizado,
    nullif({{ normalize_text('categoria') }}, '') as categoria_normalizada,
    fonte_declarada,
    _source_file,
    try_cast(_ingested_at_utc as timestamp) as ingested_at_utc
from {{ source('bronze', 'listas_normativas') }}
