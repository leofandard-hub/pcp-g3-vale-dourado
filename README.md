# Sistema de PCP — G3 · Vale Dourado Frutas

ENG037 · Planejamento e Controle da Produção · UFBA · 2026.2
Grupo: Léo Fandard e Raphael
Packing house de manga com câmaras frias · Juazeiro · data de status 13/11/2026

**Link público:** https://pcp-g3-vale-dourado-app.vercel.app

## Estrutura
```
app/                     sistema web publicado (HTML/JS, Chart.js, Three.js)
app/data/g3.json         histórico tratado + linha de base (gerado pelos scripts)
dados/brutos/            30 CSV originais do pacote G3 (não editar)
dados/tratados/          CSV após o tratamento
scripts/limpeza.py       tratamento dos dados → docs/qualidade-dos-dados.md
scripts/calculos.py      CPM da linha de base (D2) e valor agregado (Anexo D)
docs/                    D1–D12, qualidade dos dados, diário de prompts, caderno (PDF)
CONTEXTO.md              resumo do caso — toda conversa com a IA começa por ele
DICIONARIO.md            dicionário de dados do professor
```

## Entregas na pasta docs/
| Doc | Arquivo |
|---|---|
| D1 EAP comentada | D1_EAP_comentada.xlsx |
| D2 Rede e caminho crítico | D2_rede_caminho_critico.xlsx (.ods) |
| D3 Gantt (obrigatório .ods) | D3_Gantt.ods |
| D4 Histograma e nivelamento | D4_histograma_nivelamento.xlsx |
| D5 Plano de equipamentos | D5_plano_equipamentos.xlsx |
| D6 Curva ABC e compras | D6_curva_ABC_compras.xlsx |
| D7 Mapa de contratações | D7_mapa_contratacoes.xlsx |
| D8 Físico-financeiro e curva S | D8_fisico_financeiro_curva_S.xlsx |
| D9 Dimensionamento da operação | D9_dimensionamento_operacao.pdf + .xlsx |
| D10 Localização e layout | D10_localizacao_layout.pdf + .xlsx |
| D11 Plano de controle | D11_plano_de_controle.pdf |
| D12 Estratégia de PCP | D12_estrategia_PCP.pdf |
| Relatório gerencial (15 slides) | relatorio_gerencial.pdf (+ .pptx editável) |
| Qualidade dos dados | qualidade-dos-dados.md |
| Diário de prompts | diario-de-prompts.md |
| Ficha do grupo | ficha_do_grupo.docx (preencher) |
| Conferência do caderno | conferencia_caderno.md (M1, M3, M4 do sistema) |
| Kit da semana de campo | kit_semana_de_campo.pdf (parte Léo + parte Raphael) |
| Guia do caderno (estudo, não entregar) | guia_caderno_M1-M6.pdf |

Tudo é regenerado por `bash scripts/rodar_tudo.sh`.

## Rodar os cálculos
```
python scripts/limpeza.py      # trata os dados e confere os números de controle
python scripts/calculos.py     # linha de base, caminho crítico, valor agregado, gera app/data/g3.json
```

## Publicar (Vercel)
1. vercel.com → Add New → Project → importar este repositório.
2. **Root Directory = `app`**, Framework = Other, sem build → Deploy.
3. Cada merge na `main` republica sozinho.

## Banco na nuvem (R2 · Supabase)
1. supabase.com → New project (plano gratuito).
2. SQL Editor → colar `docs/supabase.sql` → Run.
3. Project Settings → API → copiar **Project URL** e **anon public key**.
4. No sistema, aba **Dados e configuração** → colar → Conectar. Cada integrante faz isso uma vez no seu navegador.
   A chave **não vai para o repositório**.

## Requisitos
| Req | Onde está no sistema |
|---|---|
| R1 Importar histórico | `app/data/g3.json` (tabelas 01–24 tratadas); conferência na aba *Dados e configuração* |
| R2 Banco na nuvem | Supabase, tabela `lancamentos` (indicador "nuvem ✓" no topo) |
| R3 Telas de lançamento | aba *Lançamentos*: RDO MO, RDO produção, equipamentos, pedidos, recebimento, plano semanal, restrições, FVS, ocorrências, custos |
| R4 Avanço por atividade e fase | *Análises* + *Dashboard* |
| R5 Valor agregado + curva S | *Dashboard* (curva S) e *Análises* (por fase) |
| R6 PPC e Pareto | *Dashboard* (causas padronizadas pelo script) |
| R7 RUP real × orçada | *Análises* (atividade e encarregado) |
| R8 Histograma real × previsto + absenteísmo | *Dashboard* + *Análises* |
| R9 Suprimentos | *Análises* (pedidos atrasados, atraso por fornecedor) + alertas de data-limite |
| R10 Equipamentos | *Análises* (disponibilidade, utilização, MTBF, MTTR por tipo) |
| R11 Dashboard de uma tela com filtro por data | *Dashboard* + campo Data no topo |
| R12 Modelo 3D | *Modelo 3D* (zonas da tabela 13, cor = avanço, controle de data, clique na zona) |
