"""Planilhas D9 (dimensionamento da operação) e D10 (localização e layout) + figuras para os PDFs.
Uso: python scripts/docs_d9_d10.py
"""
import sys, json, itertools
from pathlib import Path
import pandas as pd
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.series import SeriesLabel

sys.path.insert(0, str(Path(__file__).parent))
import calculos as C
from docs_util import *

DOCS = C.RAIZ / "docs"; FIG = DOCS / "figuras"; FIG.mkdir(exist_ok=True)
t = C.tab
OUT = {}

# ======================= D9 =======================
dem = t["25_demanda_historica"]; postos = t["26_processo_postos"]; ap = t["27_producao_apontamento"]; os_ = t["28_manutencao_os"]
wb = novo("Dimensionamento da operação", "D9",
          ["Tempo disponível por dia = turnos × horas por turno × 3.600 s × (1 − paradas planejadas); takt = tempo disponível ÷ demanda-alvo (Anexo D).",
           "Capacidade do posto = recursos × tempo disponível ÷ tempo de ciclo × OEE previsto; OEE previsto = disponibilidade × eficiência × qualidade (tabela 26).",
           "Recursos necessários = ARRED.PARA.CIMA(demanda × ciclo ÷ (tempo disponível × OEE previsto)). Investimento adicional = recursos além do projeto × investimento por recurso.",
           "OEE real (tabela 27): tempo operando = programado − parada planejada − parada não planejada − setup; disponibilidade = operando ÷ (programado − parada planejada); eficiência = quantidade × ciclo ÷ operando; qualidade = (produzida − refugada) ÷ produzida.",
           "Parâmetros (células amarelas): 2 turnos de 8 h, paradas planejadas 10%, demanda de projeto 42.000 caixas/dia (tabela 01)."],
          ["01_projeto_parametros", "25_demanda_historica", "26_processo_postos", "27_producao_apontamento", "28_manutencao_os"])

# --- Demanda
ws = aba(wb, "Demanda", [10, 26, 12, 12, 10, 4, 10, 14, 10, 14])
titulo(ws, 1, "Demanda histórica do site atual (36 meses)")
cab(ws, 3, ["Mês", "Família", "Demanda (cx)", "Atendido (cx)", "Dias úteis"])
for k, d in enumerate(dem.itertuples()):
    linha(ws, 4 + k, [d.mes, d.familia, d.demanda, d.volume_atendido, d.dias_uteis], {3: R0, 4: R0}, entrada_cols={1, 2, 3, 4, 5})
ld = 3 + len(dem)
meses = sorted(dem.mes.unique())
cab(ws, 3, ["Mês", "Demanda total (cx)", "Dias úteis", "Demanda/dia (cx)"], col=7)
for k, m in enumerate(meses):
    r = 4 + k
    linha_vals = [m, f"=SUMIF($A$4:$A${ld},G{r},$C$4:$C${ld})", int(dem[dem.mes == m].dias_uteis.iloc[0]), f"=H{r}/I{r}"]
    for j, v in enumerate(linha_vals): put(ws, r, 7 + j, v, {1: R0, 3: R0}.get(j), entrada=j in (0, 2))
lm = 3 + len(meses)
put(ws, lm + 2, 7, "Pico mensal (cx)", bold=True); put(ws, lm + 2, 8, f"=MAX(H4:H{lm})", R0)
put(ws, lm + 3, 7, "Média mensal (cx)", bold=True); put(ws, lm + 3, 8, f"=AVERAGE(H4:H{lm})", R0)
put(ws, lm + 4, 7, "Mínimo mensal (cx)", bold=True); put(ws, lm + 4, 8, f"=MIN(H4:H{lm})", R0)
put(ws, lm + 5, 7, "Pico ÷ média (sazonalidade)", bold=True); put(ws, lm + 5, 8, f"=H{lm+2}/H{lm+3}", '0.00')
put(ws, lm + 6, 7, "Pico de demanda diária (cx/dia)", bold=True); put(ws, lm + 6, 8, f"=MAX(J4:J{lm})", R0)
put(ws, lm + 7, 7, "Capacidade site atual (cx/mês)", bold=True); put(ws, lm + 7, 8, 551200, R0, entrada=True)
put(ws, lm + 8, 7, "Meses com demanda > capacidade atual", bold=True); put(ws, lm + 8, 8, f'=COUNTIF(H4:H{lm},">"&H{lm+7})')
ch = LineChart(); ch.title = "Demanda mensal × capacidade do site atual"; ch.height = 8; ch.width = 22
ch.add_data(Reference(ws, min_col=8, min_row=3, max_row=lm), titles_from_data=True); ch.set_categories(Reference(ws, min_col=7, min_row=4, max_row=lm))
ch.roundedCorners = False; ch.x_axis.delete = False; ch.y_axis.delete = False; ch.legend = None
ws.add_chart(ch, f"L4")
mt = dem.groupby("mes").demanda.sum(); md = (dem.groupby("mes").demanda.sum() / dem.groupby("mes").dias_uteis.first())
OUT["dem"] = {"pico": mt.max(), "media": mt.mean(), "min": mt.min(), "pico_dia": md.max(), "acima_cap": int((mt > 551200).sum()),
              "cv": mt.std() / mt.mean(), "mes_pico": mt.idxmax(), "fam": dem.groupby("familia").demanda.sum().div(dem.demanda.sum()).round(3).to_dict()}

