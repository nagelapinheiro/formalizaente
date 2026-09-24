{{ config(location='data/silver/int_solicitacoes_validas.parquet') }}

-- Conjunto válido que alimenta a classificação. Nenhuma linha inválida é apagada:
-- sua cópia auditável permanece em quarantine_solicitacoes.

select
    solicitacao_id,
    data_solicitacao,
    item_solicitado_original,
    item_normalizado,
    categoria_informada,
    area_origem,
    responsavel,
    lote_ingestao
from {{ ref('int_solicitacoes_preparadas') }}
where motivo_invalidade is null

