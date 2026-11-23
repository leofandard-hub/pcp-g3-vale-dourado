"""Gera (1) o kit de lançamento da semana de campo dividido entre Léo e Raphael e
(2) o guia de resolução do caderno M1–M6 (uso interno: cada um refaz à mão).
Uso: python scripts/guias.py
"""
import json, math, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import calculos as C
import semana_campo as S

R = C.RAIZ; DOCS = R / "docs"; TMP = DOCS / "_build"; TMP.mkdir(exist_ok=True)
X = json.loads((DOCS / "_d9_d10.json").read_text())
br = lambda v, d=1: (f"{v:,.{d}f}").replace(",", "X").replace(".", ",").replace("X", ".")
dt = lambda s: "/".join(reversed(s.split("-")))


def limpa(x):
    if isinstance(x, dict): return {k: limpa(v) for k, v in x.items()}
    if isinstance(x, list): return [limpa(v) for v in x]
    if x is None or (isinstance(x, float) and math.isnan(x)): return ""
    return x


def gerar(nome, spec):
    j = TMP / f"{nome}.json"; j.write_text(json.dumps(limpa(spec), ensure_ascii=False))
    subprocess.run(["node", str(R / "scripts/gerar_docx.js"), str(j), str(TMP / f"{nome}.docx")], check=True, capture_output=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(DOCS), str(TMP / f"{nome}.docx")], check=True, capture_output=True)
    print("ok", nome)


def num(v, d=1):
    if v is None or v == "" or (isinstance(v, float) and math.isnan(v)): return ""
    if isinstance(v, (int,)) or float(v).is_integer(): return str(int(v)) if abs(v) < 1000 else br(v, 0)
    return br(v, d)


def tab(titulo, cols, linhas, fonte="dossiê do G3, anexo de boletins."):
    return {"tabela": {"titulo": titulo, "cab": cols, "linhas": linhas, "fonte": 16, "fonte_txt": fonte}}

# =================== KIT DA SEMANA DE CAMPO ===================
mo, pr, eq, cu = S.mao_de_obra, S.producao, S.equipamentos, S.custos
def bloco_dias(dias):
    out = []
    for d in dias:
        out.append({"h2": f"{dt(d)} · RDO"})
        out.append(tab(f"Tela RDO · mão de obra · {dt(d)}", ["data", "id_atividade", "funcao", "efetivo_previsto", "efetivo_presente", "horas_normais", "horas_extras"],
                       [[dt(d), r.id_atividade, r.funcao, r.efetivo_previsto, r.efetivo_presente, num(r.horas_normais), num(r.horas_extras)] for r in mo[mo.data == d].itertuples()]))
        out.append(tab(f"Tela RDO · produção e ocorrências · {dt(d)}", ["data", "id_atividade", "quantidade_executada", "demais campos"],
                       [[dt(d), r.id_atividade, num(r.quantidade_executada), "deixar 0 / vazio"] for r in pr[pr.data == d].itertuples()]))
        out.append(tab(f"Tela Equipamentos · {dt(d)}", ["id_equipamento", "id_atividade", "h disp.", "operando", "corretiva", "preventiva", "ociosas", "falhas", "horímetro"],
                       [[r.id_equipamento, r.id_atividade, 8, num(r.horas_operando), num(r.horas_manutencao_corretiva), num(r.horas_manutencao_preventiva), num(r.horas_ociosas),
                         int(r.numero_falhas), num(r.horimetro)] for r in eq[eq.data == d].itertuples()], "dossiê do G3; data = " + dt(d) + " em todas as linhas."))
    return out

