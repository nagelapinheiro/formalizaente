{{ config(location='data/gold/agg_resposta_gerencial.parquet') }}

-- GRÃO: uma linha por recorte analítico da resposta gerencial.
-- Este mart consolida somente métricas já calculadas em outros modelos Gold.
-- A consulta final pode fazer SELECT direto, sem cálculo ou filtro de negócio.

with geral as (
    select
        1 as ordem_exibicao,
        'GERAL' as tipo_recorte,
        indicador as recorte,
        total_solicitacoes_validas as total_solicitacoes,
        solicitacoes_atendidas,
        taxa_cobertura_pct,
        taxa_ambiguidade_pct,
        cast(null as double) as percentual_distribuicao_pct
    from {{ ref('agg_cobertura_geral') }}
),

esfera as (
    select
        2 as ordem_exibicao,
        'ESFERA' as tipo_recorte,
        esfera_resolucao as recorte,
        total_solicitacoes,
        cast(null as hugeint) as solicitacoes_atendidas,
        cast(null as double) as taxa_cobertura_pct,
        cast(null as double) as taxa_ambiguidade_pct,
        percentual_solicitacoes as percentual_distribuicao_pct
    from {{ ref('agg_distribuicao_esfera') }}
),

periodo as (
    select
        3 as ordem_exibicao,
        'PERIODO' as tipo_recorte,
        cast(mes_referencia as varchar) as recorte,
        total_solicitacoes,
        solicitacoes_atendidas,
        taxa_cobertura_pct,
        cast(null as double) as taxa_ambiguidade_pct,
        cast(null as double) as percentual_distribuicao_pct
    from {{ ref('agg_cobertura_mensal') }}
),

categoria as (
    select
        4 as ordem_exibicao,
        'CATEGORIA' as tipo_recorte,
        categoria as recorte,
        total_solicitacoes,
        solicitacoes_atendidas,
        taxa_cobertura_pct,
        cast(null as double) as taxa_ambiguidade_pct,
        cast(null as double) as percentual_distribuicao_pct
    from {{ ref('agg_cobertura_categoria') }}
),

area as (
    select
        5 as ordem_exibicao,
        'AREA' as tipo_recorte,
        area_origem as recorte,
        total_solicitacoes,
        solicitacoes_atendidas,
        taxa_cobertura_pct,
        cast(null as double) as taxa_ambiguidade_pct,
        cast(null as double) as percentual_distribuicao_pct
    from {{ ref('agg_cobertura_area') }}
),

unificado as (
    select * from geral
    union all
    select * from esfera
    union all
    select * from periodo
    union all
    select * from categoria
    union all
    select * from area
)

select
    concat(tipo_recorte, ':', recorte) as chave_recorte,
    ordem_exibicao,
    tipo_recorte,
    recorte,
    total_solicitacoes,
    solicitacoes_atendidas,
    taxa_cobertura_pct,
    taxa_ambiguidade_pct,
    percentual_distribuicao_pct
from unificado
