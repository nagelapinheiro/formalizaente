-- O teste falha se qualquer taxa Gold sair do intervalo matematicamente possível.

select *
from {{ ref('agg_cobertura_geral') }}
where taxa_cobertura_pct not between 0 and 100
   or taxa_ambiguidade_pct not between 0 and 100

