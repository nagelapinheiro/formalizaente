{{ config(location='data/silver/int_areas_validas.parquet') }}

-- Somente áreas estruturalmente válidas e ativas podem validar solicitações.

select
    area_origem,
    descricao
from {{ ref('int_areas_preparadas') }}
where motivo_invalidade is null
  and ativa = 'SIM'
