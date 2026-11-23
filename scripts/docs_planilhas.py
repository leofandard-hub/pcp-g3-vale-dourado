"""Gera as planilhas D1–D8 em docs/ (fórmulas simples, nível Excel intermediário).
Uso: python scripts/docs_planilhas.py
"""
import sys
from pathlib import Path
import pandas as pd
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.utils import get_column_letter as L

sys.path.insert(0, str(Path(__file__).parent))
import calculos as C
from docs_util import *

DOCS = C.RAIZ / "docs"
t, a, base = C.tab, C.a, C.base.set_index("id_atividade")
cal = t["11_calendario"].copy(); cal["data_dt"] = pd.to_datetime(cal.data)
du2dt = {int(r.dia_util_projeto): r.data_dt for r in cal.itertuples() if r.dia_util_projeto == r.dia_util_projeto}
orc = t["12_orcamento_linha_de_base"].set_index("id_atividade")
prod = t["16_rdo_producao"]
pct_real = (prod[prod.data <= "2026-11-06"].groupby("id_atividade").quantidade_executada.sum() / a.quantidade_orcada).clip(upper=1).reindex(a.index).fillna(0).round(3)
rec = t["07_atividade_recursos"]
mo = rec[rec.tipo_recurso == "MAO_DE_OBRA"]
eqr = rec[rec.tipo_recurso == "EQUIPAMENTO"]


def salvar(wb, nome):
    wb.save(DOCS / nome); print("ok", nome)


# =============== D1 · EAP comentada ===============
COMENT = {
    "1.1": "Projetos, licenças e compra/fabricação dos equipamentos de processo (A05 tem 100 du: item de prazo longo).",
    "1.2": "Preparação do terreno até as fundações. Fase concluída; IDC 0,86 (equipamento e mão de obra acima).",
    "1.3": "Galpão, piso, pátio e apoio. A12 (piso) está no caminho crítico e libera câmaras e equipamentos.",
    "1.4": "Instalações prediais e utilidades. Todas dependem do fim da cobertura (A10) e do projeto A02.",
    "1.5": "Maior fase (42% do orçamento). Câmaras frias e linhas de processo; A23 → A26 são críticas.",
    "1.6": "WMS, recrutamento e treinamento (contratados, duração fixa).",
    "1.7": "Comissionamento, testes, AVCB/licença e ramp-up. Fecham o projeto (A38).",
    "1.9": "Administração local: custo indireto mensal, acompanhado fora do custo direto (Anexo D).",
}
wb = novo("EAP comentada", "D1",
          ["EAP até o nível de pacote de trabalho (nível 3), como na tabela 02.",
           "Regra dos 100%: o custo de cada fase é a SOMA dos seus pacotes (SOMASE pela coluna 'Pai'); o total deve bater com o orçamento de custo direto do projeto (R$ 28.116.171,71, tabela 01).",
           "A administração local (1.9) é custo indireto: não entra no custo direto, aparece à parte (R$ 146.000/mês)."],
          ["02_eap", "03_atividades (quantidade, unidade, regime)", "12_orcamento_linha_de_base (custo por pacote)", "01_projeto_parametros"])
ws = aba(wb, "EAP", [9, 8, 66, 9, 8, 12, 9, 12, 16, 9, 70])
titulo(ws, 1, "D1 · Estrutura Analítica do Projeto")
cab(ws, 3, ["Código", "Nível", "Descrição", "Pai", "Ativ.", "Quantidade", "Unid.", "Regime", "Custo orçado (R$)", "% do total", "Comentário"])
eap = t["02_eap"].copy()
eap["pai"] = eap.codigo_eap_pai.map(lambda x: "" if pd.isna(x) else ("1" if x == 1.0 else str(x)))
atv_por_eap = a.reset_index().set_index("codigo_eap")
r0 = 4; rows_eap = {}
for k, e in enumerate(eap.itertuples()):
    r = r0 + k; rows_eap[e.codigo_eap] = r
n_last = r0 + len(eap) - 1
for k, e in enumerate(eap.itertuples()):
    r = r0 + k
    put(ws, r, 1, str(e.codigo_eap), entrada=True, bold=e.nivel < 3)
    put(ws, r, 2, int(e.nivel), entrada=True)
    c = put(ws, r, 3, ("    " * (e.nivel - 1)) + e.descricao, entrada=True, bold=e.nivel < 3)
    put(ws, r, 4, e.pai, entrada=True)
    if e.codigo_eap in atv_por_eap.index:
        x = atv_por_eap.loc[e.codigo_eap]
        put(ws, r, 5, x.id_atividade, entrada=True); put(ws, r, 6, float(x.quantidade_orcada), '#,##0.0', entrada=True)
        put(ws, r, 7, x.unidade, entrada=True); put(ws, r, 8, x.regime_execucao, entrada=True)
        put(ws, r, 9, float(orc.custo_total_rs[x.id_atividade]), R, entrada=True)
    elif e.tipo_item == "INDIRETO":
        put(ws, r, 9, 0, R, entrada=True); nota(ws, r, "(indireto — fora do custo direto)", 6)
    else:
        put(ws, r, 9, f'=SUMIF($D${r0}:$D${n_last},A{r},$I${r0}:$I${n_last})', R, bold=True, fill=FILL_T)
    put(ws, r, 10, f"=I{r}/$I${r0}", P)
    put(ws, r, 11, COMENT.get(str(e.codigo_eap), ""))