hh = lambda dias: (mo[mo.data.isin(dias)].horas_normais + mo[mo.data.isin(dias)].horas_extras).sum()
L_DIAS, R_DIAS = S.DIAS[:3], S.DIAS[3:]
pl = S.plano
kit = {"rosto": {"grupo": "Grupo 3 · Vale Dourado Frutas · Léo Fandard e Raphael", "titulo": "Kit de lançamento da semana de campo",
                 "subtitulo": "Boletins de 09 a 13/11/2026 divididos entre os integrantes", "data": "novembro de 2026",
                 "premissas": ["Cada integrante lança a sua parte no sistema, aba Lançamentos, com o próprio nome no campo 'Quem lança'.",
                               "Os campos têm o mesmo nome das colunas das tabelas (DICIONARIO.md). Números com vírgula ou ponto, conforme o navegador aceitar.",
                               "Ao final, conferir na aba 'Dados e configuração': 55.086,8 Hh e R$ 11.689.047,31 até 13/11/2026."],
                 "fontes": ["Dossiê do Grupo 3, anexo B1 a B10."], "responsavel": "Léo Fandard (parte 1) e Raphael (parte 2)"},
       "corpo": [{"h1": "Parte 1 · Léo Fandard"},
                 {"p": f"Dias 09, 10 e 11/11 (RDO de mão de obra, produção e equipamentos) e o plano semanal da semana 46 com o fechamento de sexta. Total de Hh desta parte: {br(hh(L_DIAS))}."},
                 tab("Tela Plano semanal e fechamento · semana 2026-S46 (lançar após o fechamento de 13/11)",
                     ["id_pacote", "semana", "data_inicio_semana", "id_atividade", "encarregado", "unidade", "meta", "realizada", "concluido", "causa"],
                     [[r.id_pacote, r.semana, "09/11/2026", r.id_atividade, r.encarregado, {"A25": "un"}.get(r.id_atividade, "m²"), num(r.meta_quantidade, 2), num(r.quantidade_realizada),
                       r.concluido, r.causa_nao_cumprimento or ""] for r in pl.itertuples()]),
                 *bloco_dias(L_DIAS),
                 {"quebra": True}, {"h1": "Parte 2 · Raphael"},
                 {"p": f"Dias 12 e 13/11 (RDO), suprimentos, recebimento, requisições de material, FVS, restrições e fechamento de custos. Total de Hh desta parte: {br(hh(R_DIAS))}; custo direto: R$ {br(cu[cu.categoria != 'INDIRETO'].valor_rs.sum(), 2)}."},
                 *bloco_dias(R_DIAS),
                 {"h2": "Suprimentos (B7)"},
                 tab("Tela Pedido de compra (comprador Carla Mota; frete 0; frete_expresso 0)", ["id_pedido", "id_material", "id_atividade", "id_fornecedor", "tipo_pedido", "data_requisicao", "data_pedido",
                                                                                          "data_necessidade_obra", "data_prometida", "quantidade", "preço unit. (R$)"],
                     [["PC0118", "TFR", "A26", "F10", "PROGRAMADO", "09/11/2026", "09/11/2026", "29/12/2026", "15/12/2026", "672,9", "144,56"],
                      ["PC0120", "EVP", "A27", "F10", "REPOSICAO", "06/11/2026", "09/11/2026", "05/11/2026", "11/12/2026", "2", "42.838,90"],
                      ["PC0079", "TIN", "A16", "F12", "PROGRAMADO", "05/11/2026", "11/11/2026", "27/11/2026", "23/11/2026", "538,6", "21,07"]]),
                 tab("Tela Recebimento / requisição de material (tabela 19)", ["data", "id_material", "tipo_movimento", "quantidade", "id_atividade", "id_pedido", "documento"],
                     [["13/11/2026", "TLH", "ENTRADA", "496,8", "", "PC0133", "NF-PC0133"]] +
                     [["13/11/2026", m, "SAIDA", q, a, "", f"RM-{a}-{m}-2026-S46"] for m, a, q in
                      [("ARG", "A15", "2.639,396"), ("BRI", "A13", "229,426"), ("CER", "A15", "155,750"), ("PAV", "A13", "1.146,063"), ("PFE", "A11", "461,042"), ("TLH", "A10", "229,815")]]),
                 {"h2": "Qualidade, segurança e restrições (B8)"},
                 tab("Tela FVS", ["id_inspecao", "data", "id_atividade", "id_zona", "lote", "encarregado", "itens verif.", "itens reprov.", "resultado", "hh retrab."],
                     [["FVS0056", "09/11/2026", "A11", "GALPAO", 5, "Lúcia Farias", 8, 0, "APROVADO", 0], ["FVS0057", "12/11/2026", "A15", "APOIO", 8, "Osvaldo Lins", 14, 0, "APROVADO", 0],
                      ["FVS0058", "13/11/2026", "A13", "PATIO", 4, "Jair Bispo", 11, 0, "APROVADO", 0]]),
                 {"p": "Ocorrências de segurança: nenhuma na semana (não lançar nada)."},
                 tab("Tela Restrições (atualizações)", ["id_restricao", "id_atividade", "tipo", "responsavel", "identificação", "necessária", "remoção", "status"],
                     [[r, a_, t_, resp, i_, n_, rm, st] for r, a_, t_, resp, i_, n_, rm, st in [
                         ("R029", "A16", "PROJETO", "Engenharia", "15/10/2026", "17/11/2026", "10/11/2026", "REMOVIDA"), ("R030", "A16", "EQUIPE", "RH", "25/09/2026", "17/11/2026", "11/11/2026", "REMOVIDA"),
                         ("R052", "A24", "PROJETO", "Engenharia", "18/09/2026", "10/11/2026", "", "EM_ANDAMENTO"), ("R054", "A24", "EQUIPAMENTO", "Suprimentos", "21/09/2026", "10/11/2026", "", "EM_ANDAMENTO"),
                         ("R066", "A28", "EQUIPAMENTO", "Suprimentos", "26/10/2026", "17/11/2026", "12/11/2026", "REMOVIDA"), ("R068", "A29", "EQUIPE", "RH", "15/10/2026", "17/11/2026", "12/11/2026", "REMOVIDA"),
                         ("R070", "A30", "EQUIPE", "RH", "15/10/2026", "30/11/2026", "13/11/2026", "REMOVIDA"), ("R071", "A31", "PROJETO", "Engenharia", "26/10/2026", "17/11/2026", "11/11/2026", "REMOVIDA"),
                         ("R094", "A24", "MATERIAL", "Suprimentos", "07/10/2026", "10/11/2026", "", "EM_ANDAMENTO")]],
                     "dossiê B8; 'BLOQUEIA' no boletim = status EM_ANDAMENTO (não removida)."),
                 {"h2": "Fechamento de custos (B9)"},
                 tab("Tela Custos (data 13/11/2026 em todas as linhas)", ["id_lancamento", "codigo_eap", "id_atividade", "categoria", "valor_rs", "documento"],
                     [[r.id_lancamento, r.codigo_eap, r.id_atividade or "", r.categoria, br(r.valor_rs, 2), d] for r, d in zip(cu.itertuples(),
                      ["MED-A10-2026-S46", "MED-A11-2026-S46", "FOLHA-2026-S46", "FOLHA-2026-S46", "RM-A15-ARG-2026-S46", "RM-A15-CER-2026-S46", "RM-A11-PFE-2026-S46", "RM-A13-PAV-2026-S46",
                       "RM-A13-BRI-2026-S46", "RM-A10-TLH-2026-S46", "LOC-MUN-01-2026-S46", "LOC-CAM-01-2026-S46", "LOC-CAM-02-2026-S46", "LOC-ROL-01-2026-S46", "LOC-RET-01-2026-S46",
                       "LOC-PTA-01-2026-S46", "LOC-PTA-02-2026-S46", "LOC-PTA-03-2026-S46", "LOC-PTA-04-2026-S46", "ADM-2026-S46"])]),
                 {"h1": "Conferência final"},
                 {"p": "Depois das duas partes lançadas, a aba 'Dados e configuração' do sistema deve mostrar 55.086,8 Hh e R$ 11.689.047,31 até 13/11/2026, com ✔ nas seis linhas. O PPC da semana 46 deve dar 60% (3 de 5 pacotes) e o dashboard em 13/11 deve mostrar IDP 0,59 e IDC 0,95."}]}
