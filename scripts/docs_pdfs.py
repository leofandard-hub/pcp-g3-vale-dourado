"""Gera os PDFs D9, D10, D11 e D12 (docx acadêmico → PDF). Uso: python scripts/docs_pdfs.py"""
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

R = Path(__file__).resolve().parent.parent; DOCS = R / "docs"; TMP = DOCS / "_build"; TMP.mkdir(exist_ok=True)
X = json.loads((DOCS / "_d9_d10.json").read_text()); AN = json.loads((DOCS / "analise_13-11.json").read_text())
CE = json.loads((DOCS / "_cenarios.json").read_text()); D4 = json.loads((DOCS / "_d4.json").read_text())
br = lambda v, d=0: f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
pc = lambda v, d=1: br(v * 100, d) + "%"
rs = lambda v: "R$ " + br(v, 0)
GRUPO = "Grupo 3 · Vale Dourado Frutas · Léo Fandard e Raphael"
DATA = "novembro de 2026"
from docs_util import RESPONSAVEL
import sys; sys.path.insert(0, str(Path(__file__).parent))


def gerar(nome, spec):
    j = TMP / f"{nome}.json"; j.write_text(json.dumps(spec, ensure_ascii=False))
    docx = TMP / f"{nome}.docx"
    subprocess.run(["node", str(R / "scripts" / "gerar_docx.js"), str(j), str(docx)], check=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(DOCS), str(docx)], check=True, capture_output=True)
    print("ok", nome + ".pdf")


