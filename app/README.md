# Dashboard Streamlit — FormalizaEnte

Este dashboard é uma camada visual de consumo. Ele lê somente modelos Gold gerados pelo dbt.

## Como executar

Na raiz do projeto:

```bash
python -m src.pipeline
dbt build
streamlit run app/dashboard.py
```

## Regra importante para a avaliação

O dashboard não deve conter regra de negócio. Por isso:

- não consulta Raw, Bronze ou Silver;
- não classifica esfera;
- não recalcula taxa de cobertura ou taxa de ambiguidade;
- não decide prioridade entre REMUME, RESME e RENAME;
- apenas exibe modelos Gold como `agg_cobertura_geral`, `agg_cobertura_mensal`, `agg_cobertura_area`, `agg_cobertura_categoria`, `agg_distribuicao_esfera` e `agg_resposta_gerencial`.