gerar("kit_semana_de_campo", kit)

# =================== GUIA DO CADERNO ===================
sub = ["A23", "A24", "A25", "A26", "A27", "A28", "A29", "A30", "A31", "A35", "A36"]
ES, EF, LS, LF, fim = C.cpm(sub, C.D, C.tab["04_dependencias"])
efm = {"A23": 25, "A24": 11, "A25": 19, "A26": 24, "A27": 15, "A28": 17, "A29": 18, "A30": 13, "A31": 16, "A35": 23, "A36": 26}
qm = {"A23": (6400, 1.21), "A24": (22, 48.4), "A25": (9, 286), "A26": (2600, 3.74), "A27": (16, 96.8), "A28": (4, 330), "A29": (180, 14.3), "A30": (28, 35.2), "A31": (900, 2.42), "A35": (28, 35.2), "A36": (30, 44)}
def hist(es):
    return [sum(efm[i] * max(0, min(es[i] + C.D[i] - 1, w * 5 + 5) - max(es[i], w * 5 + 1) + 1) for i in sub) / 5 for w in range(math.ceil(fim / 5))]
h0 = hist(ES); esn = dict(ES); esn["A27"], esn["A30"] = 31, 23; hn = hist(esn)
m4 = [("1.1", 658, 1.0, 1.0, 667), ("1.2", 1122, 1.0, 1.0, 1301), ("1.3", 9658, .904, .681, 6879), ("1.4", 2308, .817, 0, 0), ("1.5", 11728, .101, 0, 0), ("1.6", 2100, .865, .814, 1721), ("1.7", 541, 0, 0, 0)]
T = [sum(x[1] for x in m4), sum(x[1] * x[2] for x in m4), sum(x[1] * x[3] for x in m4), sum(x[4] for x in m4)]
cap = X["cap"]; m3 = X["m3"]; cg = X["cg"]; ct = X["custo_transp"]; sc = X["score"]; lay = X["layout"]
zon = C.tab["13_layout_zonas"].set_index("id_zona"); flu = C.tab["14_fluxo_zonas"]
cen = {z: (r.x_m + r.largura_x_m / 2, r.y_m + r.comprimento_y_m / 2) for z, r in zon.iterrows()}
guia = {"rosto": {"grupo": "Grupo 3 · Vale Dourado Frutas · Léo Fandard e Raphael", "titulo": "Guia de resolução do caderno manuscrito",
                  "subtitulo": "Uso interno para estudo: NÃO entregar. Cada um refaz as contas e os desenhos à mão.", "data": "novembro de 2026",
                  "premissas": ["Divisão: Léo faz M1, M2 e M4; Raphael faz M3, M5 e M6. Cada um assina as suas folhas.",
                                "Papel A4 quadriculado ou milimetrado, caneta, contas com unidade e 2 a 3 linhas de interpretação no fim de cada folha.",
                                "M1, M3 e M4 precisam bater com o sistema: os valores abaixo são os do sistema."],
                  "fontes": ["Dossiê do Grupo 3 (seção 6) e Anexo D do enunciado."], "responsavel": "Léo Fandard e Raphael"},
        "corpo": [
            {"h1": "M1 · Rede e caminho crítico (Léo)"},
            {"p": "Duração = arredondar para cima (quantidade × RUP ÷ (efetivo × 8)). Ida: TI → início = término da predecessora + 1 + defasagem; II → início = início da predecessora + defasagem. Volta: o contrário, partindo do fim da sub-rede. Folga = LS − ES."},
            tab("Durações, datas e folgas da sub-rede", ["Ativ.", "Conta da duração", "Dur.", "ES", "EF", "LS", "LF", "Folga"],
                [[i, f"{num(qm[i][0])} × {num(qm[i][1], 3)} ÷ ({efm[i]} × 8) = {br(qm[i][0] * qm[i][1] / (efm[i] * 8), 2)}", C.D[i], ES[i], EF[i], LS[i], LF[i], LS[i] - ES[i]] for i in sub],
                "elaborado pelo grupo; confere com o sistema."),
            {"p": f"Duração da sub-rede: {fim} du. Caminho crítico (folga zero): A23 → A26 → A35 → A36. Atividade não crítica a atrasar primeiro: A28 (tanques hidrotérmicos, folga de {LS['A28'] - ES['A28']} du e equipe de 17 pessoas): é a de maior folga, e atrasá-la libera equipe sem mexer no prazo. Desenho: atividade no nó, cada caixa com ES, EF, LS, LF e folga, setas com o tipo de ligação (II+15 etc.)."},
            {"h1": "M2 · Histograma e nivelamento (Léo)"},
            {"p": "Para cada semana (blocos de 5 du), efetivo médio = Σ efetivo × dias da atividade dentro da semana ÷ 5. Homens-dia = Σ efetivo × duração."},
            tab("Efetivo médio por semana (pessoas)", ["Semana"] + [str(k + 1) for k in range(len(h0))],
                [["Datas cedo"] + [num(round(x, 1)) for x in h0], ["Nivelado"] + [num(round(x, 1)) for x in hn]], "elaborado pelo grupo."),
            {"p": f"Pico {num(max(h0))} pessoas (semana 3), média {br(sum(h0) / len(h0))} pessoas, total {br(sum(efm[i] * C.D[i] for i in sub), 0)} homens-dia. Nivelamento: deslocar A27 do du 13 para o 31 e A30 do du 9 para o 23, ambas dentro da folga: o pico cai para {num(max(hn))} e o prazo continua {fim} du. O pico dimensiona vestiários, refeitório, sanitários, EPIs e transporte (NR-18); o canteiro comporta 130 pessoas."},
            {"h1": "M3 · Takt, capacidade e OEE (Raphael)"},
            {"p": f"Tempo disponível = 2 turnos × 8 h × 3.600 s × (1 − 0,10) = {br(X['tdisp'], 0)} s/dia. Takt = {br(X['tdisp'], 0)} ÷ 42.000 = {br(X['takt'], 3)} s/caixa. Capacidade = recursos × tempo disponível ÷ ciclo × OEE; recursos necessários = arredondar para cima (42.000 × ciclo ÷ (tempo disponível × OEE))."},
            tab("Capacidade por posto", ["Posto", "OEE prev.", "Capacidade (cx/dia)", "Recursos proj.", "Necessários", "Invest. adicional (R$)"],
                [[c["posto"], br(c["oee"] * 100) + "%", br(c["cap"], 0), c["proj"], c["nec"], br(c["inv"], 0)] for c in cap], "elaborado pelo grupo; confere com o D9."),
            {"p": f"Gargalo: PT03 (hidrotérmico), 31.878 cx/dia. Investimento adicional: 2 tanques (R$ 1.040.000) + 1 paletizadora (R$ 190.000) = R$ 1.230.000. Gráfico: barras da capacidade de cada posto e linha horizontal em 42.000."},
            {"p": f"OEE do turno (PT04, 04/11, turno 2): operando = 6.240 − 651 − 2.411 − 217 = {num(m3['op'])} min; disponibilidade = {num(m3['op'])} ÷ (6.240 − 651) = {br(m3['disp'] * 100)}%; eficiência = 7.641 × 18,5 ÷ 60 ÷ {num(m3['op'])} = {br(m3['efic'] * 100)}%; qualidade = (7.641 − 124,8) ÷ 7.641 = {br(m3['qual'] * 100)}%; OEE = {br(m3['oee'] * 100)}%. Atacar primeiro a disponibilidade (2.411 min de parada não planejada)."},
            {"h1": "M4 · Valor agregado e PPC em 16/10 (Léo)"},
            {"p": "VP = orçamento × % previsto; VA = orçamento × % físico; VPr = VA − VP; VC = VA − CR; IDP = VA ÷ VP; IDC = VA ÷ CR; estimativa no término = orçamento ÷ IDC."},
            tab("Valor agregado por fase (R$ mil)", ["Fase", "VP", "VA", "CR", "VPr", "VC", "IDP", "IDC"],
                [[f, br(o * p, 0), br(o * r, 0), br(c, 0), br(o * r - o * p, 0), br(o * r - c, 0), br(r / p, 2) if p else "–", br(o * r / c, 2) if c else "–"] for f, o, p, r, c in m4] +
                [["Total", br(T[1], 0), br(T[2], 0), br(T[3], 0), br(T[2] - T[1], 0), br(T[2] - T[3], 0), br(T[2] / T[1], 2), br(T[2] / T[3], 2)]], "dossiê, folha M4; elaborado pelo grupo."),
            {"p": f"Estimativa no término = {br(T[0], 0)} ÷ {br(T[2] / T[3], 3)} = R$ {br(T[0] / (T[2] / T[3]), 0)} mil. Quadrante: IDP < 1 e IDC < 1 (atrasado e acima do custo). Fase a investigar primeiro: 1.3 Estrutura e edificação (maior VPr negativo, R$ {br(T[2] - T[1], 0)} mil no total). PPC: S39 2/5 = 40%; S40 2/4 = 50%; S41 1/5 = 20%; S42 3/6 = 50%; período 8/20 = 40%. Pareto: EQUIPAMENTO 4, PRODUTIVIDADE 4, SERVIÇO ANTERIOR 3, MÃO DE OBRA 1. Ação para equipamento: só comprometer pacote com equipamento disponível e preventiva programada. Curva S: marcar à mão os pontos mensais de VP, VA e CR do sistema (Dashboard)."},
            {"h1": "M5 · Localização (Raphael)"},
            {"p": f"Centro de gravidade: x = Σ(x·V) ÷ ΣV = {br(cg[0])} km; y = Σ(y·V) ÷ ΣV = {br(cg[1])} km (ΣV = 18.700 t/mês). Distância CG → terreno: A {br(X['dist_cg']['TA'])} km, B {br(X['dist_cg']['TB'])} km, C {br(X['dist_cg']['TC'])} km. Custo de transporte = Σ V × frete × distância de cada ponto ao terreno: A R$ {br(ct['TA'], 0)}/mês, B R$ {br(ct['TB'], 0)}/mês, C R$ {br(ct['TC'], 0)}/mês. Pontuação ponderada: A {br(sc['A'], 2)}, B {br(sc['B'], 2)}, C {br(sc['C'], 2)}. O Terreno A vence nos dois métodos. Sensibilidade: passar 5 pontos de peso de 'acesso' para 'incentivos fiscais' empata A e B (7,85 cada): decisão sensível. Mapa em escala com os 8 pontos, os 3 terrenos e o CG."},
            {"h1": "M6 · Layout e fluxo (Raphael)"},
            tab("Carga × distância do layout proposto", ["Origem → destino", "Viagens/dia", "|Δx| + |Δy| (m)", "C × D"],
                [[f"{f.id_zona_origem} → {f.id_zona_destino}", f.viagens_dia, br(abs(cen[f.id_zona_origem][0] - cen[f.id_zona_destino][0]) + abs(cen[f.id_zona_origem][1] - cen[f.id_zona_destino][1]), 2),
                  br(f.viagens_dia * (abs(cen[f.id_zona_origem][0] - cen[f.id_zona_destino][0]) + abs(cen[f.id_zona_origem][1] - cen[f.id_zona_destino][1])), 1)] for f in flu.itertuples()],
                "tabelas 13 e 14; centro da zona = canto + metade da largura e do comprimento."),
            {"p": f"Total: {br(lay['base'], 1)} m·viagem/dia. Trocando REC e SEL de lugar: {br(lay['rec_sel'], 1)} (−{br((1 - lay['rec_sel'] / lay['base']) * 100)}%). Vale a pena no papel, mas antes é preciso verificar espaço da seleção óptica, drenagem da área molhada, sequência sanitária e docas. Desenhos: planta em escala com o centro de cada zona, setas com espessura proporcional às viagens e o canteiro da fase de montagem (acesso de caminhões, descarga, estoque coberto dos equipamentos, guindaste e vivência), como na Figura 3 do D10."},
        ]}
gerar("guia_caderno_M1-M6", guia)