# ============================ D9 ============================
cap = X["cap"]; dem = X["dem"]; m3 = X["m3"]; oee = X["oee_real"]
gar = min(cap, key=lambda c: c["cap"]); inv_tot = sum(c["inv"] for c in cap)
RD = "D9"
d9 = {"rosto": {"grupo": GRUPO, "titulo": "D9 · Dimensionamento da operação", "subtitulo": "Packing house de manga com câmaras frias para exportação, Juazeiro (BA)", "data": DATA,
                "premissas": ["Dois turnos de 8 h por dia e paradas planejadas de 10% do turno (tabela 01).", "Demanda de projeto de 42.000 caixas por dia (pico da safra).",
                              "OEE previsto por posto = disponibilidade × eficiência × qualidade da tabela 26; fórmulas do Anexo D do enunciado."],
                "fontes": ["Tabelas 01, 25, 26, 27 e 28 do pacote de dados do G3; planilha D9_dimensionamento_operacao.xlsx."], "responsavel": RESPONSAVEL[RD]},
      "corpo": [
          {"h1": "1 Introdução"},
          {"p": "Este documento dimensiona a operação da nova unidade da Vale Dourado Frutas a partir dos dados do site atual e dos postos projetados. O objetivo é verificar se a linha, tal como projetada, atende à demanda de pico da safra, identificar o gargalo, calcular os recursos e operadores necessários e o investimento adicional, comparar o OEE atual com o previsto e propor um plano de manutenção."},
          {"h1": "2 Classificação da operação"},
          {"p": "No modelo de entradas, transformação e saídas (ITO), a unidade recebe manga in natura dos produtores do Vale do São Francisco, embalagens, água, energia e mão de obra sazonal; realiza uma transformação física (lavagem, seleção óptica, tratamento hidrotérmico exigido pela exportação, embalagem, pré-resfriamento e armazenagem refrigerada) e entrega caixas de 4 kg paletizadas e rastreadas por lote."},
          {"p": f"Pelos 4Vs, a operação tem volume alto, variedade baixa (três famílias com a mesma caixa: Tommy {pc(dem['fam']['Manga Tommy (cx 4 kg)'],0)}, Palmer {pc(dem['fam']['Manga Palmer (cx 4 kg)'],0)} e Kent {pc(dem['fam']['Manga Kent (cx 4 kg)'],0)} da demanda), variação alta e visibilidade baixa. A variação é a característica dominante: a demanda mensal oscila entre {br(dem['min'])} e {br(dem['pico'])} caixas, com coeficiente de variação de {br(dem['cv'],2)} e pico em {dem['mes_pico']}. A Figura 1 mostra que, em {dem['acima_cap']} dos 36 meses, a demanda superou a capacidade nominal do site atual (551.200 caixas por mês), o que explica a terceirização de parte do beneficiamento."},
          {"figura": {"arquivo": "../figuras/d9_demanda.png", "titulo": "Demanda mensal do site atual e capacidade nominal", "fonte": "elaborado pelo grupo a partir da tabela 25.", "ratio": 0.49}},
          {"p": "A tipologia é de produção em fluxo, repetitiva e em massa durante a safra. A política de atendimento adotada é de fazer para estoque de curtíssimo prazo, puxado pela colheita, com a expedição montada contra o pedido do importador. Como o produto é perecível, não há estoque entre safras: a capacidade precisa ser dimensionada para o pico, e não para a média."},
          {"h1": "3 Takt, capacidade e gargalo"},
          {"p": f"O tempo disponível por dia é de 2 × 8 × 3.600 × (1 − 0,10) = {br(X['tdisp'])} s, e o takt para 42.000 caixas por dia é de {br(X['takt'],3)} s por caixa. A Tabela 1 apresenta a capacidade de cada posto com os recursos do projeto e o OEE previsto."},
          {"tabela": {"titulo": "Capacidade diária por posto e recursos necessários", "cab": ["Posto", "OEE previsto", "Capacidade (cx/dia)", "Recursos projeto", "Recursos necessários", "Adicionais", "Investimento (R$)"],
                      "linhas": [[f"{c['posto']} {c['nome']}", pc(c["oee"]), br(c["cap"]), c["proj"], c["nec"], c["add"], br(c["inv"])] for c in cap],
                      "larg": [3.2, 1.2, 1.4, 1.1, 1.2, 1, 1.4], "fonte_txt": "elaborado pelo grupo a partir da tabela 26 (D9, aba Capacidade)."}},
          {"figura": {"arquivo": "../figuras/d9_capacidade.png", "titulo": "Capacidade por posto e linha de demanda", "fonte": "elaborado pelo grupo.", "ratio": 0.51}},
          {"p": f"O gargalo é o {gar['posto']} ({gar['nome']}), com {br(gar['cap'])} caixas por dia, ou seja, {pc(gar['cap']/42000,0)} da demanda: no pico, cerca de {br(42000-gar['cap'])} caixas por dia não seriam tratadas. São necessários 6 tanques em vez de 4. A paletização (PT05) também fica abaixo da demanda e precisa de um terceiro recurso. O investimento adicional total é de {rs(inv_tot)}. Em sentido contrário, a embalagem manual (PT04) foi projetada com 28 estações, quando 19 bastariam com o OEE previsto: a folga de 9 estações (cerca de R$ 342 mil) pode ser revista ou mantida como proteção, já que o OEE real desse posto é o mais baixo da operação."},
          {"p": f"Com os recursos necessários, a operação exige {br(sum(c['ops'] for c in cap))} operadores por dia nos dois turnos, valor que orienta o recrutamento da atividade A33."},
          {"h1": "4 OEE atual e OEE previsto"},
          {"tabela": {"titulo": "OEE real do site atual (31/08 a 06/11/2026) e OEE previsto no projeto", "cab": ["Posto", "Disponibilidade", "Eficiência", "Qualidade", "OEE real", "OEE previsto"],
                      "linhas": [[c["posto"], pc(oee[c["posto"]]["disp"]), pc(oee[c["posto"]]["efic"]), pc(oee[c["posto"]]["qual"]), pc(oee[c["posto"]]["oee"]), pc(c["oee"])] for c in cap],
                      "fonte_txt": "elaborado pelo grupo a partir das tabelas 26 e 27."}},
          {"p": f"Todos os postos operam hoje abaixo do OEE previsto no projeto, com a maior distância na embalagem manual (PT04, {pc(oee['PT04']['oee'])} real contra {pc(cap[3]['oee'])} previsto). Se o hidrotérmico operar com o OEE real atual ({pc(oee['PT03']['oee'])}), a capacidade do gargalo cai ainda mais, o que reforça a necessidade dos tanques adicionais. No turno indicado para a folha M3 (PT04, 04/11/2026, turno 2), o tempo operando foi de {br(m3['op'])} min, com disponibilidade de {pc(m3['disp'])}, eficiência de {pc(m3['efic'])}, qualidade de {pc(m3['qual'])} e OEE de {pc(m3['oee'])}. A perda a atacar primeiro é a disponibilidade, causada por 2.411 min de paradas não planejadas."},
          {"h1": "5 Plano de manutenção"},
          {"p": f"No período de dezembro de 2025 a novembro de 2026, o site atual registrou {X['manut']['total_corr']} ordens corretivas e {br(X['manut']['custo_pecas'])} reais em peças. O PT04 concentra {X['manut']['PT04_corr']} corretivas para apenas {X['manut']['PT04_prev']} preventivas, com lubrificação e desgaste como causas mais frequentes. O plano proposto inverte essa proporção: preventiva semanal por estação no PT04 com checklist autônomo do operador no início do turno (manutenção produtiva total), preventiva quinzenal dos tanques hidrotérmicos e dos túneis de pré-resfriamento, que são os postos de maior impacto na capacidade, e estoque mínimo de peças críticas (resistências, bombas, sensores de temperatura e ventiladores) antes de cada safra. A aba Manutenção da planilha detalha MTBF, MTTR e a ação por posto."},
          {"h1": "6 Conclusão"},
          {"p": f"A nova unidade, como projetada, não atende à demanda de 42.000 caixas por dia: o tratamento hidrotérmico limita a linha a {br(gar['cap'])} caixas por dia. A recomendação é incluir dois tanques e um recurso de paletização ({rs(inv_tot)}), avaliar a redução de estações de embalagem e implantar o plano de manutenção antes da partida, porque o OEE real do site atual está abaixo do previsto em todos os postos. Como alternativa ao investimento, um terceiro turno apenas no hidrotérmico durante o pico também cobriria a demanda, mas exigiria pulmão refrigerado antes da embalagem e mão de obra noturna."},
      ],
      "referencias": ["MAGALHÃES, L. ENG037 Trabalho Final: Comitê de PCP. Enunciado geral e dossiê do Grupo 3. Salvador: UFBA, 2026.",
                      "SLACK, N.; BRANDON-JONES, A.; JOHNSTON, R. Administração da produção. 8. ed. São Paulo: Atlas, 2018."]}
