# Defeitos intencionais das fontes

Os dados desta PoC são sintéticos e foram construídos para que o pipeline precise tratar
problemas reais de qualidade sem alterar a camada bruta.

## `solicitacoes.csv`

- diferenças de caixa e espaços extras;
- acentuação inconsistente;
- datas inválidas ou ausentes;
- identificadores ausentes e duplicados;
- item, responsável ou área ausentes/inválidos;
- dois lotes de ingestão para produzir versões Delta distintas.

## `listas_normativas.json`

- diferenças de caixa/espaçamento nos textos;
- duplicidade de item em listas distintas, gerando ambiguidade legítima;
- registro propositalmente incompleto para quarentena.

## `areas_referencia.xlsx`

- área inativa que não deve validar solicitações;
- duplicidade intencional de `NAT-JUS`;
- registro sem código da área;
- caixa e espaços inconsistentes no registro legado.

A ingestão preserva esses defeitos. Limpeza, validação, deduplicação e decisão de destino
acontecem exclusivamente nos modelos dbt.