# --- Classificação
ws = aba(wb, "Classificação", [24, 90])
titulo(ws, 1, "Classificação da operação")
CL = [("Modelo ITO · entradas", "Manga in natura dos produtores do Vale do São Francisco (Tommy, Palmer, Kent), embalagens, água, energia, mão de obra sazonal."),
      ("Modelo ITO · transformação", "Transformação física e de estado: lavagem, seleção óptica, tratamento hidrotérmico (exigência fitossanitária de exportação), embalagem, pré-resfriamento e armazenagem refrigerada."),
      ("Modelo ITO · saídas", "Caixas de 4 kg paletizadas e rastreadas por lote (WMS), expedidas refrigeradas para o Porto de Salvador, Recife e mercado interno."),
      ("4Vs · Volume", "Alto: pico de ~42 mil caixas/dia na safra (demanda de projeto)."),
      ("4Vs · Variedade", "Baixa: 3 famílias com a mesma caixa de 4 kg e o mesmo roteiro."),
      ("4Vs · Variação", f"Alta: demanda mensal varia de {OUT['dem']['min']:,.0f} a {OUT['dem']['pico']:,.0f} caixas (pico ÷ média = {OUT['dem']['pico']/OUT['dem']['media']:.2f}; coeficiente de variação {OUT['dem']['cv']:.2f}).".replace(",", ".")),
      ("4Vs · Visibilidade", "Baixa: operação de bastidor (B2B, exportação); o cliente vê prazo, rastreabilidade e qualidade."),
      ("Tipologia", "Produção em fluxo (linha), repetitiva em massa durante a safra; processo contínuo com estágios em paralelo (tanques, túneis)."),
      ("Política de atendimento", "Fazer para estoque de curtíssimo prazo (make-to-stock refrigerado) puxado pela colheita, com expedição montada contra pedido do importador; perecível, sem estoque entre safras."),
      ("Consequência para o PCP", "Capacidade deve ser dimensionada para o pico da safra; fora dela, sobra capacidade e a mão de obra é sazonal. O gargalo define a quantidade de manga que entra por dia.")]
cab(ws, 3, ["Aspecto", "Classificação do grupo"])
for k, (x, y) in enumerate(CL):
    linha(ws, 4 + k, [x, y]); ws.cell(4 + k, 2).alignment = Alignment(wrap_text=True, vertical="top")
from openpyxl.styles import Alignment

# --- Capacidade
ws = aba(wb, "Capacidade", [8, 28, 10, 10, 10, 10, 10, 10, 10, 13, 11, 11, 11, 13, 14, 14, 11])
titulo(ws, 1, "Takt, capacidade por posto e gargalo (nova unidade)")
par = [("Turnos por dia", 2, '0'), ("Horas por turno", 8, '0'), ("Paradas planejadas", 0.10, '0%'), ("Demanda-alvo (cx/dia)", 42000, R0)]
for k, (rot, v, f) in enumerate(par):
    put(ws, 3 + k, 2, rot, bold=True); put(ws, 3 + k, 3, v, f, entrada=True, fill=FILL_Y)
put(ws, 7, 2, "Tempo disponível (s/dia)", bold=True); put(ws, 7, 3, "=C3*C4*3600*(1-C5)", R0)
put(ws, 8, 2, "Takt (s/caixa)", bold=True); put(ws, 8, 3, "=C7/C6", '0.000')
cab(ws, 10, ["Posto", "Nome", "Ciclo (s/cx)", "Recursos projeto", "Disp. prev.", "Efic. prev.", "Qual. prev.", "OEE previsto", "Capacidade (cx/dia)",
             "Utilização", "Gargalo?", "Recursos necessários", "Recursos adicionais", "Invest./recurso (R$)", "Invest. adicional (R$)", "Operadores necessários", "Recursos hoje"])
for k, p in enumerate(postos.itertuples()):
    r = 11 + k
    linha(ws, r, [p.id_posto, p.nome_posto, p.tempo_ciclo_padrao_s, p.recursos_projeto, p.disponibilidade_prevista, p.eficiencia_prevista, p.qualidade_prevista,
                  f"=E{r}*F{r}*G{r}", f"=D{r}*$C$7/C{r}*H{r}", f"=$C$6/I{r}", f'=IF(I{r}=MIN($I$11:$I$17),"GARGALO",IF(I{r}<$C$6,"abaixo da demanda",""))',
                  f"=ROUNDUP($C$6*C{r}/($C$7*H{r}),0)", f"=MAX(0,L{r}-D{r})", p.investimento_por_recurso_rs, f"=M{r}*N{r}",
                  f"=L{r}*{p.operadores_por_recurso}*$C$3", p.recursos_site_atual],
          {3: '0.000', 5: P, 6: P, 7: P, 8: P, 9: R0, 10: P, 14: R0, 15: R0, 16: '0.0'}, entrada_cols={1, 2, 3, 4, 5, 6, 7, 14, 17})