gerar("D9_dimensionamento_operacao", d9)

# ============================ D10 ============================
cg = X["cg"]; ct = X["custo_transp"]; sc = X["score"]; lay = X["layout"]; dc = X["dist_cg"]
RD = "D10"
d10 = {"rosto": {"grupo": GRUPO, "titulo": "D10 · Localização e layout", "subtitulo": "Packing house de manga com câmaras frias para exportação, Juazeiro (BA)", "data": DATA,
                 "premissas": ["Centro de gravidade ponderado pelo volume mensal (t/mês); distâncias em linha reta em km.", "Custo de transporte = volume × frete × distância de cada ponto ao terreno.",
                               "Carga × distância = viagens por dia × distância retilínea entre os centros das zonas (Anexo D)."],
                 "fontes": ["Tabelas 13, 14, 29 e 30 do pacote de dados do G3; planilha D10_localizacao_layout.xlsx."], "responsavel": RESPONSAVEL[RD]},
       "corpo": [
           {"h1": "1 Introdução"},
           {"p": "Este documento avalia a localização escolhida pela empresa (Terreno A, Juazeiro) por dois métodos, o centro de gravidade e a pontuação ponderada, analisa o layout proposto pela carga × distância e apresenta o layout do canteiro para a fase de montagem dos equipamentos de processo."},
           {"h1": "2 Centro de gravidade e custo de transporte"},
           {"p": f"Ponderado pelo volume, o centro de gravidade fica em x = {br(cg[0],1)} km e y = {br(cg[1],1)} km, entre os fornecedores do Vale do São Francisco e os clientes de Salvador e Recife (Figura 1). Ele não coincide com nenhum terreno: o mais próximo é o Terreno C ({br(dc['TC'],1)} km), contra {br(dc['TA'],1)} km do A e {br(dc['TB'],1)} km do B. A distância ao centro de gravidade, porém, não considera o frete diferente de cada ponto; por isso a Tabela 1 compara o custo mensal de transporte."},
           {"figura": {"arquivo": "../figuras/d10_mapa_localizacao.png", "titulo": "Pontos logísticos, terrenos candidatos e centro de gravidade", "fonte": "elaborado pelo grupo a partir da tabela 29.", "ratio": 0.79, "largura": 500}},
           {"tabela": {"titulo": "Custo mensal de transporte e pontuação ponderada por terreno", "cab": ["Terreno", "Distância ao CG (km)", "Custo de transporte (R$/mês)", "Pontuação ponderada"],
                       "linhas": [[f"Terreno {k[-1]}", br(dc[k], 1), br(ct[k]), br(sc[k[-1]], 2)] for k in ["TA", "TB", "TC"]], "fonte_txt": "elaborado pelo grupo a partir das tabelas 29 e 30."}},
           {"p": f"O Terreno A tem o menor custo de transporte ({rs(ct['TA'])} por mês), apenas {rs(ct['TB']-ct['TA'])} abaixo do B, e a maior pontuação ponderada ({br(sc['A'],2)} contra {br(sc['B'],2)} do B e {br(sc['C'],2)} do C). A escolha da empresa é, portanto, a melhor pelos dois métodos. O Terreno C, embora mais perto do centro de gravidade, custa {rs(ct['TC']-ct['TA'])} a mais por mês porque fica longe dos fornecedores, que concentram o maior volume."},
           {"h2": "2.1 Análise de sensibilidade"},
           {"p": f"A vantagem do A sobre o B na pontuação é de apenas {br(sc['A']-sc['B'],2)} ponto. Transferir {br(X['delta_empate'],0)} pontos de peso do fator acesso rodoviário e portuário (em que A é melhor) para incentivos fiscais (em que B é melhor) basta para empatar os dois terrenos. A decisão é robusta no custo de transporte, mas sensível aos pesos qualitativos: se os incentivos fiscais de Petrolina forem decisivos para a diretoria, o Terreno B passa a ser uma alternativa equivalente."},
           {"h1": "3 Layout e fluxo"},
           {"p": f"A Figura 2 mostra a planta em escala com o centro de cada zona e os fluxos diários. A carga × distância do layout proposto é de {br(lay['base'])} m·viagem por dia. A troca de posição entre recepção (REC) e seleção (SEL) reduz esse valor para {br(lay['rec_sel'])}, uma economia de {pc(1-lay['rec_sel']/lay['base'])}, porque aproxima a recepção das docas (665 viagens por dia) e do retorno da embalagem (595 viagens). Entre todas as trocas possíveis entre zonas de processo, testadas por script, essa é a melhor; a segunda melhor é {lay['best'][1]} ↔ {lay['best'][2]}."},
           {"figura": {"arquivo": "../figuras/d10_planta_fluxos.png", "titulo": "Planta em escala com as zonas e o diagrama de fluxo", "fonte": "elaborado pelo grupo a partir das tabelas 13 e 14.", "ratio": 0.87, "largura": 520}},
           {"p": "Antes de alterar o projeto, é preciso verificar se a seleção óptica cabe no espaço da recepção, se a área molhada da lavagem pode ficar junto ao hidrotérmico sem prejudicar a drenagem e se a mudança afeta a sequência sanitária exigida para exportação. Como o piso industrial ainda não começou, a troca ainda é possível sem retrabalho."},
           {"h1": "4 Layout do canteiro na fase de montagem"},
           {"p": "Na fase de montagem dos equipamentos de processo, o canteiro precisa receber carretas com tanques, compressores e painéis isotérmicos, estocá-los cobertos e içá-los para dentro do galpão. A Figura 3 apresenta a proposta: acesso de caminhões pelo pátio ao sul, área de descarga junto às docas, estoque coberto dos equipamentos na área do canteiro a oeste, guindaste posicionado entre as docas e o galpão para cobrir a maior parte da área de processo, e áreas de vivência afastadas da movimentação de cargas."},
           {"figura": {"arquivo": "../figuras/d10_canteiro.png", "titulo": "Layout do canteiro na fase de montagem", "fonte": "elaborado pelo grupo.", "ratio": 0.87, "largura": 520}},
           {"h1": "5 Conclusão"},
           {"p": "O Terreno A é a melhor localização pelos dois métodos, com uma margem estreita sobre o B na pontuação ponderada. No layout, a troca entre recepção e seleção reduz em cerca de 7% a movimentação interna e deve ser avaliada pela engenharia antes do início do piso industrial."},
       ],
       "referencias": ["MAGALHÃES, L. ENG037 Trabalho Final: Comitê de PCP. Enunciado geral e dossiê do Grupo 3. Salvador: UFBA, 2026."]}
