# CONTEXTO.md — G3 · Vale Dourado Frutas (Juazeiro)

> Toda conversa nova com a IA começa colando este arquivo.

## Grupo
- Léo Fandard: D1, D2, D3, D4, D8, D12, relatório gerencial; caderno M1, M2, M4.
- Raphael: D5, D6, D7, D9, D10, D11; caderno M3, M5, M6.
- Entrega única até terça 24/11/2026 23h59; apresentação em 30/11/2026.

## O caso
- Packing house de manga com câmaras frias para exportação, 9.000 m². Juazeiro (BA).
- Início 16/02/2026 (dia útil 1 = 18/02, Carnaval). Contrato: **23/03/2027** (du 271).
- Custo direto orçado **R$ 28.116.171,71** · adm. local R$ 146.000/mês · preço de venda R$ 36,6 mi (BDI 22%).
- **Multa R$ 18.300/du** de atraso · **ganho operacional R$ 30.900/du** em operação.
- Efetivo máximo no canteiro: 130. Demanda da nova unidade: 42.000 caixas/dia, 2 turnos de 8 h, paradas planejadas 10%.
- Histórico nos CSV até **06/11/2026**; semana 09–13/11 vem nos boletins do dossiê (digitar pelas telas, ≥3 integrantes). **Data de status: 13/11/2026.**

## Dados
- 30 tabelas em `dados/brutos/` (dicionário em `DICIONARIO.md`). Tratadas em `dados/tratados/` por `scripts/limpeza.py`.
- Problemas encontrados: 9 duplicatas (t15), 3 quantidades 10× (t16: A09, A11, A15), 12 custos DIVERSOS (t20, reapropriados pelo documento), causas fora do padrão (t21).
- Números de controle (06/11): 691 linhas t15 · 53.222,4 Hh · R$ 11.419.304,12 · 124 pedidos — **todos batem**.
  Após a semana de campo (13/11): 55.086,8 Hh · R$ 11.689.047,31.

## Convenções (Anexo D)
- Duração esforço = ⌈qtd × RUP ÷ (efetivo × 8)⌉; efetivo = soma da mão de obra na t07. FIXA = duracao_fixa_du.
- Rede em du: TI → ES ≥ EF_pred + 1 + lag; II → ES ≥ ES_pred + lag. Linha de base = datas mais cedo.
- VP linear nos du da duração; avanço = Σ qtd executada ÷ qtd orçada (≤100%); VA = avanço × custo orçado.
- CR = custos de todas as naturezas exceto INDIRETO. IDC = VA/CR, IDP = VA/VP, EAC = BAC/IDC.
- PPC = concluídos ÷ planejados (concluído ≥ 97% da meta). RUP real = (Hh normais + extras) ÷ qtd executada.
- Equipamentos: disp. = 1 − (corr+prev)/h disp.; MTBF = h operando/falhas; MTTR = h corretiva/falhas.

## Resultados já calculados (scripts/calculos.py)
- Linha de base: **261 du → término 09/03/2027** (folga de 10 du até o contrato).
- Caminho crítico: A01 → A03 → A07 → A08 → A09 → A10 → A12 → A23 → A26 → A35 → A37 → A38. Quase crítica: A36 (folga 2).
- Valor agregado em 16/10 confere com a folha M4 do dossiê (% previsto e % físico por fase).
- Em 06/11: VP R$ 17,95 mi · VA R$ 10,84 mi · CR R$ 11,42 mi · **IDP 0,60 · IDC 0,95** · EAC R$ 29,62 mi.
- Sub-rede M1: 74 du, crítico A23 → A26 → A35 → A36.

## Stack
- `app/` estático (Chart.js e Three.js por CDN), publicado no Vercel (Root Directory = app).
- Lançamentos no Supabase, tabela `lancamentos` (docs/supabase.sql); URL e chave coladas na tela, nunca no repositório.
