{{ config(location='data/gold/dim_categoria.parquet') }}

-- Dimensão derivada das categorias efetivamente presentes nas solicitações válidas.

select distinct categoria
from {{ ref('int_classificacao_solicitacoes') }}

