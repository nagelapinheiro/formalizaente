{{ config(location='data/silver/int_areas_preparadas.parquet') }}

-- Valida a referência organizacional e identifica duplicidades antes de usá-la
-- como domínio de áreas aceitas nas solicitações.

with ranked as (
    select
        *,
        row_number() over (
            partition by area_origem
            order by source_row_number
        ) as occurrence_number
    from {{ ref('stg_areas_referencia') }}
),

classified as (
    select
        *,
        case
            when area_origem is null then 'AREA_AUSENTE'
            when ativa not in ('SIM', 'NAO') then 'STATUS_ATIVA_INVALIDO'
            when occurrence_number > 1 then 'AREA_DUPLICADA'
            else null
        end as motivo_invalidade
    from ranked
)

select * from classified
