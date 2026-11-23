# Qualidade dos dados — G3 · Vale Dourado Frutas

Gerado por `scripts/limpeza.py`. Arquivos originais em `dados/brutos/` (não alterados); arquivos tratados em `dados/tratados/`.

## 1. Linhas duplicadas
- `15_rdo_mao_de_obra`: **9 linhas duplicadas removidas** (linhas do CSV: [68, 194, 304, 336, 352, 555, 560, 616, 643])

## 2. Erros de digitação (quantidade 10× maior)
| Data | Atividade | Valor lançado | Mediana da atividade | Valor corrigido |
|---|---|---|---|---|
| 2026-08-25 | A09 | 58.6 | 5.56 | 5.86 |
| 2026-10-07 | A15 | 640.34 | 70.042 | 64.034 |
| 2026-10-21 | A11 | 806.36 | 82.858 | 80.636 |

Conferência: após a correção, A09 soma exatamente 288,0 t (100% da quantidade orçada).

## 3. Custos sem apropriação (DIVERSOS)
| Lançamento | Data | Documento | Valor (R$) | Reapropriado para | Critério |
|---|---|---|---|---|---|
| L00080 | 2026-05-08 | LOC-CAM-02-2026-S19 | 3,609.80 | A07 | apontamento do CAM-02 na semana S19 (tabela 17) |
| L00105 | 2026-05-22 | LOC-CAM-03-2026-S21 | 2,149.08 | A07 | apontamento do CAM-03 na semana S21 (tabela 17) |
| L00111 | 2026-05-29 | FOLHA-2026-S22 | 46,726.40 | A08 | nome da atividade na descrição da folha |
| L00116 | 2026-05-29 | LOC-RET-01-2026-S22 | 4,038.70 | A08 | apontamento do RET-01 na semana S22 (tabela 17) |
| L00148 | 2026-06-26 | RM-A08-FOR-2026-S26 | 7,498.56 | A08 | atividade no código da requisição |
| L00157 | 2026-07-03 | RM-A08-FOR-2026-S27 | 9,439.08 | A08 | atividade no código da requisição |
| L00158 | 2026-07-03 | LOC-BET-01-2026-S27 | 7,406.16 | A08 | apontamento do BET-01 na semana S27 (tabela 17) |
| L00159 | 2026-07-03 | LOC-RET-01-2026-S27 | 3,230.96 | A08 | apontamento do RET-01 na semana S27 (tabela 17) |
| L00218 | 2026-08-21 | RM-A14-ARG-2026-S34 | 1,683.68 | A14 | atividade no código da requisição |
| L00317 | 2026-10-02 | LOC-PTA-04-2026-S40 | 1,719.54 | A10 | apontamento do PTA-04 na semana S40 (tabela 17) |
| L00401 | 2026-10-30 | RM-A13-PAV-2026-S44 | 75,368.74 | A13 | atividade no código da requisição |
| L00425 | 2026-11-06 | LOC-RET-01-2026-S45 | 3,230.96 | A13 | apontamento do RET-01 na semana S45 (tabela 17) |

O total do custo direto não muda (R$ 11.419.304,12 até 06/11): só a apropriação por atividade/fase.

## 4. Causas de não cumprimento fora do padrão (tabela 21)
| Texto original | Padronizado | Ocorrências |
|---|---|---|
| `Produtividade ` | PRODUTIVIDADE | 2 |
| `equip.` | EQUIPAMENTO | 1 |
| `produtividade` | PRODUTIVIDADE | 1 |
| `terceiros` | TERCEIROS | 1 |
| `Servico_anterior` | SERVICO_ANTERIOR | 1 |
| `EQUIPAMENTOS` | EQUIPAMENTO | 1 |
| `mão de obra` | MAO_DE_OBRA | 1 |

## 5. Conferência com os números de controle do dossiê (até 06/11/2026)

| Conferência | Dossiê | Dados tratados | Bate? |
|---|---|---|---|
| Linhas da tabela 15 sem duplicatas | 691 | 691 | ✔ |
| Homens-hora (normais + extras) | 53.222,4 | 53,222.4 | ✔ |
| Custo direto apropriado (inclui DIVERSOS) | 11.419.304,12 | 11,419,304.12 | ✔ |
| Pedidos de compra emitidos | 124 | 124 | ✔ |

