-- Os defeitos intencionais devem permanecer demonstráveis na entrega.

select 1 as erro
where (select count(*) from {{ ref('quarantine_solicitacoes') }}) = 0