gerar("D10_localizacao_layout", d10)

# ============================ D11 ============================
IND = [("Avanço físico", "Σ qtd executada ÷ qtd orçada (por atividade e fase)", "Semanal", "100% do previsto", "Engenharia de planejamento"),
       ("IDP", "VA ÷ VP", "Semanal", "≥ 0,95", "Engenharia de planejamento"),
       ("IDC", "VA ÷ CR (custo direto)", "Mensal", "≥ 0,98", "Controladoria da obra"),
       ("Estimativa no término", "Orçamento ÷ IDC", "Mensal", "≤ R$ 28,1 mi", "Controladoria da obra"),
       ("PPC", "Pacotes concluídos (≥ 97% da meta) ÷ planejados", "Semanal", "≥ 80%", "Coordenação de PCP"),
       ("Restrições removidas no prazo", "Restrições removidas até a data necessária ÷ total", "Semanal", "≥ 90%", "Coordenação de PCP"),
       ("RUP real ÷ orçada", "(Hh normais + extras) ÷ qtd executada ÷ RUP orçada", "Semanal", "≤ 1,05", "Encarregado da frente"),
       ("Absenteísmo", "1 − presentes ÷ previstos", "Semanal", "≤ 5%", "RH"),
       ("Pedidos atrasados", "Pedidos com data prometida vencida e sem entrega", "Semanal", "0 itens A", "Suprimentos"),
       ("Disponibilidade de equipamentos", "1 − (corretiva + preventiva) ÷ horas disponíveis", "Semanal", "≥ 95%", "Engenharia de equipamentos"),
       ("Utilização de equipamentos", "Horas operando ÷ horas disponíveis", "Semanal", "≥ 75%", "Engenharia de equipamentos"),
       ("FVS reprovadas", "FVS reprovadas ÷ FVS realizadas", "Semanal", "≤ 5%", "Qualidade"),
       ("Taxa de ocorrências de segurança", "Ocorrências ÷ Hh trabalhadas × 10⁶", "Mensal", "0 com afastamento", "Segurança do trabalho")]
