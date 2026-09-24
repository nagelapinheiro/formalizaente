{{ config(location='data/gold/agg_cobertura_area.parquet') }}

-- Grão: uma linha por área de origem.

select
    area_origem,
    count(*) as total_solicitacoes,
    sum(indicador_atendida) as solicitacoes_atendidas,
    round(100.0 * sum(indicador_atendida) / nullif(count(*), 0), 2) as taxa_cobertura_pct
from {{ ref('fct_solicitacoes') }}
group by area_origem

