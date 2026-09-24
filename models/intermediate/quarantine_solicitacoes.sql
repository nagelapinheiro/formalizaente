{{ config(materialized='table') }}

-- Destino explícito dos registros inválidos, preservando origem e motivo.

select *
from {{ ref('int_solicitacoes_preparadas') }}
where motivo_invalidade is not null