FVS1 = [("Base e sub-base compactadas, sem bolsões", "Visual e ensaio de compactação", "≥ 95% do Proctor"), ("Lona plástica e juntas de dilatação posicionadas", "Visual", "Conforme projeto"),
        ("Tela soldada e fibras na posição", "Trena e espaçadores", "Cobrimento 3 cm ± 0,5"), ("Concreto recebido", "Nota fiscal e slump", "fck 30 MPa; slump 10 ± 2 cm"),
        ("Planicidade e nivelamento", "Régua de 3 m / nível a laser", "FF ≥ 35; FL ≥ 25"), ("Aplicação do endurecedor e acabamento", "Visual", "Sem desplacamento"),
        ("Corte das juntas", "Trena", "Até 24 h; profundidade 1/3 da espessura"), ("Cura", "Visual e registro", "Mínimo 7 dias úmida")]
FVS2 = [("Tubos e conexões conforme especificação", "Nota fiscal e marcação", "Material e diâmetro do projeto"), ("Suportes e espaçamento", "Trena", "Conforme projeto, ± 5 cm"),
        ("Soldas/brasagens", "Visual e inspeção 10%", "Sem porosidade ou trinca"), ("Teste de estanqueidade", "Pressurização com nitrogênio", "Sem queda de pressão em 24 h"),
        ("Vácuo do sistema", "Vacuômetro", "≤ 500 mícrons"), ("Isolamento térmico contínuo", "Visual", "Sem frestas; barreira de vapor íntegra"),
        ("Identificação das linhas", "Visual", "Cor e sentido de fluxo"), ("Limpeza e proteção", "Visual", "Sem resíduos no interior")]