rr = n_last + 2
put(ws, rr, 3, "Orçamento de custo direto (tabela 01)", bold=True); put(ws, rr, 9, 28116171.71, R, entrada=True)
put(ws, rr + 1, 3, "Regra dos 100%: diferença EAP − orçamento", bold=True); put(ws, rr + 1, 9, f"=I{r0}-I{rr}", R)
put(ws, rr + 2, 3, "Confere?", bold=True); put(ws, rr + 2, 9, f'=IF(ABS(I{rr+1})<0.01,"SIM","NÃO")')
ws.freeze_panes = "D4"
salvar(wb, "D1_EAP_comentada.xlsx")

# =============== D2 · Rede (refeito no padrão) ===============
wb = novo("Rede e caminho crítico", "D2",
          ["Duração das atividades por esforço = ARRED.PARA.CIMA(quantidade × RUP ÷ (efetivo × 8 h)); efetivo = soma da mão de obra da atividade na tabela 07 (Anexo D).",
           "Atividades de duração fixa usam duracao_fixa_du da tabela 03.",
           "Rede em dias úteis: TI → início ≥ término da predecessora + 1 + defasagem; II → início ≥ início da predecessora + defasagem. Dia útil 1 = 18/02/2026 (16 e 17/02 são Carnaval).",
           "Datas mais cedo/mais tarde calculadas por ida e volta (scripts/calculos.py); a planilha recalcula duração, términos e folgas.",
           "Quase crítica = folga total de 1 a 5 dias úteis."],
          ["03_atividades", "04_dependencias", "07_atividade_recursos", "11_calendario"])
ws = aba(wb, "Rede", [7, 44, 8, 8, 9, 10, 8, 8, 10, 6, 6, 6, 6, 8, 8, 9, 12, 12, 28])
titulo(ws, 1, "D2 · Rede, datas e folgas da linha de base")
cab(ws, 3, ["Ativ.", "Nome", "EAP", "Tipo", "Qtd", "RUP (Hh/un)", "Efetivo", "Dur. fixa", "Duração (du)", "ES", "EF", "LS", "LF",
            "Folga total", "Crítica", "Quase crít.", "Início (data)", "Término (data)", "Predecessoras"])
CALR = calendario(wb, cal)
dep = t["04_dependencias"]
for k, i in enumerate(a.index):
    r = 4 + k; b = base.loc[i]; x = a.loc[i]
    pr = "; ".join(f"{d.id_atividade_predecessora} ({d.tipo_dependencia}{'+' + str(d.defasagem_du) if d.defasagem_du else ''})"
                   for d in dep[dep.id_atividade_sucessora == i].itertuples())
    linha(ws, r, [i, x.nome_atividade, x.codigo_eap, x.tipo_duracao, float(x.quantidade_orcada),
                  None if pd.isna(x.rup_orcada_hh_un) else float(x.rup_orcada_hh_un), int(C.efetivo.get(i, 0)),
                  None if pd.isna(x.duracao_fixa_du) else int(x.duracao_fixa_du),
                  f'=IF(D{r}="FIXA",H{r},ROUNDUP(E{r}*F{r}/(G{r}*8),0))', int(b.es_du), f"=J{r}+I{r}-1", int(b.ls_du), f"=L{r}+I{r}-1",
                  f"=L{r}-J{r}", f'=IF(N{r}=0,"SIM","")', f'=IF(AND(N{r}>0,N{r}<=5),"SIM","")',
                  f"=VLOOKUP(J{r},{CALR},2,FALSE)", f"=VLOOKUP(K{r},{CALR},2,FALSE)", pr],
          {5: '#,##0.0', 6: '0.000', 17: D, 18: D}, entrada_cols={1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 19})
    if b.critica:
        for c in ws[r][:18]: c.font = Font(name=ARIAL, size=10, bold=True, color="C0392B")
n = 3 + len(a)
r = n + 2
put(ws, r, 2, "Duração do projeto (du)", bold=True); put(ws, r, 9, f"=MAX(K4:K{n})")
put(ws, r + 1, 2, "Término da linha de base", bold=True); put(ws, r + 1, 9, f"=VLOOKUP(I{r},{CALR},2,FALSE)", D)
put(ws, r + 2, 2, "Data contratual", bold=True); put(ws, r + 2, 9, pd.Timestamp("2027-03-23"), D, entrada=True)
put(ws, r + 3, 2, "Folga do projeto até o contrato (du)", bold=True); put(ws, r + 3, 9, f"=271-I{r}")
put(ws, r + 4, 2, "Caminho crítico", bold=True); put(ws, r + 4, 3, " → ".join(base[base.critica].sort_values("es_du").index))
ws.freeze_panes = "C4"
salvar(wb, "D2_rede_caminho_critico.xlsx")

# =============== D3 · Gantt (grade semanal) ===============
wb = novo("Cronograma de Gantt (linha de base)", "D3",
          ["Linha de base = datas mais cedo do D2, em dias úteis reais do calendário (tabela 11).",
           "Opção 2 do Anexo C: grade com uma coluna por semana. A fórmula marca 1 quando a semana cruza o intervalo ES–EF da atividade; a formatação condicional pinta: azul = crítica, cinza = não crítica, roxo = atividade concluída (avanço real 100%).",
           "Avanço real até o fim do histórico (06/11/2026), tabela 16. A coluna da data de status (13/11/2026) fica com borda vermelha.",
           "Marcos: início (18/02/2026), término da linha de base e data contratual (23/03/2027)."],
          ["D2 (ES/EF/folga)", "11_calendario", "16_rdo_producao"])
