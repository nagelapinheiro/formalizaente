{{ config(location='data/silver/int_solicitacoes_preparadas.parquet') }}

-- Valida estrutura e identifica IDs repetidos. A validade da área não fica
-- hardcoded: ela é verificada contra a fonte XLSX de áreas ativas.

with ranked as (
    select
        *,
        row_number() over (
            partition by solicitacao_id
            order by source_row_number
        ) as occurrence_number
    from {{ ref('stg_solicitacoes') }}
),

areas_validas as (
    select area_origem
    from {{ ref('int_areas_validas') }}
),

classified as (
    select
        ranked.*,
        case
            when solicitacao_id is null then 'ID_AUSENTE'
            when data_solicitacao is null then 'DATA_INVALIDA_OU_AUSENTE'
            when item_normalizado is null then 'ITEM_AUSENTE'
            when not exists (
                select 1
                from areas_validas
                where areas_validas.area_origem = ranked.area_origem
            ) then 'AREA_INVALIDA'
            when responsavel is null then 'RESPONSAVEL_AUSENTE'
            when occurrence_number > 1 then 'ID_DUPLICADO'
            else null
        end as motivo_invalidade
    from ranked
)

select * from classified
