{{ config(materialized='table') }}

-- Quarentena preserva o registro e o motivo; nada é descartado silenciosamente.

select *
from {{ ref('int_listas_preparadas') }}
where motivo_invalidade is not null