ws = aba(wb, "Gantt", [6, 34, 7, 6, 6, 8, 8])
semanas = cal[cal.dia_util_projeto.notna() & (cal.dia_util_projeto <= 275)].groupby("semana").agg(ini=("dia_util_projeto", "min"), fim=("dia_util_projeto", "max"), d=("data_dt", "min"))
titulo(ws, 1, "D3 · Gantt da linha de base (uma coluna por semana)")
cab(ws, 4, ["Ativ.", "Nome", "Folga", "ES", "EF", "Crítica", "% real"])
C0 = 8
for j, s in enumerate(semanas.itertuples()):
    col = C0 + j; ws.column_dimensions[L(col)].width = 3.2
    put(ws, 2, col, int(s.ini), entrada=True); put(ws, 3, col, int(s.fim), entrada=True)
    c = put(ws, 4, col, s.d.strftime("%d/%m"), entrada=True); c.alignment = Alignment(text_rotation=90); c.font = Font(name=ARIAL, size=7)
put(ws, 2, C0 - 1, "du início ↓", bold=True); put(ws, 3, C0 - 1, "du fim ↓", bold=True)
ws.row_dimensions[4].height = 40
lastc = L(C0 + len(semanas) - 1)
ordem = base.sort_values("es_du").index
for k, i in enumerate(ordem):
    r = 5 + k; b = base.loc[i]
    linha(ws, r, [i, a.nome_atividade[i][:40], int(b.folga_total_du), int(b.es_du), int(b.ef_du), "SIM" if b.critica else "", float(pct_real[i])],
          {7: '0%'}, entrada_cols={1, 2, 3, 4, 5, 6, 7})
    for j in range(len(semanas)):
        cl = L(C0 + j)
        c = ws.cell(r, C0 + j, f'=IF(AND({cl}$2<=$E{r},{cl}$3>=$D{r}),1,"")'); c.font = Font(name=ARIAL, size=7, color="FFFFFF")
nr = 4 + len(ordem)
area = f"{L(C0)}5:{lastc}{nr}"
ws.conditional_formatting.add(area, FormulaRule(formula=[f'AND({L(C0)}5=1,$G5>=1)'], fill=PatternFill("solid", fgColor="7B3FA0"), stopIfTrue=True))
ws.conditional_formatting.add(area, FormulaRule(formula=[f'AND({L(C0)}5=1,$F5="SIM")'], fill=PatternFill("solid", fgColor="1F5FBF"), stopIfTrue=True))
ws.conditional_formatting.add(area, FormulaRule(formula=[f'{L(C0)}5=1'], fill=PatternFill("solid", fgColor="A9B4C2"), stopIfTrue=True))
from openpyxl.styles import Border, Side
red = Side(style="medium", color="C00000")
col_status = C0 + list(semanas.index).index("2026-S46")
for r in range(2, nr + 1):
    ws.cell(r, col_status).border = Border(left=red, right=red)
put(ws, 1, col_status, "status 13/11", bold=True).font = Font(name=ARIAL, size=8, bold=True, color="C00000")
r = nr + 2
for rot, v in [("Marco · início do projeto", "18/02/2026"), ("Marco · término da linha de base", base.termino_cedo.max()),
               ("Marco · data contratual", "23/03/2027"), ("Legenda", "azul = crítica · cinza = não crítica · roxo = concluída · coluna com borda vermelha = data de status")]:
    put(ws, r, 2, rot, bold=True); put(ws, r, 3, str(v)); r += 1
ws.freeze_panes = ws.cell(5, C0)
salvar(wb, "D3_Gantt.xlsx")

# =============== D4 · Histograma e nivelamento ===============
def perfil(es):
    p = {}
    for i in a.index:
        e = int(C.efetivo.get(i, 0))
        for d in range(es[i], es[i] + int(base.duracao_du[i])): p[d] = p.get(d, 0) + e
    return p

es0 = {i: int(base.es_du[i]) for i in a.index}
dep = t["04_dependencias"]
def es_min(i, es):
    m = 1
    for d in dep[dep.id_atividade_sucessora == i].itertuples():
        p = d.id_atividade_predecessora
        m = max(m, es[p] + int(base.duracao_du[p]) + d.defasagem_du if d.tipo_dependencia == "TI" else es[p] + d.defasagem_du)
    return m
def succ_ok(i, s, es):
    for d in dep[dep.id_atividade_predecessora == i].itertuples():
        j = d.id_atividade_sucessora
        need = s + int(base.duracao_du[i]) + d.defasagem_du if d.tipo_dependencia == "TI" else s + d.defasagem_du
        if es[j] < need: return False
    return True
# nivelamento: desloca atividades com folga (das mais tardias para as mais cedo) para reduzir o pico, sem mexer no prazo
esn = dict(es0)
for _ in range(3):
    for i in sorted(a.index, key=lambda x: -es0[x]):
        if base.folga_total_du[i] == 0 or C.efetivo.get(i, 0) == 0: continue
        melhor, pico_m = esn[i], None
        for s in range(es_min(i, esn), int(base.ls_du[i]) + 1):
            if not succ_ok(i, s, esn): break
            tmp = dict(esn); tmp[i] = s; pk = max(perfil(tmp).values())
            if pico_m is None or pk < pico_m or (pk == pico_m and s == esn[i]): melhor, pico_m = s, pk
        esn[i] = melhor
