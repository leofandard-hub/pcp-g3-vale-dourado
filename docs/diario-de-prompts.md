# Diário de prompts — G3 · Vale Dourado Frutas

Registro dos pedidos mais importantes feitos à IA (Claude), do que ela errou e de como o grupo corrigiu.
Os pedidos estão **resumidos e reformulados** a partir das conversas reais; os erros e as correções são os que de fato aconteceram.
Entradas de Raphael: ver seção no final.

---

### 1 · 22/11 · Léo · Entender o trabalho e localizar os dados
**Pedido:** "Resuma o enunciado do Trabalho Final e liste os arquivos de que você precisa para começar. Procure no Drive da disciplina o pacote de dados do G3."
**O que a IA errou:** procurou só na pasta "Materiais das Aulas" e concluiu que o pacote não estava disponível; antes disso, já tinha montado uma primeira versão do sistema com colunas genéricas, sem conhecer o DICIONARIO.md.
**Como corrigimos:** indicamos a pasta correta do Grupo 3 no Drive (enunciado, dossiê, DICIONARIO.md, 30 CSV) e pedimos para refazer tudo com as tabelas reais.
**Commit:** 4554063

### 2 · 22/11 · Léo · Tratamento dos dados e números de controle
**Pedido:** "Escreva um script que trate os 30 CSV (duplicatas, erros de digitação, custos sem apropriação, textos fora do padrão), documente cada correção e confira os totais com os números de controle do dossiê."
**O que a IA errou:** a primeira versão só sinalizava valores suspeitos sem corrigir, e o sistema removia linhas idênticas em todas as tabelas, inclusive onde podiam ser legítimas.
**Como corrigimos:** critério explícito para os erros ×10 (só corrige se ÷10 voltar à mediana da atividade; conferido: A09 fecha em 288,0 t), duplicatas removidas só no script, DIVERSOS reapropriados pelo documento de origem. Os quatro números de controle de 06/11 batem (691 linhas, 53.222,4 Hh, R$ 11.419.304,12, 124 pedidos).
**Commit:** 16e534a · docs/qualidade-dos-dados.md

### 3 · 22/11 · Léo · Linha de base (CPM) pelo Anexo D
**Pedido:** "Calcule durações pela RUP, datas mais cedo e mais tarde, folgas e caminho crítico seguindo exatamente o Anexo D, e valide o método com algum dado do dossiê."
**O que a IA errou:** risco de convenção de dias (o dia útil 1 é 18/02, por causa do Carnaval; ligação TI com +1 dia).
**Como corrigimos:** comparamos o % previsto por fase em 16/10 com a folha M4 do dossiê: bate em todas as fases (90,4%, 81,7%, 10,1%, 86,5%). Linha de base: 261 du, término 09/03/2027.
**Commit:** 4554063 · scripts/calculos.py

### 4 · 22/11 · Léo · Cálculo do PPC
**Pedido:** "Calcule o PPC por semana e o Pareto das causas no sistema."
**O que a IA errou:** usou a coluna `concluido` da tabela 21 em vez da regra do Anexo D (pacote concluído = pelo menos 97% da meta).
**Como corrigimos:** PPC recalculado pela regra dos 97% a partir de meta e quantidade realizada.
**Commit:** 4554063

### 5 · 22/11 · Léo · Planilhas D1 a D8
**Pedido:** "Gere as planilhas D1 a D8 com fórmulas simples, que um aluno de nível intermediário em Excel consiga refazer (SOMA, SE, PROCV, SOMASE), com capa de premissas e fonte."
**O que a IA errou:** no D5, a análise locar × comprar indicava COMPRAR o guindaste, porque supunha revenda pelo valor contábil e ignorava o custo de capital; no D3, uma atividade com 99,9998% não aparecia como concluída no Gantt.
**Como corrigimos:** incluímos custo de capital (1% a.m.) e deságio de revenda (15%) em células de premissa → decisão LOCAR; avanço arredondado. Todas as planilhas recalculadas no LibreOffice sem erro.
**Commit:** 4554063

### 6 · 22/11 · Léo · D9 e D10
**Pedido:** "Monte o dimensionamento da operação (takt, capacidade, gargalo, OEE, manutenção) e a análise de localização e layout, com planilha e relatório em PDF."
**O que a IA errou:** o gráfico de demanda do D9 saiu zerado, porque uma variável do script foi reaproveitada para a tabela de manutenção.
**Como corrigimos:** variável renomeada e figura conferida visualmente. Resultado mantido: gargalo PT03 (hidrotérmico), 31.878 cx/dia para 42.000.
**Commit:** 4554063

### 7 · 22/11 · Léo · Cenários de recuperação de prazo
**Pedido:** "Compare três cenários (seguir como está, recuperar prazo, replanejar) com custo adicional, multa evitada e ganho operacional, usando a mesma rede da linha de base."
**O que a IA errou:** não verificou o limite de 130 pessoas no canteiro; o cenário de recuperação chegava a 193 pessoas simultâneas.
**Como corrigimos:** contagem de efetivo por turno, nivelamento das atividades com folga (pico 161) e custo de ampliação temporária da vivência incluído no cenário.
**Commit:** 4554063 · scripts/cenarios_custos.py

