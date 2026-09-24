# Entrega — FormalizaEnte

Esta versão reorganiza o storage para seguir o padrão físico Medallion usado na PoC da professora:

```text
data/
├── raw
├── bronze
├── silver
└── gold
```

## Como rodar

```bash
python -m pip install -r requirements.txt
python -m src.pipeline
dbt build
python -m src.answer
python -m src.time_travel
```

## Dashboard

Abra:

```text
notebooks/dashboard_formalizaente.ipynb
```

Antes do notebook, execute:

```bash
python -m src.pipeline
dbt build
```

## Slides

Arquivo principal:

```text
slides/FormalizaEnte_Apresentacao_Completa.pptx
```

Os slides incluem: pergunta de negócio, arquitetura Medallion, fontes, erros propositais, ingestão, tratamento, quarentena, ambiguidade, Gold, resultado e dashboard.
