# Catálogo de dados

Todas as fontes são sintéticas e próprias para a atividade acadêmica.

## `data/raw/solicitacoes.csv`

Fonte operacional principal. Contém identificador, data, item, categoria informada, área,
responsável e lote de ingestão.

Papel no projeto:

- define o universo de solicitações;
- possui dois lotes para gerar 2+ versões Delta;
- contém defeitos intencionais para demonstrar quarentena.

## `data/raw/listas_normativas.json`

Amostra sintética de itens associados às listas REMUME, RESME e RENAME.

Papel no projeto:

- permite derivar cobertura;
- permite derivar esfera de resolução;
- permite detectar ambiguidade quando o mesmo item existe em mais de uma lista.

## `data/raw/areas_referencia.xlsx`

Cadastro sintético de áreas organizacionais.

Papel no projeto:

- fornece um terceiro formato de fonte;
- substitui a validação hardcoded de áreas;
- contém registro inativo, duplicidade e código ausente para demonstrar tratamento de referência
  inválida.

## `seeds/ref_listas.csv`

Não é uma fonte bruta: é uma **regra de referência versionada no dbt**. Define qual esfera está
associada a cada lista e sua prioridade. A mudança da política passa a ser uma alteração explícita
e testável.

## Metadados técnicos da Bronze

A ingestão adiciona somente:

- `source_row_number`;
- `_source_file`;
- `_ingested_at_utc`.

Esses campos existem para rastreabilidade e não mudam o significado do dado de negócio.

## Defeitos

A lista detalhada está em `data/raw/DEFEITOS.md`.
