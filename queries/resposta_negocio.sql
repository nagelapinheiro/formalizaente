-- RESPOSTA FINAL.
-- Lê exclusivamente a camada Gold. Não calcula métrica, não classifica registros,
-- não contém WHERE e não acessa Raw/Bronze/Silver.

select
    tipo_recorte,
    recorte,
    total_solicitacoes,
    solicitacoes_atendidas,
    taxa_cobertura_pct,
    taxa_ambiguidade_pct,
    percentual_distribuicao_pct
from gold.agg_resposta_gerencial
order by ordem_exibicao, recorte;