### 8 · 22/11 · Léo · Relatório gerencial
**Pedido:** "Prepare o relatório para a diretoria em até 15 slides, conclusão primeiro, com a tabela e o filtro de origem de cada número."
**O que a IA errou:** cartões de texto transbordavam sobre a fonte, um número estava errado (26 causas em vez de 22) e o JSON dos dados tinha valores NaN que quebravam a geração.
**Como corrigimos:** altura dos cartões proporcional ao texto, números conferidos contra a tabela 21, NaN tratados.
**Commit:** 4554063

### 9 · 22/11 · Léo · Modelo 3D
**Pedido:** "Faça o modelo 3D com as zonas da tabela 13, cor pelo avanço, controle de data e clique na zona mostrando as atividades."
**O que a IA errou:** a cena ficava vazia (o módulo 3D carregava antes dos dados) e a câmera apontava para fora do terreno (eixo y da planta invertido).
**Como corrigimos:** sinal de "dados prontos" antes de desenhar e câmera reposicionada; testado com clique na zona GALPAO.
**Commit:** 4554063

### 10 · 22/11 · Léo · Publicação (GitHub, Vercel, Supabase)
**Pedido:** "Publique o repositório, coloque o sistema online e ligue um banco na nuvem para que os dois integrantes vejam os mesmos lançamentos."
**O que a IA errou:** tentou criar o repositório e não tinha permissão; o sistema só aceitava a chave antiga do Supabase (formato `eyJ…`), e o projeto novo usa `sb_publishable_…`; faltavam permissões da chave pública na tabela.
**Como corrigimos:** repositório criado manualmente; Root Directory `app` no Vercel; código adaptado aos dois formatos de chave; `grant` adicionado em docs/supabase.sql.
**Commits:** 100053e, 984834f, aca687b

### 11 · 22/11 · Léo · Telas de lançamento (semana de campo)
**Pedido:** "Vamos lançar os boletins da semana de campo pelas telas do sistema."
**O que a IA errou:** o formulário vinha com a data de status (13/11) preenchida, e a primeira linha do RDO de 09/11 foi gravada com a data errada; o botão de apagar não funcionava, porque o navegador bloqueava a janela de confirmação.
**Como corrigimos:** linha apagada e relançada; formulário passou a exigir a data e a guardar a última usada; apagar em dois cliques. Conferência automática: 21 linhas de mão de obra, 1.096 Hh, sem faltas nem duplicatas.
**Commits:** a553d5b, 10a90ad

### 12 · 26/11 · Léo · Modelo 3D mais legível
**Pedido:** "O modelo 3D está pouco claro: há falhas de textura, as cores quase não se distinguem e os volumes não representam bem a obra. Refaça a representação e explique o que cada cor e cada volume significam."
**O que a IA errou:** a primeira versão empilhava caixas transparentes (texturas piscando por sobreposição), usava um degradê contínuo difícil de ler e desenhava o terreno como se fosse uma zona. Depois, o controle de data ia até março de 2027, embora só exista avanço real até a data de status: a obra "congelava" a partir de 16/11.
**Como corrigimos:** materiais opacos sem sobreposição, 5 classes de cor com legenda (0%, 1–33%, 34–66%, 67–99%, 100%), galpão montado atividade por atividade (sapatas A08, pilares A09, cobertura A10, fechamento A11, piso A12), moldura vermelha nas zonas críticas atrasadas e controle de data limitado a 13/11. Testado no navegador sem erros.
**Commits:** 708bd7b, d8c0fb9, 26079f5

### 13 · 26/11 · Léo · Copiloto de IA no sistema (opcional)
**Pedido:** "Crie uma aba onde a diretoria faça perguntas em linguagem natural sobre a obra. A IA não pode inventar números: deve responder só com o que o sistema já calculou, dizer quando o dado não existe e citar a fonte. A chave da IA não pode ficar no repositório."
**O que a IA errou:** (1) as respostas levavam de 30 s a 2 min, porque o modelo "raciocinava" longamente antes de responder; (2) uma pergunta falhou quando o servidor do Gemini estava sobrecarregado (erro 503); (3) ao listar as atividades críticas atrasadas, esqueceu a A12 (piso, 0% realizado contra 97,5% previsto), porque usou só a lista de atrasos do relatório, que contém apenas atividades já iniciadas.
**Como corrigimos:** raciocínio interno reduzido, limite de 25 s por chamada e modelo mais leve primeiro (resposta em cerca de 2 s); nova tentativa automática com modelos reserva quando há sobrecarga; regra no prompt para comparar previsto × realizado de todas as atividades. Conferimos as respostas com os números do relatório (cenários, multa, atrasos), e uma pergunta fora do escopo recebeu "Esse dado não está no sistema". Chave guardada só na variável `GEMINI_API_KEY` da Vercel. Feito numa branch e integrado por pull request (#1).
**Commits:** 502fc6e, 7fb0ccc (merge do PR #1), 9d44399, 31eb32c, 062add2

---

## Entradas de Raphael

| # | Data | O que pediu à IA | O que a IA errou | Como corrigiu | Commit |
|---|---|---|---|---|---|
| 14 | | | | | |
| 15 | | | | | |