put(ws, 19, 2, "Investimento adicional total", bold=True); put(ws, 19, 15, "=SUM(O11:O17)", R0, bold=True)
put(ws, 20, 2, "Capacidade da linha (posto gargalo)", bold=True); put(ws, 20, 9, "=MIN(I11:I17)", R0, bold=True)
put(ws, 21, 2, "Operadores por dia (todos os postos)", bold=True); put(ws, 21, 16, "=SUM(P11:P17)", '0')
nota(ws, 22, "Operadores necessários = recursos necessários × operadores por recurso × turnos.")
ch = BarChart(); ch.title = "Capacidade por posto × demanda (cx/dia)"; ch.height = 8; ch.width = 20
ch.add_data(Reference(ws, min_col=9, min_row=10, max_row=17), titles_from_data=True); ch.set_categories(Reference(ws, min_col=1, min_row=11, max_row=17))
put(ws, 10, 18, "Demanda"); [put(ws, 11 + k, 18, "=$C$6", R0) for k in range(7)]
ln = LineChart(); ln.add_data(Reference(ws, min_col=18, min_row=10, max_row=17), titles_from_data=True); ch += ln
ch.roundedCorners = False; ch.x_axis.delete = False; ch.y_axis.delete = False; ch.legend.position = "b"; ch.legend.overlay = False
ws.add_chart(ch, "B24")
# valores para o PDF
tdisp = 2 * 8 * 3600 * 0.9; takt = tdisp / 42000
cap = []
for p in postos.itertuples():
    oee = p.disponibilidade_prevista * p.eficiencia_prevista * p.qualidade_prevista
    c = p.recursos_projeto * tdisp / p.tempo_ciclo_padrao_s * oee
    nec = -(-42000 * p.tempo_ciclo_padrao_s // (tdisp * oee))
    cap.append({"posto": p.id_posto, "nome": p.nome_posto, "oee": oee, "cap": c, "nec": int(nec), "proj": p.recursos_projeto,
                "add": max(0, int(nec) - p.recursos_projeto), "inv": max(0, int(nec) - p.recursos_projeto) * p.investimento_por_recurso_rs,
                "ops": int(nec) * p.operadores_por_recurso * 2})
OUT["cap"] = cap; OUT["tdisp"] = tdisp; OUT["takt"] = takt

# --- OEE real
ws = aba(wb, "OEE real", [11, 6, 7, 8, 10, 10, 10, 9, 11, 10, 9, 11, 10, 10, 10, 10])
titulo(ws, 1, "OEE real do site atual (tabela 27)")
cab(ws, 3, ["Data", "Turno", "Posto", "Recursos", "Programado (min)", "Parada plan. (min)", "Parada não plan. (min)", "Setup (min)", "Produzida (cx)", "Refugada (cx)",
            "Ciclo (s)", "Operando (min)", "Disponib.", "Eficiência", "Qualidade", "OEE"])
ciclo = postos.set_index("id_posto").tempo_ciclo_padrao_s
for k, x in enumerate(ap.itertuples()):
    r = 4 + k
    linha(ws, r, [pd.Timestamp(x.data), x.turno, x.id_posto, x.recursos_ativos, x.tempo_programado_min, x.parada_planejada_min, x.parada_nao_planejada_min, x.setup_min,
                  x.quantidade_produzida, x.quantidade_refugada, float(ciclo[x.id_posto]), f"=E{r}-F{r}-G{r}-H{r}", f"=L{r}/(E{r}-F{r})",
                  f"=I{r}*K{r}/60/L{r}", f"=(I{r}-J{r})/I{r}", f"=M{r}*N{r}*O{r}"],
          {1: D, 13: P, 14: P, 15: P, 16: P}, entrada_cols=set(range(1, 12)))
la = 3 + len(ap)
ws2 = aba(wb, "OEE por posto", [8, 28, 12, 12, 12, 12, 12, 12])
titulo(ws2, 1, "OEE real agregado por posto × OEE previsto no projeto")
cab(ws2, 3, ["Posto", "Nome", "Disponib. real", "Eficiência real", "Qualidade real", "OEE real", "OEE previsto", "Diferença (p.p.)"])
for k, p in enumerate(postos.itertuples()):
    r = 4 + k; rg = lambda c: f"'OEE real'!${c}$4:${c}${la}"
    s = lambda c: f"SUMIF({rg('C')},A{r},{rg(c)})"
    linha(ws2, r, [p.id_posto, p.nome_posto, f"={s('L')}/({s('E')}-{s('F')})", f"=SUMIF({rg('C')},A{r},{rg('I')})*{float(ciclo[p.id_posto])}/60/{s('L')}",
                   f"=({s('I')}-{s('J')})/{s('I')}", f"=C{r}*D{r}*E{r}", f"=Capacidade!H{11+k}", f"=F{r}-G{r}"],
          {3: P, 4: P, 5: P, 6: P, 7: P, 8: P}, entrada_cols={1, 2})
titulo(ws2, 13, "Folha M3 · turno real: PT04, 04/11/2026, turno 2")
m3 = ap[(ap.data == "2026-11-04") & (ap.id_posto == "PT04") & (ap.turno == 2)].iloc[0]
r3 = 4 + ap.index[(ap.data == "2026-11-04") & (ap.id_posto == "PT04") & (ap.turno == 2)][0]
for k, (rot, f, fm) in enumerate([("Tempo operando (min)", f"='OEE real'!L{r3}", R0), ("Disponibilidade", f"='OEE real'!M{r3}", P),
                                  ("Eficiência", f"='OEE real'!N{r3}", P), ("Qualidade", f"='OEE real'!O{r3}", P), ("OEE", f"='OEE real'!P{r3}", P)]):
    put(ws2, 14 + k, 2, rot, bold=True); put(ws2, 14 + k, 3, f, fm)
nota(ws2, 20, "Maior perda do turno: disponibilidade (2.411 min de parada não planejada). É a primeira a atacar.")
op = m3.tempo_programado_min - m3.parada_planejada_min - m3.parada_nao_planejada_min - m3.setup_min
OUT["m3"] = {"op": op, "disp": op / (m3.tempo_programado_min - m3.parada_planejada_min), "efic": m3.quantidade_produzida * 18.5 / 60 / op,
             "qual": (m3.quantidade_produzida - m3.quantidade_refugada) / m3.quantidade_produzida}
OUT["m3"]["oee"] = OUT["m3"]["disp"] * OUT["m3"]["efic"] * OUT["m3"]["qual"]
apx = ap.assign(op=ap.tempo_programado_min - ap.parada_planejada_min - ap.parada_nao_planejada_min - ap.setup_min, cic=ap.id_posto.map(ciclo))
g = apx.groupby("id_posto").agg(op=("op", "sum"), prog=("tempo_programado_min", "sum"), pp=("parada_planejada_min", "sum"), q=("quantidade_produzida", "sum"),
                                ref=("quantidade_refugada", "sum"), cic=("cic", "first"))
g["disp"] = g.op / (g.prog - g.pp); g["efic"] = g.q * g.cic / 60 / g.op; g["qual"] = (g.q - g.ref) / g.q; g["oee"] = g.disp * g.efic * g.qual
OUT["oee_real"] = g[["disp", "efic", "qual", "oee"]].round(4).to_dict("index")

# --- Manutenção
ws = aba(wb, "Manutenção", [8, 12, 12, 13, 12, 13, 12, 12, 14, 60])
titulo(ws, 1, "Manutenção do site atual (tabela 28) e plano proposto")
put(ws, 2, 1, "Período", bold=True); put(ws, 2, 2, f"{os_.data_abertura.min()} a {os_.data_abertura.max()}")
put(ws, 3, 1, "Dias de operação no período", bold=True); put(ws, 3, 4, int(pd.bdate_range(os_.data_abertura.min(), os_.data_abertura.max()).size), entrada=True)
cab(ws, 5, ["Posto", "Recursos hoje", "Corretivas", "Preventivas", "Horas de parada corretiva", "Horas programadas", "MTBF (h)", "MTTR (h)", "Custo peças (R$)", "Plano proposto"])
key = os_.id_posto + "|" + os_.tipo_manutencao
ws3 = aba(wb, "OS", [8, 11, 8, 12, 10, 10, 11, 18])
cab(ws3, 1, ["Chave", "Data", "Posto", "Tipo", "Horas parada", "Hh", "Peças (R$)", "Causa"])
for k, o in enumerate(os_.itertuples()):
    linha(ws3, 2 + k, [f"{o.id_posto}|{o.tipo_manutencao}", pd.Timestamp(o.data_abertura), o.id_posto, o.tipo_manutencao, o.horas_parada, o.hh_manutencao, o.custo_pecas_rs, o.causa],
          {2: D, 7: R}, entrada_cols=set(range(1, 9)))
lo = 1 + len(os_)
causas_top = os_[os_.tipo_manutencao == "CORRETIVA"].groupby("id_posto").causa.agg(lambda s: s.value_counts().index[0])
PLANO = {"PT04": "Prioridade 1: 152 corretivas. Preventiva semanal por estação (lubrificação e troca de itens de desgaste), checklist autônomo no início do turno (TPM).",
         "PT03": "Preventiva quinzenal nos tanques (resistências, bombas, sensores de temperatura); estoque de peças críticas.",
         "PT06": "Preventiva quinzenal dos ventiladores e evaporadores dos túneis; limpeza de serpentinas antes da safra.",
         "PT05": "Preventiva mensal da cintadeira; ajuste operacional com padrão visual.",
         "PT02": "Calibração e limpeza óptica semanal; contrato com o fabricante.", "PT01": "Preventiva mensal de bombas e escovas.",
         "PT07": "Preventiva mensal das empilhadeiras e portas rápidas."}
for k, p in enumerate(postos.itertuples()):
    r = 6 + k
    linha(ws, r, [p.id_posto, p.recursos_site_atual, f'=COUNTIF(OS!$A$2:$A${lo},A{r}&"|CORRETIVA")', f'=COUNTIF(OS!$A$2:$A${lo},A{r}&"|PREVENTIVA")',
                  f'=SUMIF(OS!$A$2:$A${lo},A{r}&"|CORRETIVA",OS!$E$2:$E${lo})', f"=B{r}*$D$3*16", f"=(F{r}-E{r})/C{r}", f"=E{r}/C{r}",
                  f'=SUMIF(OS!$C$2:$C${lo},A{r},OS!$G$2:$G${lo})', PLANO[p.id_posto] + f" Causa mais frequente: {causas_top[p.id_posto]}."],
          {5: '0.0', 6: R0, 7: '0.0', 8: '0.0', 9: R}, entrada_cols={1, 2})
    ws.cell(r, 10).alignment = Alignment(wrap_text=True, vertical="top")
nota(ws, 14, "MTBF = (horas programadas − horas de parada corretiva) ÷ nº de corretivas; horas programadas = recursos × dias × 16 h (2 turnos).")
mtos = os_.groupby(["id_posto", "tipo_manutencao"]).size().unstack(fill_value=0)
OUT["manut"] = {"PT04_corr": int(mtos.loc["PT04", "CORRETIVA"]), "PT04_prev": int(mtos.loc["PT04", "PREVENTIVA"]), "total_corr": int(mtos.CORRETIVA.sum()),
                "custo_pecas": float(os_.custo_pecas_rs.sum())}
wb.save(DOCS / "D9_dimensionamento_operacao.xlsx"); print("ok D9")

# ======================= D10 =======================
pts = t["29_pontos_logisticos"]; fat = t["30_localizacao_fatores"]; zon = t["13_layout_zonas"].set_index("id_zona"); flu = t["14_fluxo_zonas"]
wb = novo("Localização e layout", "D10",
          ["Centro de gravidade ponderado pelo volume (t/mês): x = Σ(x·V) ÷ ΣV; y = Σ(y·V) ÷ ΣV (coordenadas em km, tabela 29).",
           "Custo mensal de transporte de cada terreno = Σ volume × frete × distância em linha reta até cada ponto.",
           "Pontuação ponderada = Σ peso × nota (tabela 30). Sensibilidade: transferência de peso entre dois fatores (célula amarela) e o ponto de empate calculado.",
           "Layout: centro de cada zona = canto + metade da largura/comprimento; carga × distância = viagens/dia × distância retilínea |Δx| + |Δy| (Anexo D)."],
          ["29_pontos_logisticos", "30_localizacao_fatores", "13_layout_zonas", "14_fluxo_zonas"])
ws = aba(wb, "Centro de gravidade", [7, 32, 18, 9, 9, 12, 12, 12, 12])
titulo(ws, 1, "Centro de gravidade e custo de transporte")
cab(ws, 3, ["Ponto", "Nome", "Tipo", "x (km)", "y (km)", "Volume (t/mês)", "Frete (R$/t·km)", "x·V", "y·V"])
pl = pts[pts.tipo_ponto != "TERRENO_CANDIDATO"]; tr = pts[pts.tipo_ponto == "TERRENO_CANDIDATO"]
for k, p in enumerate(pl.itertuples()):
    r = 4 + k
    linha(ws, r, [p.id_ponto, p.nome_ponto, p.tipo_ponto, p.x_km, p.y_km, p.volume_t_mes, p.custo_frete_rs_t_km, f"=D{r}*F{r}", f"=E{r}*F{r}"],
          {6: R0, 7: '0.00', 8: R0, 9: R0}, entrada_cols={1, 2, 3, 4, 5, 6, 7})
lp = 3 + len(pl)
put(ws, lp + 1, 2, "Totais", bold=True); put(ws, lp + 1, 6, f"=SUM(F4:F{lp})", R0); put(ws, lp + 1, 8, f"=SUM(H4:H{lp})", R0); put(ws, lp + 1, 9, f"=SUM(I4:I{lp})", R0)
put(ws, lp + 2, 2, "Centro de gravidade (x ; y)", bold=True); put(ws, lp + 2, 4, f"=H{lp+1}/F{lp+1}", '0.0', bold=True); put(ws, lp + 2, 5, f"=I{lp+1}/F{lp+1}", '0.0', bold=True)
rcg = lp + 2
r0 = lp + 4
cab(ws, r0, ["Terreno", "Nome", "Distância ao CG (km)", "x (km)", "y (km)", "Custo transporte (R$/mês)"])
cust = {}
for k, p in enumerate(tr.itertuples()):
    r = r0 + 1 + k
    custo_f = "+".join(f"$F${4+j}*$G${4+j}*SQRT(($D${4+j}-D{r})^2+($E${4+j}-E{r})^2)" for j in range(len(pl)))
    linha(ws, r, [p.id_ponto, p.nome_ponto, f"=SQRT((D{r}-$D${rcg})^2+(E{r}-$E${rcg})^2)", p.x_km, p.y_km, f"={custo_f}"], {3: '0.0', 6: R0}, entrada_cols={1, 2, 4, 5})
    cust[p.id_ponto] = sum(q.volume_t_mes * q.custo_frete_rs_t_km * ((q.x_km - p.x_km) ** 2 + (q.y_km - p.y_km) ** 2) ** .5 for q in pl.itertuples())
put(ws, r0 + 5, 2, "Menor custo de transporte", bold=True)
put(ws, r0 + 5, 6, f'=IF(F{r0+1}=MIN(F{r0+1}:F{r0+3}),A{r0+1},IF(F{r0+2}=MIN(F{r0+1}:F{r0+3}),A{r0+2},A{r0+3}))', bold=True)
cgx = (pl.x_km * pl.volume_t_mes).sum() / pl.volume_t_mes.sum(); cgy = (pl.y_km * pl.volume_t_mes).sum() / pl.volume_t_mes.sum()
OUT["cg"] = (cgx, cgy); OUT["custo_transp"] = cust
OUT["dist_cg"] = {p.id_ponto: ((p.x_km - cgx) ** 2 + (p.y_km - cgy) ** 2) ** .5 for p in tr.itertuples()}

ws = aba(wb, "Pontuação ponderada", [46, 10, 11, 11, 11, 4, 12, 12, 12])
titulo(ws, 1, "Pontuação ponderada e sensibilidade")
cab(ws, 3, ["Fator", "Peso (%)", "Terreno A", "Terreno B", "Terreno C", "", "Pond. A", "Pond. B", "Pond. C"])
for k, f in enumerate(fat.itertuples()):
    r = 4 + k
    linha(ws, r, [f.fator, f.peso_pct, f.nota_terreno_a, f.nota_terreno_b, f.nota_terreno_c, None, f"=$B{r}*C{r}/100", f"=$B{r}*D{r}/100", f"=$B{r}*E{r}/100"],
          {7: '0.00', 8: '0.00', 9: '0.00'}, entrada_cols={1, 2, 3, 4, 5})
lf = 3 + len(fat)
put(ws, lf + 1, 1, "Total", bold=True); put(ws, lf + 1, 2, f"=SUM(B4:B{lf})")
for c in "GHI": put(ws, lf + 1, " ABCDEFGHI".index(c), f"=SUM({c}4:{c}{lf})", '0.00', bold=True)
put(ws, lf + 2, 1, "Vencedor", bold=True); put(ws, lf + 2, 7, f'=IF(G{lf+1}=MAX(G{lf+1}:I{lf+1}),"A",IF(H{lf+1}=MAX(G{lf+1}:I{lf+1}),"B","C"))', bold=True)
rs = lf + 4
titulo(ws, rs, "Sensibilidade: tirar Δ pontos de peso de 'Acesso rodoviário e portuário' e somar em 'Incentivos fiscais'")
put(ws, rs + 1, 1, "Δ transferido (pontos de peso)", bold=True); put(ws, rs + 1, 2, 5, entrada=True, fill=FILL_Y)
put(ws, rs + 2, 1, "Novo total A", bold=True); put(ws, rs + 2, 2, f"=G{lf+1}+B{rs+1}*(C7-C5)/100", '0.00')
put(ws, rs + 3, 1, "Novo total B", bold=True); put(ws, rs + 3, 2, f"=H{lf+1}+B{rs+1}*(D7-D5)/100", '0.00')
put(ws, rs + 4, 1, "Novo total C", bold=True); put(ws, rs + 4, 2, f"=I{lf+1}+B{rs+1}*(E7-E5)/100", '0.00')
put(ws, rs + 5, 1, "Δ de empate A × B (pontos de peso)", bold=True); put(ws, rs + 5, 2, f"=(G{lf+1}-H{lf+1})*100/((D7-D5)-(C7-C5))", '0.0')
nota(ws, rs + 6, "Leitura: basta transferir poucos pontos de peso para o Terreno B empatar com o A; a escolha é sensível ao peso dos incentivos fiscais.")
sc = {k: (fat.peso_pct * fat[f"nota_terreno_{k.lower()}"]).sum() / 100 for k in "ABC"}
OUT["score"] = sc; OUT["delta_empate"] = (sc["A"] - sc["B"]) * 100 / ((fat.nota_terreno_b[3] - fat.nota_terreno_b[1]) - (fat.nota_terreno_a[3] - fat.nota_terreno_a[1]))

# --- Layout
ws = aba(wb, "Layout", [10, 34, 9, 9, 9, 9, 10, 10])
titulo(ws, 1, "Centros das zonas")
cab(ws, 3, ["Zona", "Nome", "x", "y", "Largura", "Comprimento", "Centro x", "Centro y"])
for k, (zid, z) in enumerate(zon.iterrows()):
    r = 4 + k
    linha(ws, r, [zid, z.nome_zona, z.x_m, z.y_m, z.largura_x_m, z.comprimento_y_m, f"=C{r}+E{r}/2", f"=D{r}+F{r}/2"], {7: '0.0', 8: '0.0'}, entrada_cols={1, 2, 3, 4, 5, 6})
lz = 3 + len(zon); ZR = f"$A$4:$H${lz}"
cen = {zid: (z.x_m + z.largura_x_m / 2, z.y_m + z.comprimento_y_m / 2) for zid, z in zon.iterrows()}

def cxd(c, troca=None):
    c = dict(c)
    if troca: c[troca[0]], c[troca[1]] = c[troca[1]], c[troca[0]]
    return sum(f.viagens_dia * (abs(c[f.id_zona_origem][0] - c[f.id_zona_destino][0]) + abs(c[f.id_zona_origem][1] - c[f.id_zona_destino][1])) for f in flu.itertuples())
proc = [z for z in zon.index if zon.tipo_zona[z] == "PROCESSO"]
melhores = sorted(((cxd(cen, (x, y)), x, y) for x, y in itertools.combinations(proc, 2)))
base_cd = cxd(cen); recsel = cxd(cen, ("REC", "SEL")); best = next(m for m in melhores if {m[1], m[2]} != {"REC", "SEL"})
OUT["layout"] = {"base": base_cd, "rec_sel": recsel, "best": best, "rank": melhores[:5]}
r0 = lz + 3
titulo(ws, r0 - 1, "Carga × distância: layout proposto, troca REC↔SEL e melhor troca entre zonas de processo")
put(ws, r0, 1, "Troca 1", bold=True); put(ws, r0, 2, "REC", entrada=True, fill=FILL_Y); put(ws, r0, 3, "SEL", entrada=True, fill=FILL_Y)
put(ws, r0 + 1, 1, "Troca 2", bold=True); put(ws, r0 + 1, 2, best[1], entrada=True, fill=FILL_Y); put(ws, r0 + 1, 3, best[2], entrada=True, fill=FILL_Y)
cab(ws, r0 + 3, ["Origem", "Destino", "Viagens/dia", "Dist. proposta (m)", "C×D proposta", "Dist. troca 1 (m)", "C×D troca 1", "Dist. troca 2 (m)", "C×D troca 2"])
ws.column_dimensions["I"].width = 11

def zona_troca(cel, a_, b_):  # zona efetiva após a troca: se for a_ vira b_ e vice-versa
    return f'IF({cel}={a_},{b_},IF({cel}={b_},{a_},{cel}))'
for k, f in enumerate(flu.itertuples()):
    r = r0 + 4 + k
    def dist(o, d): return f"ABS(VLOOKUP({o},{ZR},7,FALSE)-VLOOKUP({d},{ZR},7,FALSE))+ABS(VLOOKUP({o},{ZR},8,FALSE)-VLOOKUP({d},{ZR},8,FALSE))"
    t1o, t1d = zona_troca(f"A{r}", f"$B${r0}", f"$C${r0}"), zona_troca(f"B{r}", f"$B${r0}", f"$C${r0}")
    t2o, t2d = zona_troca(f"A{r}", f"$B${r0+1}", f"$C${r0+1}"), zona_troca(f"B{r}", f"$B${r0+1}", f"$C${r0+1}")
    linha(ws, r, [f.id_zona_origem, f.id_zona_destino, f.viagens_dia, f"={dist(f'A{r}', f'B{r}')}", f"=C{r}*D{r}",
                  f"={dist(t1o, t1d)}", f"=C{r}*F{r}", f"={dist(t2o, t2d)}", f"=C{r}*H{r}"],
          {3: R0, 4: '0.0', 5: R0, 6: '0.0', 7: R0, 8: '0.0', 9: R0}, entrada_cols={1, 2, 3})
lf2 = r0 + 3 + len(flu)
put(ws, lf2 + 1, 1, "Total (m·viagem/dia)", bold=True)
for c in (5, 7, 9): put(ws, lf2 + 1, c, f"=SUM({'ABCDEFGHI'[c-1]}{r0+4}:{'ABCDEFGHI'[c-1]}{lf2})", R0, bold=True)
put(ws, lf2 + 2, 1, "Variação vs proposto", bold=True)
for c in (7, 9): put(ws, lf2 + 2, c, f"={'ABCDEFGHI'[c-1]}{lf2+1}/$E${lf2+1}-1", P, bold=True)
nota(ws, lf2 + 3, f"REC↔SEL é a melhor de todas as {len(melhores)} trocas entre zonas de processo (testadas por script); a troca 2 é a segunda melhor. Antes de mudar: verificar pé-direito, docas, drenagem do hidrotérmico e isolamento térmico.")
wb.save(DOCS / "D10_localizacao_layout.xlsx"); print("ok D10")

# ======================= figuras =======================
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
plt.rcParams["font.family"] = "DejaVu Serif"
# mapa de localização
fig, ax = plt.subplots(figsize=(7, 5.5))
for p in pl.itertuples():
    ax.scatter(p.x_km, p.y_km, s=p.volume_t_mes / 15, color="#3b6ea5" if p.tipo_ponto == "FORNECEDOR" else "#d4880f", alpha=.7, edgecolor="k")
    ax.annotate(p.nome_ponto, (p.x_km, p.y_km), xytext=(5, 5), textcoords="offset points", fontsize=8)
for p in tr.itertuples():
    ax.scatter(p.x_km, p.y_km, marker="s", s=60, color="#2e9e5b", edgecolor="k"); ax.annotate(p.id_ponto, (p.x_km, p.y_km), xytext=(-14, -12), textcoords="offset points", fontsize=8, color="#1f4d3a")
ax.scatter(cgx, cgy, marker="*", s=250, color="#c0392b", edgecolor="k", zorder=5); ax.annotate(f"CG ({cgx:.0f}; {cgy:.0f})", (cgx, cgy), xytext=(8, -12), textcoords="offset points", fontsize=9, color="#c0392b")
ax.set_xlabel("x (km)"); ax.set_ylabel("y (km)"); ax.set_aspect("equal"); ax.grid(alpha=.3)
ax.scatter([], [], color="#3b6ea5", label="fornecedor (área ∝ volume)"); ax.scatter([], [], color="#d4880f", label="cliente (área ∝ volume)")
ax.scatter([], [], marker="s", color="#2e9e5b", label="terreno candidato"); ax.legend(fontsize=8, loc="lower right")
fig.tight_layout(); fig.savefig(FIG / "d10_mapa_localizacao.png", dpi=180); plt.close(fig)
# planta com fluxos
fig, ax = plt.subplots(figsize=(8, 7))
cores = {"TERRENO": "#f4efe3", "EDIFICACAO": "none", "PATIO": "#e3e3e3", "APOIO": "#d6e4f0", "UTILIDADES": "#f0e0d6", "CANTEIRO": "#fde9c9", "PROCESSO": "#dcefe2"}
for zid, z in zon.iterrows():
    ax.add_patch(Rectangle((z.x_m, z.y_m), z.largura_x_m, z.comprimento_y_m, facecolor=cores[z.tipo_zona], edgecolor="k", lw=1.6 if zid == "GALPAO" else .8))
    if zid not in ("TERRENO", "GALPAO"):
        cx, cy = cen[zid]; ax.plot(cx, cy, "k.", ms=4); ax.text(cx, cy + 3, zid, ha="center", fontsize=8, weight="bold")
mx = flu.viagens_dia.max()
for f in flu.itertuples():
    (x0, y0), (x1, y1) = cen[f.id_zona_origem], cen[f.id_zona_destino]
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=10, lw=0.5 + 5 * f.viagens_dia / mx, color="#c0392b", alpha=.65,
                                 connectionstyle="arc3,rad=0.15"))
