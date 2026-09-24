{{ config(materialized='table') }}

-- Registros inválidos da planilha de referência permanecem auditáveis.

select *
from {{ ref('int_areas_preparadas') }}
where motivo_invalidade is not null
