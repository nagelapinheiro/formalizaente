{{ config(location='data/gold/agg_distribuicao_esfera.parquet') }}

-- Grão: uma linha por esfera já classificada na camada intermediária.

select
    esfera_resolucao,
    count(*) as total_solicitacoes,
    round(100.0 * count(*) / sum(count(*)) over (), 2) as percentual_solicitacoes
from {{ ref('fct_solicitacoes') }}
group by esfera_resolucao

