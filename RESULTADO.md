# Resposta da PoC — FormalizaEnte

Os dados são sintéticos e foram construídos para demonstrar a jornada de dados e os tratamentos de qualidade. Os percentuais não representam cobertura oficial de listas reais.

A fonte oficial dos números é a camada Gold, especialmente `gold.agg_cobertura_geral` e `gold.agg_resposta_gerencial`.

## Resultado principal

Após a quarentena dos registros estruturalmente inválidos, o resultado da PoC é:

- **65 solicitações válidas**;
- **56 solicitações cobertas** por ao menos uma amostra normativa;
- **9 solicitações não encontradas**;
- **taxa de cobertura: 86,15%**;
- **11 solicitações ambíguas** presentes em duas ou mais listas;
- **taxa de ambiguidade: 16,92%**.

## Distribuição por esfera

A esfera é decidida a partir da prioridade versionada em `seeds/ref_listas.csv`:

1. REMUME → Município;
2. RESME → Estado;
3. RENAME → União;
4. ausência nas listas → Não encontrado.

Quando um item aparece em mais de uma lista, a prioridade define a esfera principal, mas o indicador de ambiguidade é preservado.

## Recortes principais

### Período

| Mês | Total | Atendidas | Cobertura |
|---|---:|---:|---:|
| 2026-01 | 20 | 20 | 100,00% |
| 2026-02 | 20 | 15 | 75,00% |
| 2026-03 | 20 | 17 | 85,00% |
| 2026-04 | 5 | 4 | 80,00% |

### Área

| Área | Total | Atendidas | Cobertura |
|---|---:|---:|---:|
| DEFENSORIA | 21 | 18 | 85,71% |
| NAT-JUS | 23 | 19 | 82,61% |
| VARA_CIVEL | 21 | 19 | 90,48% |

## Como obter a resposta

```bash
python -m src.pipeline
dbt build
python -m src.answer
```

O último comando lê a camada Gold e grava evidências em `docs/evidence/`.

## Limite de validade

Os números são confiáveis **para o dataset sintético desta PoC**. Eles não representam cobertura oficial do FormalizaEnte, do TJMS, de Campo Grande/MS, do SUS ou de listas oficiais completas.
