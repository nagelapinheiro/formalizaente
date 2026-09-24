{{ config(location='data/silver/stg_areas_referencia.parquet') }}

-- Padroniza a planilha de áreas sem decidir ainda se o registro é utilizável.
-- A planilha é uma fonte independente (XLSX), usada para retirar do código a lista
-- rígida de áreas válidas e tornar a validação rastreável na DAG.

select
    cast(source_row_number as integer) as source_row_number,
    area_origem as area_origem_original,
    nullif({{ normalize_text('area_origem') }}, '') as area_origem,
    descricao,
    nullif({{ normalize_text('ativa') }}, '') as ativa,
    _source_file,
    try_cast(_ingested_at_utc as timestamp) as ingested_at_utc
from {{ source('bronze', 'areas_referencia') }}
