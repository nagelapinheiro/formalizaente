{{ config(location='data/silver/stg_solicitacoes.parquet') }}

-- Limpa e tipa as solicitações, mantendo os campos originais para auditoria.
-- try_cast evita interromper o pipeline quando uma data inválida é recebida;
-- o destino desse registro é decidido explicitamente na camada intermediária.

select
    cast(source_row_number as integer) as source_row_number,
    nullif(trim(solicitacao_id), '') as solicitacao_id,
    data_solicitacao as data_solicitacao_original,
    try_cast(data_solicitacao as date) as data_solicitacao,
    item_solicitado as item_solicitado_original,
    nullif({{ normalize_text('item_solicitado') }}, '') as item_normalizado,
    coalesce(nullif({{ normalize_text('categoria_informada') }}, ''), 'NAO_INFORMADO')
        as categoria_informada,
    nullif({{ normalize_text('area_origem') }}, '') as area_origem,
    nullif({{ normalize_text('responsavel') }}, '') as responsavel,
    nullif(trim(lote_ingestao), '') as lote_ingestao,
    _source_file,
    try_cast(_ingested_at_utc as timestamp) as ingested_at_utc
from {{ source('bronze', 'solicitacoes') }}
