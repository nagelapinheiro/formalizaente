{{ config(location='data/gold/fct_solicitacoes.parquet') }}

-- GRÃO: uma linha representa uma solicitação sintética válida submetida ao FormalizaEnte.
-- Solicitações inválidas e duplicidades ficam fora deste grão e permanecem nas quarentenas.

select
    solicitacao_id,
    data_solicitacao,
    date_trunc('month', data_solicitacao)::date as mes_referencia,
    item_solicitado_original,
    item_normalizado,
    categoria,
    area_origem,
    responsavel,
    lote_ingestao,
    esfera_resolucao,
    case when esfera_resolucao = 'NAO_ENCONTRADO' then 0 else 1 end as indicador_atendida,
    existe_remume,
    existe_resme,
    existe_rename,
    (existe_remume + existe_resme + existe_rename) as quantidade_listas_encontradas,
    case when (existe_remume + existe_resme + existe_rename) > 1 then 1 else 0 end
        as indicador_ambiguidade
from {{ ref('int_classificacao_solicitacoes') }}

