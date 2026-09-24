{{ config(location='data/silver/int_listas_validas.parquet') }}

-- Somente itens estruturalmente válidos participam do cruzamento normativo.

select
    lista,
    codigo,
    item_original,
    item_normalizado,
    categoria_normalizada
from {{ ref('int_listas_preparadas') }}
where motivo_invalidade is null

