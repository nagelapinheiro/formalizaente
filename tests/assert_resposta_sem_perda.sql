-- A linha GERAL da resposta executiva deve reconciliar com a fato principal.
select 1 as erro
where (
    select total_solicitacoes
    from {{ ref('agg_resposta_gerencial') }}
    where tipo_recorte = 'GERAL'
) != (
    select count(*)
    from {{ ref('fct_solicitacoes') }}
)