pico0, picon = max(perfil(es0).values()), max(perfil(esn).values())
fim0 = max(es0[i] + base.duracao_du[i] - 1 for i in a.index); fimn = max(esn[i] + base.duracao_du[i] - 1 for i in a.index)
print("D4 pico", pico0, "→", picon, "fim", fim0, fimn)

wb = novo("Histograma de mão de obra e nivelamento", "D4",
          ["Efetivo de cada atividade = soma das funções de mão de obra da tabela 07; a atividade ocupa a equipe completa em todos os seus dias úteis.",
           "Efetivo médio da semana = efetivo × dias úteis da atividade na semana ÷ dias úteis da semana (fórmula com MÍNIMO/MÁXIMO).",
           "Homens-dia = efetivo × duração. Pico e média calculados sobre as semanas com efetivo > 0.",
           f"Nivelamento: só atividades com folga foram deslocadas (sem violar a rede), para respeitar o máximo de 130 pessoas no canteiro sem alterar o término ({base.termino_cedo.max()}).",
           f"Resultado: pico diário de {pico0} → {picon} pessoas; término {fim0} → {fimn} du (inalterado)."],
          ["D2 (ES, duração, folga)", "07_atividade_recursos", "05_funcoes_mao_de_obra", "01_projeto_parametros (efetivo máximo 130)"])
sem = cal[cal.dia_util_projeto.notna() & (cal.dia_util_projeto <= fim0)].groupby("semana").agg(ini=("dia_util_projeto", "min"), fim=("dia_util_projeto", "max"))
for nome_aba, ESX in [("Linha de base", es0), ("Nivelado", esn)]:
    ws = aba(wb, nome_aba, [6, 7, 8, 6, 6, 9])
    titulo(ws, 1, f"D4 · Efetivo médio por semana — {nome_aba.lower()}")
    cab(ws, 4, ["Ativ.", "Função", "Efetivo", "ES", "EF", "Homens-dia"])
    put(ws, 2, 6, "du início →", bold=True); put(ws, 3, 6, "du fim →", bold=True)
    for j, s in enumerate(sem.itertuples()):
        col = 7 + j; ws.column_dimensions[L(col)].width = 5.5
        put(ws, 2, col, int(s.ini), entrada=True); put(ws, 3, col, int(s.fim), entrada=True)
        c = put(ws, 4, col, s.Index[2:], entrada=True); c.alignment = Alignment(text_rotation=90); c.font = Font(name=ARIAL, size=7)
    r = 5
    for i in sorted(a.index, key=lambda x: ESX[x]):
        for f in mo[mo.id_atividade == i].itertuples():
            linha(ws, r, [i, f.codigo_recurso, int(f.quantidade), ESX[i], f"=D{r}+{int(base.duracao_du[i])}-1", f"=C{r}*(E{r}-D{r}+1)"],
                  entrada_cols={1, 2, 3, 4})
            for j in range(len(sem)):
                cl = L(7 + j)
                ws.cell(r, 7 + j, f"=$C{r}*MAX(0,MIN($E{r},{cl}$3)-MAX($D{r},{cl}$2)+1)/({cl}$3-{cl}$2+1)").number_format = '0.0'
                ws.cell(r, 7 + j).font = Font(name=ARIAL, size=8)
            r += 1
    last = r - 1; rt = r + 1
    put(ws, rt, 1, "TOTAL (média/dia)", bold=True)
    for j in range(len(sem)):
        cl = L(7 + j); put(ws, rt, 7 + j, f"=SUM({cl}5:{cl}{last})", '0', bold=True, fill=FILL_T)
    funcs = sorted(mo.codigo_recurso.unique())
    for k, f in enumerate(funcs):
        rr = rt + 1 + k; put(ws, rr, 1, "Função", bold=True); put(ws, rr, 2, f, bold=True)
        for j in range(len(sem)):
            cl = L(7 + j); put(ws, rr, 7 + j, f'=SUMIF($B$5:$B${last},$B{rr},{cl}5:{cl}{last})', '0')
    rs = rt + len(funcs) + 2
    lc = L(6 + len(sem))
    put(ws, rs, 1, "Pico semanal (média/dia)", bold=True); put(ws, rs, 6, f"=MAX(G{rt}:{lc}{rt})", '0')
    put(ws, rs + 1, 1, "Média das semanas com efetivo", bold=True); put(ws, rs + 1, 6, f'=SUM(G{rt}:{lc}{rt})/COUNTIF(G{rt}:{lc}{rt},">0")', '0')
    put(ws, rs + 2, 1, "Homens-dia totais", bold=True); put(ws, rs + 2, 6, f"=SUM(F5:F{last})", R0)
    put(ws, rs + 3, 1, "Efetivo máximo do canteiro", bold=True); put(ws, rs + 3, 6, 130, entrada=True, fill=FILL_Y)
    put(ws, rs + 4, 1, "Semanas acima do máximo", bold=True); put(ws, rs + 4, 6, f'=COUNTIF(G{rt}:{lc}{rt},">"&F{rs+3})')
    ch = BarChart(); ch.title = f"Efetivo médio por semana — {nome_aba}"; ch.y_axis.title = "pessoas"; ch.height = 8; ch.width = 26
    ch.add_data(Reference(ws, min_col=7, max_col=6 + len(sem), min_row=rt), from_rows=True, titles_from_data=False)
    ch.set_categories(Reference(ws, min_col=7, max_col=6 + len(sem), min_row=4)); ch.legend = None
    ch.roundedCorners = False; ch.x_axis.delete = False; ch.y_axis.delete = False
    ws.add_chart(ch, f"A{rs + 7}")
    ws.freeze_panes = "G5"
