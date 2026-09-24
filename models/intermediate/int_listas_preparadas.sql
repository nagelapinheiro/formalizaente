{{ config(location='data/silver/int_listas_preparadas.parquet') }}

-- Identifica defeitos estruturais e duplicidades antes de liberar registros para comparação.

with ranked as (
    select
        *,
        row_number() over (
            partition by lista, item_normalizado
            order by source_row_number
        ) as occurrence_number
    from {{ ref('stg_listas_normativas') }}
),

classified as (
    select
        *,
        case
            when lista is null then 'LISTA_AUSENTE'
            when lista not in ('REMUME', 'RESME', 'RENAME') then 'LISTA_INVALIDA'
            when codigo is null then 'CODIGO_AUSENTE'
            when item_normalizado is null then 'ITEM_AUSENTE'
            when categoria_normalizada is null then 'CATEGORIA_AUSENTE'
            when occurrence_number > 1 then 'DUPLICIDADE_LISTA_ITEM'
            else null
        end as motivo_invalidade
    from ranked
)

select * from classified

