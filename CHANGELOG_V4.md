# V4 — consolidação das três versões

Esta versão não simplesmente acumula arquivos: ela preserva uma única pergunta e uma única
arquitetura, incorporando os pontos mais fortes encontrados nas três implementações anteriores.

## Incorporado da versão mais completa

- pergunta de negócio focada em cobertura;
- métricas derivadas na Gold;
- documentação extensa;
- CI, Makefile, testes Python e testes dbt;
- pipeline reprocessável;
- histórico Delta e time travel;
- consulta final sem regra de negócio.

## Incorporado das demais versões

- fonte XLSX, chegando a **3 formatos**;
- Bronze declarada como `source()` na DAG dbt;
- regra de prioridade retirada de SQL hardcoded e movida para seed versionado;
- referência organizacional externa para validar áreas;
- quarentena também para dados de referência;
- mart único orientado à resposta completa.

## Resultado

A V4 foi desenhada especificamente para reduzir os riscos do enunciado:

- `python -m src.pipeline` + `dbt build` a partir da raiz;
- nada de regra de negócio na consulta final;
- 2+ versões Delta;
- mais de duas fontes e mais de dois formatos;
- 8+ testes e múltiplos tipos;
- DAG clara desde a Bronze;
- DECISOES.md específico, não genérico.
