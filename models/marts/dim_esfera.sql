{{ config(location='data/gold/dim_esfera.parquet') }}

-- Dimensão derivada da regra versionada em seed, mais o estado de não cobertura.

select
    esfera_resolucao,
    prioridade as ordem_prioridade,
    descricao
from {{ ref('ref_listas') }}

union all

select
    'NAO_ENCONTRADO' as esfera_resolucao,
    4 as ordem_prioridade,
    'Não encontrado nas amostras' as descricao