RD = "D11"
d11 = {"rosto": {"grupo": GRUPO, "titulo": "D11 · Plano de controle", "subtitulo": "Indicadores, rotina do Last Planner e fichas de verificação de serviço", "data": DATA,
                 "premissas": ["Fórmulas dos indicadores conforme Anexo D do enunciado.", "Metas definidas pelo grupo a partir da meta de PPC da empresa (80%) e do diagnóstico de 13/11/2026.",
                               "Os indicadores são calculados no sistema do grupo (abas Dashboard e Análises)."],
                 "fontes": ["Enunciado (Anexo D); tabelas 01, 15 a 24; sistema de PCP do grupo."], "responsavel": RESPONSAVEL[RD]},
       "corpo": [
           {"h1": "1 Indicadores de controle"},
           {"p": "O plano de controle define o que é medido, como, com que frequência, qual é a meta e quem responde por cada indicador. A Tabela 1 reúne os indicadores acompanhados pelo sistema. As metas de prazo e custo foram fixadas próximas de 1, porque o diagnóstico de 13/11/2026 mostrou IDP de 0,59 e IDC de 0,95, e a meta de PPC segue o valor da empresa."},
           {"tabela": {"titulo": "Indicadores do plano de controle", "cab": ["Indicador", "Fórmula", "Frequência", "Meta", "Dono"], "linhas": [list(x) for x in IND],
                       "larg": [2.2, 3.6, 1.1, 1.4, 2], "alin": [None, "L", None, None, "L"], "fonte_txt": "elaborado pelo grupo com base no Anexo D do enunciado."}},
           {"h1": "2 Rotina semanal do Last Planner"},
           {"p": "A rotina semanal organiza o planejamento em três níveis. O plano de longo prazo é a linha de base (D2 e D3). O lookahead de seis semanas identifica as restrições de cada pacote (projeto, material, equipamento, equipe, licença e serviço anterior) e atribui um responsável e uma data de remoção. O plano semanal só pode incluir pacotes sem restrição pendente, ou seja, que passaram de deve para pode."},
           {"lista": ["Segunda-feira, 7h30: reunião de compromisso com os encarregados; só entram pacotes liberados no lookahead, com meta em quantidade.",
                      "Diariamente: lançamento do RDO de mão de obra, produção e equipamentos no sistema até as 18h.",
                      "Quarta-feira: revisão do lookahead de seis semanas e da lista de restrições com suprimentos, engenharia e RH.",
                      "Sexta-feira, 16h: fechamento do plano semanal, cálculo do PPC (pacote concluído com pelo menos 97% da meta) e registro padronizado da causa de cada pacote não concluído.",
                      "Sexta-feira: análise do Pareto das causas das últimas quatro semanas e definição de uma ação para a causa principal, com dono e prazo."], "numerada": True},
           {"h1": "3 Fichas de verificação de serviço"},
           {"p": "As fichas abaixo foram preparadas para os dois serviços críticos que começam após a data de status: o piso industrial (A12), que libera a montagem das câmaras, e a tubulação frigorífica (A26), a atividade mais longa do caminho crítico. Cada lote só é liberado para o serviço seguinte com a ficha aprovada; um item reprovado abre uma não conformidade e uma nova inspeção."},
           {"tabela": {"titulo": "FVS do piso industrial de concreto (A12)", "cab": ["Item verificado", "Método", "Critério de aceitação"], "linhas": [list(x) for x in FVS1],
                       "larg": [3.2, 2.4, 2.6], "alin": [None, "L", "L"], "fonte_txt": "elaborado pelo grupo."}},
           {"tabela": {"titulo": "FVS da tubulação frigorífica e isolamento (A26)", "cab": ["Item verificado", "Método", "Critério de aceitação"], "linhas": [list(x) for x in FVS2],
                       "larg": [3.2, 2.4, 2.6], "alin": [None, "L", "L"], "fonte_txt": "elaborado pelo grupo."}},
           {"p": "Cada ficha registra ainda a data, a zona, o lote, o encarregado, o inspetor, o número de itens verificados e reprovados, o resultado e as horas de retrabalho estimadas, que são os mesmos campos da tela de FVS do sistema."},
       ],
       "referencias": ["MAGALHÃES, L. ENG037 Trabalho Final: Comitê de PCP. Enunciado geral e dossiê do Grupo 3. Salvador: UFBA, 2026.",
                       "BALLARD, G. The Last Planner System of production control. 2000. Tese (Doutorado), University of Birmingham, Birmingham, 2000."]}