desloc = [(i, es0[i], esn[i]) for i in a.index if es0[i] != esn[i]]
ws = aba(wb, "Deslocamentos", [8, 40, 10, 10, 10, 10])
titulo(ws, 1, "Atividades deslocadas no nivelamento (só com folga)")
cab(ws, 3, ["Ativ.", "Nome", "ES base", "ES nivelado", "Desloc. (du)", "Folga total"])
for k, (i, e0, e1) in enumerate(desloc):
    linha(ws, 4 + k, [i, a.nome_atividade[i], e0, e1, f"=D{4+k}-C{4+k}", int(base.folga_total_du[i])], entrada_cols={1, 2, 3, 4, 6})
r = 5 + len(desloc)
put(ws, r, 2, "Pico diário antes / depois", bold=True); put(ws, r, 3, pico0, entrada=True); put(ws, r, 4, picon, entrada=True)
nota(ws, r + 1, "O pico dimensiona as áreas de vivência (vestiários, refeitório, sanitários — NR-18), EPIs, transporte e a supervisão do canteiro.")
salvar(wb, "D4_histograma_nivelamento.xlsx")
D4_RES = {"pico0": pico0, "picon": picon, "desloc": desloc}

# =============== D5 · Plano de equipamentos ===============
eqc = t["06_equipamentos"]
tipos = eqc.groupby("tipo_equipamento").agg(desc=("descricao", "first"), diaria=("diaria_orcada_rs", "mean"), compra=("valor_compra_novo_rs", "mean"),
                                             manut=("custo_manutencao_mensal_proprio_rs", "mean"), vida=("vida_util_anos", "mean"))
wb = novo("Plano de equipamentos de obra", "D5",
          ["Equipamentos por atividade e quantidade: tabela 07 (tipo_recurso = EQUIPAMENTO). Entrada = início da atividade (ES) e saída = término (EF) da linha de base.",
           "Custo de locação previsto = quantidade × diárias (dias úteis da atividade) × diária orçada média do tipo (tabela 06).",
           "Locar × comprar (2 tipos de maior custo): compra = valor do equipamento novo − valor residual (depreciação linear pela vida útil) + manutenção própria mensal × meses de uso. Meses = diárias ÷ 21.",
           "Premissas de compra (células amarelas): custo de capital 1,0% ao mês sobre o valor investido; revenda no fim do uso pelo valor residual contábil com deságio de 15%."],
          ["07_atividade_recursos", "06_equipamentos", "D2"])
CALR = calendario(wb, cal)
ws = aba(wb, "Plano", [7, 8, 34, 6, 7, 7, 12, 12, 9, 12, 14])
titulo(ws, 1, "D5 · Entrada, saída e custo de locação previsto")
cab(ws, 3, ["Ativ.", "Tipo", "Equipamento", "Qtd", "ES", "EF", "Entrada", "Saída", "Diárias", "Diária orçada (R$)", "Custo previsto (R$)"])
r = 4
for e in eqr.sort_values("id_atividade").itertuples():
    b = base.loc[e.id_atividade]; tp = tipos.loc[e.codigo_recurso]
    linha(ws, r, [e.id_atividade, e.codigo_recurso, tp.desc, int(e.quantidade), int(b.es_du), int(b.ef_du),
                  f"=VLOOKUP(E{r},{CALR},2,FALSE)", f"=VLOOKUP(F{r},{CALR},2,FALSE)", f"=F{r}-E{r}+1", round(float(tp.diaria), 2), f"=D{r}*I{r}*J{r}"],
          {7: D, 8: D, 10: R, 11: R}, entrada_cols={1, 2, 3, 4, 5, 6, 10})
    r += 1
last = r - 1
put(ws, r + 1, 3, "TOTAL locação prevista", bold=True); put(ws, r + 1, 11, f"=SUM(K4:K{last})", R, bold=True)
ws2 = aba(wb, "Resumo por tipo", [8, 34, 12, 16])
cab(ws2, 1, ["Tipo", "Equipamento", "Diárias", "Custo previsto (R$)"])
tot_tipo = {}
for k, tp in enumerate(sorted(eqr.codigo_recurso.unique())):
    rr = 2 + k
    linha(ws2, rr, [tp, tipos.desc[tp], f"=SUMIF(Plano!$B$4:$B${last},A{rr},Plano!$I$4:$I${last})", f"=SUMIF(Plano!$B$4:$B${last},A{rr},Plano!$K$4:$K${last})"],
          {4: R}, entrada_cols={1, 2})
    sub = eqr[eqr.codigo_recurso == tp]
    tot_tipo[tp] = sum(q * (base.duracao_du[i]) * tipos.diaria[tp] for i, q in zip(sub.id_atividade, sub.quantidade))
