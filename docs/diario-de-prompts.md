# Diário de prompts — G3

Mínimo 10 entradas, de pelo menos 4 integrantes. Para cada uma: o que foi pedido, o que a IA errou, como o grupo corrigiu.

| # | Data | Quem | Ferramenta | O que pedimos | O que a IA errou | Como corrigimos | Commit |
|---|---|---|---|---|---|---|---|
| 1 | 22/11 | Léo | Claude | Estrutura do repositório e primeira versão do sistema, antes de ter os dados | Fez um sistema genérico, com nomes de colunas inventados, sem conhecer o DICIONARIO.md | Localizamos a pasta do G3 no Drive e pedimos para refazer com as tabelas reais | |
| 2 | 22/11 | Léo | Claude | Script de limpeza que bata com os números de controle do dossiê | Primeira versão só sinalizava valores suspeitos (>5× a mediana) sem corrigir; também detectava "duplicatas" legítimas em tabelas sem ID | Critério ajustado: só corrige se ÷10 voltar à mediana da atividade; duplicata exata só na t15. Conferido: A09 fecha em 288,0 t; 691 linhas, 53.222,4 Hh, R$ 11.419.304,12, 124 pedidos ✔ | |
| 3 | 22/11 | Léo | Claude | Reapropriar os 12 custos DIVERSOS | — (propôs deixar sem dono) | Pedimos para usar o documento de origem (RM-Axx, LOC + apontamento da semana na t17, FOLHA + descrição). Total não muda | |
| 4 | 22/11 | Léo | Claude | CPM da linha de base pelo Anexo D | Risco de errar a convenção de dias (dia útil 1 = 18/02 por causa do Carnaval, TI com +1) | Validamos contra a folha M4 do dossiê: % previsto em 16/10 bate em todas as fases (90,4%, 81,7%, 10,1%, 86,5%) | |
| 5 | 22/11 | Léo | Claude | Modelo 3D com a tabela 13 | Módulo 3D carregava depois dos dados e a tela ficava vazia; câmera apontava para o lugar errado (eixo y da planta invertido) | Flag `PCP.ready` + câmera reposicionada; testado com clique na zona GALPAO | |
| 6 | 22/11 | Léo | Claude | Pareto das causas no dashboard | Barras desenhadas no eixo de % acumulado (ficavam minúsculas) | Eixo y explícito para as barras | |
| 7 | 22/11 | Léo | Claude | D5 locar × comprar | Concluiu "COMPRAR" o guindaste por supor revenda pelo valor contábil, sem custo de capital | Incluímos custo de capital (1% a.m.) e deságio de revenda (15%) em células amarelas → LOCAR | |
| 8 | 22/11 | Léo | Claude | D9 em PDF com gráfico da demanda | Gráfico da demanda saiu zerado: uma variável foi reaproveitada para a tabela de manutenção | Variável renomeada e figura conferida visualmente | |
| 9 | 22/11 | Léo | Claude | Cenários de recuperação de prazo | Não checou o limite de 130 pessoas no canteiro; o cenário 2 dava pico de 193 | Nivelamento das atividades com folga (pico 161) + custo de ampliar a vivência incluído no cenário | |
| 10 | 22/11 | Léo | Claude | Relatório gerencial | Alguns cartões de texto vazavam sobre a fonte; número de causas citado errado (26 em vez de 22) | Altura dos cartões pelo tamanho do texto; números conferidos contra a tabela 21 | |
| 11 | | | | | | | |
| 12 | | | | | | | |