gerar("D11_plano_de_controle", d11)

# ============================ D12 ============================
c1, c2, c3 = [CE["cenarios"][k] for k in CE["cenarios"]]
he = AN["hora_extra"]; pz = AN["prazo"]
RD = "D12"
d12 = {"rosto": {"grupo": GRUPO, "titulo": "D12 · Estratégia de PCP", "subtitulo": "Decisões do grupo e seus trade-offs", "data": DATA,
                 "premissas": ["Multa de R$ 18.300 por dia útil após 23/03/2027 e ganho operacional de R$ 30.900 por dia útil em operação (tabela 01).",
                               "Previsão de término feita com a rede da linha de base, o avanço real em 13/11/2026 e a produtividade real das atividades em andamento.",
                               "Custos de reforço com premissas explícitas: adicional noturno de 20%, perda de produtividade noturna de 10%, iluminação, supervisão e diligenciamento."],
                 "fontes": ["Tabelas 01, 04, 05, 07, 15 a 21; scripts analise.py e cenarios_custos.py do repositório."], "responsavel": RESPONSAVEL[RD]},
       "corpo": [
           {"h1": "1 Situação de partida"},
           {"p": f"Na data de status, a obra tem {pc(AN['evm']['VA']/AN['evm']['O'])} de avanço físico contra {pc(AN['evm']['VP']/AN['evm']['O'])} previstos (IDP de {br(AN['evm']['IDP'],2)}) e IDC de {br(AN['evm']['IDC'],2)}. Se nada mudar, a unidade fica pronta em {pz['fim_previsto'][8:10]}/{pz['fim_previsto'][5:7]}/{pz['fim_previsto'][:4]}, {int(pz['atraso_vs_base_du'])} dias úteis depois da linha de base e {int(pz['atraso_vs_contrato_du'])} depois da data contratual, com multa de {rs(pz['multa_rs'])}. O caminho crítico passa agora pelo fim da cobertura (A10), pelo piso industrial (A12, ainda não iniciado), pelos painéis das câmaras (A23), pela tubulação frigorífica (A26), pelo comissionamento (A35), pela licença de operação (A37) e pela partida assistida (A38)."},
           {"h1": "2 Regime de trabalho e recuperação do prazo"},
           {"p": f"Três formas de recuperar prazo foram comparadas. A hora extra foi descartada: o histórico mostra que, nos dias com hora extra, a RUP real ficou {br(he['rup_rel_com_HE'],2)} vezes a orçada, contra {br(he['rup_rel_sem_HE'],2)} vezes nos dias sem hora extra, e as {br(he['hh_extras_total'])} horas extras já custaram {rs(he['custo_adicional_HE'])} de adicional sem efeito visível no avanço. O reforço de equipe no mesmo turno esbarra no limite de 130 pessoas no canteiro. A opção escolhida é um segundo turno nas duas atividades críticas de maior duração (A12 e A26), que dobra a produção diária sem aumentar o efetivo simultâneo dessas frentes, combinado com a antecipação da montagem das câmaras (início de A23 dez dias úteis após o início do piso, em vez de vinte), concretando primeiro a área das câmaras."},
           {"tabela": {"titulo": "Comparação dos três cenários", "cab": ["Item", "1. Seguir como está", "2. Recuperar o prazo", "3. Replanejar"],
                       "linhas": [["Término previsto", *[f"{c['fim'][8:10]}/{c['fim'][5:7]}/{c['fim'][:4]}" for c in (c1, c2, c3)]],
                                  ["Atraso sobre o contrato (du)", *[c["atraso_contrato_du"] for c in (c1, c2, c3)]],
                                  ["Custo adicional (R$)", *[br(c["custo_adicional"]) for c in (c1, c2, c3)]],
                                  ["Multa (R$)", *[br(c["multa"]) for c in (c1, c2, c3)]],
                                  ["Ganho operacional perdido (R$)", *[br(c["ganho_perdido_vs_contrato"]) for c in (c1, c2, c3)]],
                                  ["Administração local extra (R$)", *[br(c["adm_local_extra_vs_base"]) for c in (c1, c2, c3)]],
                                  ["Impacto total (R$)", *[br(c["impacto_total"]) for c in (c1, c2, c3)]]],
                       "larg": [2.6, 1.6, 1.6, 1.6], "fonte_txt": "elaborado pelo grupo (cenarios_custos.py). Ganho negativo = ganho obtido por entregar antes do contrato."}},
           {"p": f"O cenário 2 custa {rs(c2['custo_adicional'])} a mais, mas evita {rs(c1['multa'])} de multa e {rs(c1['ganho_perdido_vs_contrato'])} de ganho operacional perdido, com impacto total de {rs(c2['impacto_total'])} contra {rs(c1['impacto_total'])} do cenário 1. Cada dia útil recuperado vale {rs(18300+30900)} (multa mais ganho operacional), enquanto o reforço custa cerca de {rs(c2['custo_adicional']/(c1['fim_du']-c2['fim_du']))} por dia recuperado. O trade-off principal é o risco: o cenário 2 deixa só dois dias úteis de folga e depende das entregas do fornecedor F10. O pico de efetivo diurno, mesmo após o nivelamento das atividades não críticas, chega a {c2['pico_nivelado']} pessoas, o que exige ampliar temporariamente as áreas de vivência ou passar também instalações não críticas para o segundo turno."},
           {"h1": "3 Política de compras"},
           {"p": "Os itens da classe A (estrutura metálica, linha de seleção, compressores, telhas, tanques e painéis) somam 78% do custo de insumos e devem ser comprados por data-limite (data de uso menos lead time menos cinco dias úteis de margem), com diligenciamento semanal e inspeção na fábrica para os equipamentos de processo. O fornecedor F10, responsável por cerca de R$ 10,3 milhões em equipamentos, tem atraso médio de 10,9 dias úteis e cinco pedidos vencidos na data de status; um atraso dessa ordem nos tanques ou na linha de seleção passa a ser crítico no cenário 2. Os itens das classes B e C podem seguir compra programada por reposição, sem frete expresso, que só deve ser usado quando o dia recuperado valer mais que o frete."},
           {"h1": "4 Turnos da operação"},
           {"p": "A nova unidade foi projetada para dois turnos de 8 horas. Com os tanques e o recurso de paletização adicionais propostos no D9, os dois turnos atendem às 42.000 caixas por dia do pico. Fora da safra, a demanda cai a menos de um terço do pico, e a recomendação é operar em um turno, com mão de obra sazonal recrutada para a safra. Um terceiro turno no hidrotérmico é a alternativa ao investimento nos tanques, mas exige um pulmão refrigerado antes da embalagem e equipe noturna especializada, o que o grupo considera mais arriscado para um produto perecível."},
           {"h1": "5 Decisão"},
           {"p": "O grupo recomenda o cenário 2, recuperar o prazo, com quatro condições: segundo turno em A12 assim que A10 for concluída e em A26 desde o início; concretagem da área das câmaras antes do restante do piso; diligenciamento semanal do fornecedor F10 com plano B para os tanques; e plano semanal que só comprometa pacotes sem restrição. Se até meados de dezembro o F10 confirmar atraso superior a dez dias úteis nos tanques, a decisão deve ser revista em favor do cenário 3, com renegociação da data contratual."},
       ],
       "referencias": ["MAGALHÃES, L. ENG037 Trabalho Final: Comitê de PCP. Enunciado geral e dossiê do Grupo 3. Salvador: UFBA, 2026."]}
gerar("D12_estrategia_PCP", d12)