top2 = sorted(tot_tipo, key=tot_tipo.get, reverse=True)[:2]
ws3 = aba(wb, "Locar x comprar", [44, 16, 16])
titulo(ws3, 1, "Locar × comprar — dois tipos de maior custo de locação")
cab(ws3, 3, ["Item", top2[0], top2[1]])
put(ws3, 2, 1, "Custo de capital (% ao mês)", bold=True); put(ws3, 2, 2, 0.01, '0.0%', entrada=True, fill=FILL_Y)
put(ws3, 2, 3, "Deságio na revenda", bold=True); put(ws3, 2, 4, 0.15, '0%', entrada=True, fill=FILL_Y)
itens = [("Diárias previstas (todas as unidades)", [f"=SUMIF(Plano!$B$4:$B${last},\"{x}\",Plano!$I$4:$I${last})" for x in top2], R0, False),
         ("Custo de locação (R$)", [f"=SUMIF(Plano!$B$4:$B${last},\"{x}\",Plano!$K$4:$K${last})" for x in top2], R, False),
         ("Unidades simultâneas (máx. por atividade)", [int(eqr[eqr.codigo_recurso == x].quantidade.max()) for x in top2], R0, True),
         ("Meses de uso por unidade (diárias ÷ unidades ÷ 21)", ["=B4/B6/21", "=C4/C6/21"], '0.0', False),
         ("Valor de compra por unidade (R$)", [float(tipos.compra[x]) for x in top2], R, True),
         ("Vida útil (anos)", [float(tipos.vida[x]) for x in top2], '0', True),
         ("Valor de revenda = residual contábil × (1 − deságio) (R$)", ["=B8*B6*(1-B7/(B9*12))*(1-$D$2)", "=C8*C6*(1-C7/(C9*12))*(1-$D$2)"], R, False),
         ("Manutenção própria mensal por unidade (R$)", [float(tipos.manut[x]) for x in top2], R, True),
         ("Custo de capital = valor × taxa × meses (R$)", ["=B8*B6*$B$2*B7", "=C8*C6*$B$2*C7"], R, False),
         ("Custo de comprar = compra − revenda + manutenção + capital (R$)", ["=B8*B6-B10+B11*B7*B6+B12", "=C8*C6-C10+C11*C7*C6+C12"], R, False),
         ("Decisão", ['=IF(B5<B13,"LOCAR","COMPRAR")', '=IF(C5<C13,"LOCAR","COMPRAR")'], None, False)]
for k, (rot, vals, fm, ent) in enumerate(itens):
    rr = 4 + k; put(ws3, rr, 1, rot, bold=k == 10)
    for j, v in enumerate(vals): put(ws3, rr, 2 + j, v, fm, entrada=ent, bold=k == 10)
nota(ws3, 16, "Leitura: com poucos meses de uso, custo de capital, deságio na revenda e manutenção própria superam a locação. Comprar só compensa com uso futuro garantido.")
salvar(wb, "D5_plano_equipamentos.xlsx")

# =============== D6 · Curva ABC e plano de compras ===============
am = t["09_atividade_materiais"]; mats = t["08_materiais"].set_index("id_material")
lin = []
for m in mats.index:
    usos = am[am.id_material == m]
    q = sum(a.quantidade_orcada[x.id_atividade] * x.consumo_por_unidade for x in usos.itertuples()) * (1 + mats.perda_orcada_pct[m] / 100)
    q_sem = sum(a.quantidade_orcada[x.id_atividade] * x.consumo_por_unidade for x in usos.itertuples())
    prim = min(usos.id_atividade, key=lambda x: base.es_du[x])
    lin.append((m, mats.descricao[m], mats.unidade[m], q_sem, mats.perda_orcada_pct[m] / 100, mats.preco_orcado_rs[m], prim, int(base.es_du[prim]), int(mats.lead_time_du[m]),
                q * mats.preco_orcado_rs[m]))
lin.sort(key=lambda x: -x[-1])
ped = t["18_compras_pedidos"]
wb = novo("Curva ABC e plano de compras", "D6",
          ["Quantidade de cada insumo = Σ (quantidade orçada da atividade × consumo por unidade) × (1 + perda orçada). Custo orçado = quantidade × preço orçado.",
           "Classes: A até 80% do custo acumulado, B de 80% a 95%, C acima de 95%.",
           "Data-limite de pedido = data de uso (início da primeira atividade que usa o insumo, linha de base) − lead time − margem de segurança (5 dias úteis, célula amarela).",
           "Comparação com o 1º pedido real (tabela 18): pedido depois da data-limite = risco de atraso."],
          ["08_materiais", "09_atividade_materiais", "03_atividades", "D2", "18_compras_pedidos", "11_calendario"])
CALR = calendario(wb, cal)
ws = aba(wb, "ABC", [7, 34, 7, 12, 7, 12, 14, 9, 9, 7, 7, 8, 12, 12, 12, 11])
titulo(ws, 1, "D6 · Curva ABC dos insumos e data-limite de pedido")
put(ws, 2, 1, "Margem de segurança (du)", bold=True); put(ws, 2, 4, 5, entrada=True, fill=FILL_Y)
cab(ws, 4, ["Insumo", "Descrição", "Unid.", "Qtd s/ perda", "Perda", "Preço (R$)", "Custo orçado (R$)", "% do total", "% acum.", "Classe",
            "1ª ativ.", "du de uso", "Lead time (du)", "Data de uso", "Data-limite pedido", "1º pedido real"])