ax.set_xlim(-2, 207); ax.set_ylim(-2, 177); ax.set_aspect("equal"); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
ax.set_title("Planta em escala (m) e fluxos (espessura ∝ viagens/dia)", fontsize=10)
fig.tight_layout(); fig.savefig(FIG / "d10_planta_fluxos.png", dpi=180); plt.close(fig)
# layout do canteiro na fase de montagem
fig, ax = plt.subplots(figsize=(8, 7))
for zid in ["TERRENO", "GALPAO", "PATIO", "DOCAS", "APOIO", "UTIL", "CANTEIRO"]:
    z = zon.loc[zid]; ax.add_patch(Rectangle((z.x_m, z.y_m), z.largura_x_m, z.comprimento_y_m, facecolor=cores[z.tipo_zona] if zid != "GALPAO" else "#eef3f6", edgecolor="k", lw=.8))
    ax.text(z.x_m + z.largura_x_m / 2, z.y_m + z.comprimento_y_m - 6, zid if zid != "TERRENO" else "", ha="center", fontsize=8, weight="bold")
el = [((5, 84.7, 30, 18), "#9ecae1", "Vivência: vestiários,\nrefeitório, sanitários"), ((5, 102.7, 30, 22), "#fdd49e", "Escritório da obra\ne almoxarifado"),
      ((5, 130, 30, 30), "#c7e9c0", "Estoque coberto dos\nequipamentos de processo"), ((40, 40, 50, 30), "#d9d9d9", "Área de descarga\n(carretas)"),
      ((95, 40, 40, 30), "#fcbba1", "Pré-montagem de\npainéis e tubulação"), ((140, 40, 18, 30), "#e5e5e5", "Bota-fora e\ncaçambas")]
