{{ config(location='data/gold/agg_cobertura_geral.parquet') }}

-- Grão: uma linha para o conjunto completo de solicitações válidas.

select
    'GERAL' as indicador,
    count(*) as total_solicitacoes_validas,
    sum(indicador_atendida) as solicitacoes_atendidas,
    count(*) - sum(indicador_atendida) as solicitacoes_nao_encontradas,
    round(100.0 * sum(indicador_atendida) / nullif(count(*), 0), 2) as taxa_cobertura_pct,
    sum(indicador_ambiguidade) as solicitacoes_com_ambiguidade,
    round(100.0 * sum(indicador_ambiguidade) / nullif(count(*), 0), 2)
        as taxa_ambiguidade_pct
from {{ ref('fct_solicitacoes') }}