n = len(lin); lastr = 4 + n
for k, x in enumerate(lin):
    r = 5 + k
    p1 = ped[ped.id_material == x[0]].data_pedido.min()
    linha(ws, r, [x[0], x[1], x[2], round(x[3], 2), x[4], x[5], f"=D{r}*(1+E{r})*F{r}", f"=G{r}/SUM($G$5:$G${lastr})",
                  f"=H{r}" if k == 0 else f"=I{r-1}+H{r}", f'=IF(I{r}<=0.8,"A",IF(I{r}<=0.95,"B","C"))', x[6], x[7], x[8],
                  f"=VLOOKUP(L{r},{CALR},2,FALSE)", f"=VLOOKUP(MAX(1,L{r}-M{r}-$D$2),{CALR},2,FALSE)",
                  pd.Timestamp(p1) if isinstance(p1, str) else "sem pedido"],
          {4: '#,##0.00', 5: '0%', 6: R, 7: R, 8: P, 9: P, 14: D, 15: D, 16: D}, entrada_cols={1, 2, 3, 4, 5, 6, 11, 12, 13, 16})
ws.conditional_formatting.add(f"P5:P{lastr}", FormulaRule(formula=['AND(ISNUMBER(P5),P5>O5)'], fill=PatternFill("solid", fgColor="F8D7DA")))
r = lastr + 2
put(ws, r, 2, "Total", bold=True); put(ws, r, 7, f"=SUM(G5:G{lastr})", R, bold=True)
for k, cl in enumerate("ABC"):
    put(ws, r + 1 + k, 2, f"Classe {cl}: nº de itens / custo", bold=True)
    put(ws, r + 1 + k, 4, f'=COUNTIF(J5:J{lastr},"{cl}")'); put(ws, r + 1 + k, 7, f'=SUMIF(J5:J{lastr},"{cl}",G5:G{lastr})', R)
nota(ws, r + 5, "Vermelho na coluna P: o primeiro pedido saiu depois da data-limite.")
ch = LineChart(); ch.title = "Curva ABC (% acumulado)"; ch.height = 8; ch.width = 18
ch.add_data(Reference(ws, min_col=9, min_row=4, max_row=lastr), titles_from_data=True); ch.set_categories(Reference(ws, min_col=1, min_row=5, max_row=lastr))
ch.roundedCorners = False; ch.x_axis.delete = False; ch.y_axis.delete = False; ch.legend = None
ws.add_chart(ch, f"B{r + 8}")
ws.freeze_panes = "C5"
salvar(wb, "D6_curva_ABC_compras.xlsx")

# =============== D7 · Mapa de contratações ===============
JUST = {
    "CONTRATADA": ("Serviço especializado (projeto, licença, software, fabricação, RH) que a empresa não executa; preço por entrega/medição.",
                   "Transfere ao contratado o risco técnico e de produtividade; a empresa fica com o risco de prazo de interface e de aprovação."),
    "PROPRIA": ("Serviço com mão de obra comum ou montagem crítica que exige controle direto de equipe e sequência (Last Planner).",
                "A empresa assume todo o risco de produtividade, absenteísmo, hora extra e equipamento (ex.: RUP real acima da orçada)."),
    "EMPREITADA": ("Serviço repetitivo com fornecimento técnico específico (estrutura, cobertura, fechamento, painéis, incêndio), pago por preço unitário.",
                   "Transfere o risco de produtividade ao empreiteiro (preço unitário fixo); a empresa mantém o risco de prazo, de material próprio e de liberação de frente."),
}
wb = novo("Mapa de contratações", "D7",
          ["Regime de cada pacote conforme a tabela 03 (própria, empreitada ou contratada).",
           "Justificativa e risco transferido avaliados pelo grupo; preço unitário de empreitada da tabela 03.",
           "Observação do histórico: as empreitadas de estrutura/cobertura/fechamento (A09–A11) ficaram com RUP real 55% a 81% acima da orçada; parte desse risco volta para a empresa na forma de prazo."],
          ["03_atividades", "12_orcamento_linha_de_base"])
ws = aba(wb, "Mapa", [7, 44, 12, 14, 14, 60, 60])
titulo(ws, 1, "D7 · Própria × empreitada × contratada")
cab(ws, 3, ["Ativ.", "Pacote", "Regime", "Preço unit. empreitada (R$)", "Custo orçado (R$)", "Justificativa", "Risco que o regime transfere / mantém"])
for k, i in enumerate(a.index):
    r = 4 + k; reg = a.regime_execucao[i]
    linha(ws, r, [i, a.nome_atividade[i], reg, None if pd.isna(a.preco_unitario_empreitada_rs[i]) else float(a.preco_unitario_empreitada_rs[i]),
                  float(orc.custo_total_rs[i]), JUST[reg][0], JUST[reg][1]], {4: R, 5: R}, entrada_cols={1, 2, 3, 4, 5})
    for c in (6, 7): ws.cell(r, c).alignment = Alignment(wrap_text=True, vertical="top")
last = 3 + len(a)
r = last + 2
for k, reg in enumerate(["PROPRIA", "EMPREITADA", "CONTRATADA"]):
    put(ws, r + k, 2, f"Total {reg}", bold=True); put(ws, r + k, 3, f'=COUNTIF(C4:C{last},"{reg}")'); put(ws, r + k, 5, f'=SUMIF(C4:C{last},"{reg}",E4:E{last})', R)
    put(ws, r + k, 6, f"=E{r+k}/SUM($E$4:$E${last})", P)