for (x, y, w, h), c, txt in el:
    ax.add_patch(Rectangle((x, y), w, h, facecolor=c, edgecolor="k", lw=.7, hatch="..")); ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=7)
ax.annotate("", xy=(100, 10), xytext=(100, -1), arrowprops=dict(arrowstyle="-|>", lw=2.5, color="#1f4d3a")); ax.text(103, 1, "Acesso de caminhões (portão)", fontsize=8, color="#1f4d3a")
ax.plot([100, 100, 65], [10, 35, 35], "--", color="#1f4d3a", lw=1.5); ax.text(70, 36.5, "via interna", fontsize=7, color="#1f4d3a")
gx, gy = 100, 79
from matplotlib.patches import Circle
ax.add_patch(Circle((gx, gy), 2.5, color="#c0392b")); ax.add_patch(Circle((gx, gy), 36, fill=False, ls=":", color="#c0392b"))
ax.text(gx + 3, gy - 6, "Guindaste 70 t\n(raio útil ~36 m)", fontsize=7, color="#c0392b")
ax.set_xlim(-2, 207); ax.set_ylim(-3, 177); ax.set_aspect("equal"); ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
ax.set_title("Layout do canteiro — fase de montagem dos equipamentos de processo", fontsize=10)
fig.tight_layout(); fig.savefig(FIG / "d10_canteiro.png", dpi=180); plt.close(fig)
# capacidade
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.bar([c["posto"] for c in cap], [c["cap"] for c in cap], color=["#c0392b" if c["cap"] < 42000 else "#2e9e5b" for c in cap])
ax.axhline(42000, color="k", ls="--", lw=1); ax.text(6.4, 43000, "demanda 42.000", ha="right", fontsize=8)
ax.set_ylabel("caixas/dia"); ax.set_title("Capacidade diária por posto (recursos do projeto)", fontsize=10); ax.grid(axis="y", alpha=.3)
fig.tight_layout(); fig.savefig(FIG / "d9_capacidade.png", dpi=180); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.plot(mt.index, mt.values / 1000, marker="o", color="#1f4d3a"); ax.axhline(551.2, color="#c0392b", ls="--", lw=1); ax.text(0, 565, "capacidade do site atual (551,2 mil)", fontsize=8, color="#c0392b")
ax.set_ylabel("mil caixas/mês"); ax.set_title("Demanda mensal do site atual (36 meses)", fontsize=10)
ax.set_xticks(range(0, len(mt), 3)); ax.set_xticklabels(mt.index[::3], rotation=45, fontsize=7); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(FIG / "d9_demanda.png", dpi=180); plt.close(fig)

(DOCS / "_d9_d10.json").write_text(json.dumps(OUT, default=float, ensure_ascii=False, indent=1))
print(json.dumps({k: OUT[k] for k in ["dem", "takt", "m3", "cg", "custo_transp", "score", "delta_empate", "layout", "manut"]}, default=float, indent=1, ensure_ascii=False))
for c in cap: print(c)
print(OUT["oee_real"])
