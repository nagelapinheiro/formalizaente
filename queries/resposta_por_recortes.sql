-- Recortes pedidos pelo enunciado: período, categoria e área.
-- Os agregados e as métricas já foram calculados na camada Gold.

select
    'PERIODO' as tipo_recorte,
    cast(mes_referencia as varchar) as recorte,
    total_solicitacoes,
    solicitacoes_atendidas,
    taxa_cobertura_pct
from gold.agg_cobertura_mensal

union all

select
    'CATEGORIA' as tipo_recorte,
    categoria as recorte,
    total_solicitacoes,
    solicitacoes_atendidas,
    taxa_cobertura_pct
from gold.agg_cobertura_categoria

union all

select
    'AREA' as tipo_recorte,
    area_origem as recorte,
    total_solicitacoes,
    solicitacoes_atendidas,
    taxa_cobertura_pct
from gold.agg_cobertura_area

order by tipo_recorte, recorte;