salvar(wb, "D7_mapa_contratacoes.xlsx")

# =============== D8 · Físico-financeiro e curva S ===============
meses = sorted(cal[cal.dia_util_projeto.notna() & (cal.dia_util_projeto <= C.fim)].mes.unique())
du_mes = {}
for i in a.index:
    b = base.loc[i]
    for d in range(int(b.es_du), int(b.ef_du) + 1):
        m = du2dt[d].strftime("%Y-%m"); du_mes[(i, m)] = du_mes.get((i, m), 0) + 1
wb = novo("Físico-financeiro e curva S", "D8",
          ["Desembolso mensal orçado = custo orçado da atividade ÷ duração × dias úteis da atividade no mês (VP linear, Anexo D).",
           "Administração local: R$ 146.000 por mês do projeto (16/02/2026 a término da linha de base), somada ao custo direto para o orçamento no término total.",
           "Curva S = valor planejado acumulado mês a mês. A matriz de dias úteis por mês vem do calendário (tabela 11) e da linha de base (D2)."],
          ["D2", "12_orcamento_linha_de_base", "01_projeto_parametros", "11_calendario"])
ws = aba(wb, "Cronograma financeiro", [7, 34, 14, 8] + [12] * len(meses))
titulo(ws, 1, "D8 · Desembolso mensal orçado (R$)")
put(ws, 2, 1, "Adm. local (R$/mês)", bold=True); put(ws, 2, 3, 146000, R, entrada=True, fill=FILL_Y)
cab(ws, 4, ["Ativ.", "Nome", "Custo orçado", "Duração (du)"] + meses)
r = 5
for i in a.index:
    linha(ws, r, [i, a.nome_atividade[i], float(orc.custo_total_rs[i]), int(base.duracao_du[i])], {3: R}, entrada_cols={1, 2, 3, 4})
    for j, m in enumerate(meses):
        dm = du_mes.get((i, m), 0)
        put(ws, r, 5 + j, f"=$C{r}/$D{r}*{dm}" if dm else 0, R0)
    r += 1
last = r - 1
lc = L(4 + len(meses))
rows = {"cd": r + 1, "adm": r + 2, "tot": r + 3, "ac_cd": r + 4, "ac": r + 5, "pct": r + 6}
put(ws, rows["cd"], 2, "Custo direto do mês", bold=True); put(ws, rows["adm"], 2, "Administração local", bold=True)
put(ws, rows["tot"], 2, "Desembolso total do mês", bold=True); put(ws, rows["ac_cd"], 2, "VP acumulado (custo direto)", bold=True)
put(ws, rows["ac"], 2, "Desembolso acumulado (com adm. local)", bold=True); put(ws, rows["pct"], 2, "% acumulado do total", bold=True)
for j in range(len(meses)):
    cl = L(5 + j); pv = L(4 + j)
    put(ws, rows["cd"], 5 + j, f"=SUM({cl}5:{cl}{last})", R0, bold=True, fill=FILL_T)
    put(ws, rows["adm"], 5 + j, "=$C$2", R0)
    put(ws, rows["tot"], 5 + j, f"={cl}{rows['cd']}+{cl}{rows['adm']}", R0, bold=True)
    put(ws, rows["ac_cd"], 5 + j, f"={cl}{rows['cd']}" if j == 0 else f"={pv}{rows['ac_cd']}+{cl}{rows['cd']}", R0)
    put(ws, rows["ac"], 5 + j, f"={cl}{rows['tot']}" if j == 0 else f"={pv}{rows['ac']}+{cl}{rows['tot']}", R0)
    put(ws, rows["pct"], 5 + j, f"={cl}{rows['ac']}/${lc}${rows['ac']}", P)
rb = rows["pct"] + 2
put(ws, rb, 2, "Orçamento no término — custo direto", bold=True); put(ws, rb, 3, f"=SUM(C5:C{last})", R)
put(ws, rb + 1, 2, "Orçamento no término — adm. local", bold=True); put(ws, rb + 1, 3, f"=SUM(E{rows['adm']}:{lc}{rows['adm']})", R)
put(ws, rb + 2, 2, "Orçamento no término — total", bold=True); put(ws, rb + 2, 3, f"=C{rb}+C{rb+1}", R, bold=True)
ch = LineChart(); ch.title = "Curva S — desembolso acumulado (R$)"; ch.height = 9; ch.width = 26
ch.add_data(Reference(ws, min_col=4, max_col=4 + len(meses), min_row=rows["ac_cd"]), from_rows=True, titles_from_data=True)
ch.add_data(Reference(ws, min_col=4, max_col=4 + len(meses), min_row=rows["ac"]), from_rows=True, titles_from_data=True)
ch.set_categories(Reference(ws, min_col=5, max_col=4 + len(meses), min_row=4))
put(ws, rows["ac_cd"], 4, "VP direto"); put(ws, rows["ac"], 4, "Com adm. local")
ch.roundedCorners = False; ch.x_axis.delete = False; ch.y_axis.delete = False; ch.legend.position = "b"; ch.legend.overlay = False
ws.add_chart(ch, f"B{rb + 5}")
ws.freeze_panes = "E5"
salvar(wb, "D8_fisico_financeiro_curva_S.xlsx")

import json
(DOCS / "_d4.json").write_text(json.dumps({"pico0": int(pico0), "picon": int(picon), "desloc": [(i, int(x), int(y)) for i, x, y in desloc]}))
