# Roteiro de apresentação — 20 minutos

## 0–4 min — pergunta de negócio e fontes

Pergunta:

> Qual é a taxa de cobertura das solicitações pelo FormalizaEnte, em qual esfera — Município, Estado ou União — elas são resolvidas e como essa cobertura varia por período, categoria e área de origem?

Fontes sintéticas:

- `data/raw/solicitacoes.csv` — pedidos que serão avaliados;
- `data/raw/listas_normativas.json` — amostras de REMUME, RESME e RENAME;
- `data/raw/areas_referencia.xlsx` — domínio de áreas.

Erros propositais colocados nos dados:

- diferenças de caixa e espaços extras;
- acentuação inconsistente;
- datas inválidas;
- identificadores ausentes e duplicados;
- item, área ou responsável ausentes/inválidos;
- lista normativa incompleta;
- área inativa e área duplicada.

## 4–12 min — demo do pipeline e das camadas

Mostrar a estrutura física do storage:

```text
data/
├── raw
├── bronze
├── silver
└── gold
```

Executar:

```bash
python -m src.pipeline
```

Explicar:

- `data/raw` é preservado;
- `data/bronze` recebe Delta Lake;
- solicitações possuem pelo menos duas versões Delta;
- a ingestão não limpa, não deduplica e não classifica.

Em seguida executar:

```bash
dbt build
```

Mostrar:

- `data/silver` recebe modelos de tratamento em Parquet;
- `data/gold` recebe fatos, dimensões e agregados em Parquet;
- o DuckDB continua sendo o engine/catálogo analítico.

## 12–16 min — DAG, time travel do Delta e decisões obrigatórias

Explicar o tratamento:

1. Staging normaliza textos, remove espaços, padroniza caixa e tipa datas com `try_cast`;
2. Intermediate valida registros, identifica duplicidades e manda defeitos para quarentena;
3. A comparação com REMUME, RESME e RENAME ocorre apenas depois da validação;
4. A ambiguidade é preservada e resolvida por prioridade versionada em `seeds/ref_listas.csv`;
5. A Gold calcula indicadores e recortes prontos para consumo.

Mostrar obrigatoriamente, porque é exigência explícita do professor:

```bash
dbt docs generate
dbt docs serve
python -m src.time_travel
```

Na DAG do dbt, apontar a linhagem:

```text
source(Bronze) → staging → intermediate/quarantine → marts Gold → resposta gerencial
```

No time travel do Delta, explicar:

- versão 0: primeira carga sintética;
- versão 1: segunda carga com histórico preservado;
- a mesma leitura pode ser feita na versão atual e na anterior;
- isso prova rastreabilidade e reprocessamento a partir da preservação do bruto.

Duas decisões do `DECISOES.md` para comentar em sala:

1. **Arquitetura Medallion adaptada** — Raw preserva, Bronze versiona em Delta, Silver trata e Gold responde.
2. **Destino dos inválidos** — registros inválidos vão para quarentena, não são descartados nem corrigidos silenciosamente.

Decisão extra, se der tempo:

- **Ambiguidade REMUME/RESME/RENAME** — a prioridade REMUME → RESME → RENAME fica versionada em `seeds/ref_listas.csv`, não escondida no dashboard.

## 16–20 min — resposta gerencial e dashboard

Executar:

```bash
python -m src.answer
```

Mostrar `queries/resposta_negocio.sql`:

- lê somente `gold.agg_resposta_gerencial`;
- não calcula taxa;
- não classifica esfera;
- não deduplica;
- não acessa Raw, Bronze ou Silver.

Número principal:

- **65 solicitações válidas**;
- **56 cobertas**;
- **9 não encontradas**;
- **86,15% de cobertura**;
- **11 ambíguas**;
- **16,92% de ambiguidade**.

Encerrar com o dashboard Jupyter em `notebooks/dashboard_formalizaente.ipynb`. Se usar o Streamlit, destacar que ele lê agregados Gold prontos e não recalcula regra de negócio.
