-- A planilha contém defeitos intencionais; a demonstração deve manter evidência deles.
select 1 as erro
where (select count(*) from {{ ref('quarantine_areas_referencia') }}) = 0
