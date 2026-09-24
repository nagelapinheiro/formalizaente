-- A distribuição percentual por esfera deve fechar em 100% (salvo tolerância de arredondamento).
with total as (
    select round(sum(percentual_solicitacoes), 2) as percentual_total
    from {{ ref('agg_distribuicao_esfera') }}
)
select *
from total
where abs(percentual_total - 100.00) > 0.02
