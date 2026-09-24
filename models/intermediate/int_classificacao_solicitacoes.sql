{{ config(location='data/silver/int_classificacao_solicitacoes.parquet') }}

-- Regra de negócio central: quando um item aparece em mais de uma lista, a esfera
-- é escolhida pela menor prioridade definida no seed versionado `ref_listas`.
-- A política atual é Município (REMUME) > Estado (RESME) > União (RENAME).

with cobertura_lista as (
    select distinct
        listas.item_normalizado,
        listas.lista,
        listas.categoria_normalizada,
        referencia.esfera_resolucao,
        referencia.prioridade
    from {{ ref('int_listas_validas') }} as listas
    inner join {{ ref('ref_listas') }} as referencia using (lista)
),

cobertura as (
    select
        item_normalizado,
        max(case when lista = 'REMUME' then 1 else 0 end) as existe_remume,
        max(case when lista = 'RESME' then 1 else 0 end) as existe_resme,
        max(case when lista = 'RENAME' then 1 else 0 end) as existe_rename,
        min(categoria_normalizada) as categoria_referencia,
        arg_min(esfera_resolucao, prioridade) as esfera_resolucao
    from cobertura_lista
    group by item_normalizado
),

classified as (
    select
        solicitacoes.solicitacao_id,
        solicitacoes.data_solicitacao,
        solicitacoes.item_solicitado_original,
        solicitacoes.item_normalizado,
        case
            when solicitacoes.categoria_informada = 'NAO_INFORMADO'
                then coalesce(cobertura.categoria_referencia, 'NAO_INFORMADO')
            else solicitacoes.categoria_informada
        end as categoria,
        solicitacoes.area_origem,
        solicitacoes.responsavel,
        solicitacoes.lote_ingestao,
        coalesce(cobertura.existe_remume, 0) as existe_remume,
        coalesce(cobertura.existe_resme, 0) as existe_resme,
        coalesce(cobertura.existe_rename, 0) as existe_rename,
        coalesce(cobertura.esfera_resolucao, 'NAO_ENCONTRADO') as esfera_resolucao
    from {{ ref('int_solicitacoes_validas') }} as solicitacoes
    left join cobertura using (item_normalizado)
)

select * from classified
