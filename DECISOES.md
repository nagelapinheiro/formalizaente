# DECISOES.md — decisões de arquitetura e modelagem

## Contexto

A PoC aplica a jornada **fontes → ingestão → preservação do bruto → transformação → consumo →
resposta** ao domínio sintético do FormalizaEnte. O objetivo é produzir uma resposta gerencial
reproduzível, sem afirmar cobertura oficial das listas do SUS.

## 1. Arquitetura de armazenamento

Foi escolhida a arquitetura **Raw → Bronze → Silver → Gold**.

- **Raw:** arquivos imutáveis em CSV, JSON e XLSX.
- **Bronze:** Delta Lake em `data/bronze`, preservando defeitos e adicionando apenas metadados técnicos de ingestão.
- **Silver:** dbt materializado em Parquet em `data/silver`, para limpeza, tipagem, validação, deduplicação, quarentena e classificação.
- **Gold:** dbt materializado em Parquet em `data/gold`, com fato, dimensões e agregados orientados à pergunta.
- **Resposta:** um mart final, `agg_resposta_gerencial`, consolida somente métricas já prontas.

A Bronze também é exposta no DuckDB como views e declarada em `models/sources.yml`. Isso permite
que a DAG do dbt mostre explicitamente os nós de origem Bronze, sem fazer o dbt depender de acesso
direto ao log Delta. O storage visível segue o padrão Medallion: `data/raw` → `data/bronze` → `data/silver` → `data/gold`.

O Delta fica na Bronze porque o time travel é mais útil antes de qualquer transformação: é
possível demonstrar exatamente qual conjunto foi capturado em cada lote.

## 2. Grão

O grão principal de `gold.fct_solicitacoes` é:

> **Uma linha representa uma solicitação sintética válida submetida ao FormalizaEnte.**

Ficam fora desse grão registros sem identificador, com data inválida, sem item, com área inválida,
sem responsável ou duplicados. Eles não são descartados: permanecem em
`silver.quarantine_solicitacoes`.

Foi escolhida uma **tabela larga** como modelo principal porque o volume é pequeno, os atributos
analíticos são poucos e a pergunta pede cruzamentos simples. Dimensões de domínio são mantidas
quando ajudam integridade e documentação.

O mart `gold.agg_resposta_gerencial` possui outro grão, declarado no topo do SQL:

> **Uma linha por recorte analítico da resposta gerencial.**

Ele existe para que a consulta final não precise recalcular métricas.

## 3. Dado ambíguo que exigiu escolha

Um medicamento pode aparecer simultaneamente em REMUME, RESME e RENAME. A PoC precisa escolher
uma esfera para produzir uma resposta única.

A política aplicada é:

1. REMUME → `MUNICIPIO`;
2. RESME → `ESTADO`;
3. RENAME → `UNIAO`;
4. nenhuma correspondência → `NAO_ENCONTRADO`.

A diferença da V4 é que a prioridade não fica mais espalhada em um `CASE`. Ela está versionada em
`seeds/ref_listas.csv` e é consumida pelo dbt. O código também preserva indicadores de presença em
cada lista e calcula a ambiguidade, portanto a escolha da esfera não apaga as demais ocorrências.

Em produção, essa política deve ser homologada pelo responsável normativo do processo, não pela
equipe de tecnologia isoladamente.

## 4. Destino do registro inválido

Foi escolhida **quarentena**.

- descartar impediria reconciliação e auditoria;
- converter qualquer defeito para “não informado” misturaria ausência legítima com erro
  estrutural;
- quarentena preserva linha, origem e motivo.

Há quarentena tanto para solicitações quanto para listas normativas e para a nova referência XLSX
de áreas. A terceira fonte contém defeitos intencionais para demonstrar que a mesma política de
qualidade vale também para dados de referência.

## Decisões complementares da V4

### Validação de área deixou de ser hardcoded

As áreas válidas não ficam mais em uma lista literal dentro do SQL. Elas vêm de
`areas_referencia.xlsx`, passam por Staging, validação e quarentena, e somente áreas ativas e
válidas alimentam a validação das solicitações.

### Consulta final sem regra de negócio

A SQL de entrega lê exclusivamente `gold.agg_resposta_gerencial`. Não há cálculo de percentual,
regra de prioridade, classificação, deduplicação ou filtro de negócio nela.

### Reprocessamento

`python -m src.pipeline` remove apenas artefatos derivados previamente autorizados e recria Bronze,
snapshots e as views source. `data/raw` permanece intacto. Em seguida `dbt build` reconstrói todo o
restante pela linhagem.
