"""Linha de base (CPM) e valor agregado do G3, pelas convenções do Anexo D.

Uso:  python scripts/calculos.py   (depois de scripts/limpeza.py)
Gera:
  docs/D2_rede_caminho_critico.csv   durações, datas cedo/tarde, folgas, críticas
  docs/valor_agregado.csv            VP, VA, CR, IDP, IDC por fase em datas de corte
  app/data/g3.json                   tabelas tratadas + linha de base para o sistema
"""
import json, math
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
T = RAIZ / "dados" / "tratados"
tab = {p.stem: pd.read_csv(p) for p in sorted(T.glob("*.csv"))}

# ---------- calendário: dia útil do projeto <-> data ----------
cal = tab["11_calendario"]
du = cal.dropna(subset=["dia_util_projeto"]).astype({"dia_util_projeto": int})
du2data = dict(zip(du.dia_util_projeto, du.data))
data2du = dict(zip(du.data, du.dia_util_projeto))


def du_ate(data):  # número de dias úteis do projeto até a data (inclusive)
    return int(du[du.data <= data].dia_util_projeto.max())


# ---------- durações (Anexo D) ----------
a = tab["03_atividades"].set_index("id_atividade")
rec = tab["07_atividade_recursos"]
efetivo = rec[rec.tipo_recurso == "MAO_DE_OBRA"].groupby("id_atividade").quantidade.sum()
orc = tab["12_orcamento_linha_de_base"].set_index("id_atividade").custo_total_rs


def duracao(i):
    r = a.loc[i]
    if r.tipo_duracao == "FIXA":
        return int(r.duracao_fixa_du)
    return math.ceil(r.quantidade_orcada * r.rup_orcada_hh_un / (efetivo[i] * 8) - 1e-9)


ativ = list(a.index)
D = {i: duracao(i) for i in ativ}


# ---------- CPM ----------
def cpm(ativ, D, dep):
    """ES/EF em dias úteis (dia 1 = início). TI: ES >= EF_pred + 1 + lag; II: ES >= ES_pred + lag."""
    preds = {i: [] for i in ativ}
    for r in dep.itertuples():
        if r.id_atividade_sucessora in preds and r.id_atividade_predecessora in preds:
            preds[r.id_atividade_sucessora].append((r.id_atividade_predecessora, r.tipo_dependencia, int(r.defasagem_du)))
    succs = {i: [] for i in ativ}
    for s, ps in preds.items():
        for p, tp, lag in ps:
            succs[p].append((s, tp, lag))
    ES, EF = {}, {}
    pend = set(ativ)
    while pend:
        for i in sorted(pend):
            if all(p in EF for p, _, _ in preds[i]):
                es = 1
                for p, tp, lag in preds[i]:
                    es = max(es, EF[p] + 1 + lag if tp == "TI" else ES[p] + lag)
                ES[i], EF[i] = es, es + D[i] - 1
                pend.discard(i)
    fim = max(EF.values())
    LS, LF = {}, {}
    pend = set(ativ)
    while pend:
        for i in sorted(pend):
            if all(s in LS for s, _, _ in succs[i]):
                lf = fim
                for s, tp, lag in succs[i]:
                    lf = min(lf, LS[s] - 1 - lag if tp == "TI" else LS[s] - lag + D[i] - 1)
                LF[i], LS[i] = lf, lf - D[i] + 1
                pend.discard(i)
    return ES, EF, LS, LF, fim


dep = tab["04_dependencias"]
ES, EF, LS, LF, fim = cpm(ativ, D, dep)
base = pd.DataFrame({
    "id_atividade": ativ, "nome": a.nome_atividade, "fase": a.fase, "codigo_eap": a.codigo_eap,
    "id_zona": a.id_zona, "duracao_du": [D[i] for i in ativ],
    "efetivo": [int(efetivo.get(i, 0)) for i in ativ],
    "es_du": [ES[i] for i in ativ], "ef_du": [EF[i] for i in ativ],
    "ls_du": [LS[i] for i in ativ], "lf_du": [LF[i] for i in ativ],
    "custo_orcado_rs": [float(orc[i]) for i in ativ]}).reset_index(drop=True)
base["folga_total_du"] = base.ls_du - base.es_du
base["critica"] = base.folga_total_du == 0
base["quase_critica"] = (base.folga_total_du > 0) & (base.folga_total_du <= 5)
base["inicio_cedo"] = base.es_du.map(du2data)
base["termino_cedo"] = base.ef_du.map(du2data)
base["inicio_tarde"] = base.ls_du.map(du2data)
base["termino_tarde"] = base.lf_du.map(du2data)

# ---------- sub-rede M1 (conferência com o caderno) ----------
sub = ["A23", "A24", "A25", "A26", "A27", "A28", "A29", "A30", "A31", "A35", "A36"]
ES1, EF1, LS1, LF1, fim1 = cpm(sub, D, dep)
m1 = pd.DataFrame({"atividade": sub, "dur": [D[i] for i in sub], "ES": [ES1[i] for i in sub], "EF": [EF1[i] for i in sub],
                   "LS": [LS1[i] for i in sub], "LF": [LF1[i] for i in sub]})
m1["folga"] = m1.LS - m1.ES

# ---------- valor agregado ----------
prod = tab["16_rdo_producao"]
custos = tab["20_custos_apropriados"]
fases = a.fase


def evm(data):
    n = du_ate(data)
    linhas = []
    for i in ativ:
        b = base.set_index("id_atividade").loc[i]
        pct_plan = min(1, max(0, (n - b.es_du + 1) / b.duracao_du))
        q = prod[(prod.id_atividade == i) & (prod.data <= data)].quantidade_executada.sum()
        pct_real = min(1, q / a.loc[i, "quantidade_orcada"])
        cr = custos[(custos.id_atividade == i) & (custos.data <= data) & (custos.categoria != "INDIRETO")].valor_rs.sum()
        linhas.append((i, fases[i], b.custo_orcado_rs, pct_plan, pct_real, b.custo_orcado_rs * pct_plan, b.custo_orcado_rs * pct_real, cr))
    d = pd.DataFrame(linhas, columns=["id_atividade", "fase", "orcamento", "pct_plan", "pct_real", "VP", "VA", "CR"])
    sem = custos[(custos.id_atividade.isna()) & (custos.data <= data) & (custos.categoria != "INDIRETO")].valor_rs.sum()
    return d, sem


def resumo(data):
    d, sem = evm(data)
    g = d.groupby("fase", sort=False)[["orcamento", "VP", "VA", "CR"]].sum()
    g.loc["TOTAL"] = g.sum()
    g.loc["TOTAL", "CR"] += sem
    g["VPr"], g["VC"] = g.VA - g.VP, g.VA - g.CR
    g["IDP"], g["IDC"] = g.VA / g.VP, g.VA / g.CR
    g["pct_previsto"], g["pct_fisico"] = g.VP / g.orcamento, g.VA / g.orcamento
    g.insert(0, "data_corte", data)
    return g.reset_index()


if __name__ == "__main__":
    (RAIZ / "docs").mkdir(exist_ok=True)
    base.to_csv(RAIZ / "docs" / "D2_rede_caminho_critico.csv", index=False)
    ev = pd.concat([resumo("2026-10-16"), resumo("2026-11-06")])
    ev.to_csv(RAIZ / "docs" / "valor_agregado.csv", index=False)

    pd.set_option("display.width", 250)
    print(f"Duração da linha de base: {fim} du · término {du2data[fim]} · contrato {du2data.get(271)} (du 271)")
    print("Caminho crítico:", " → ".join(base[base.critica].sort_values("es_du").id_atividade))
    print("Quase críticas:", ", ".join(base[base.quase_critica].id_atividade))
    print(base[["id_atividade", "duracao_du", "es_du", "ef_du", "folga_total_du", "inicio_cedo", "termino_cedo"]].to_string(index=False))
    print(f"\nM1 sub-rede: duração {fim1} du\n", m1.to_string(index=False))
    print("\nCrítico M1:", [r.atividade for r in m1.itertuples() if r.folga == 0])
    print(ev[["data_corte", "fase", "orcamento", "VP", "VA", "CR", "IDP", "IDC", "pct_previsto", "pct_fisico"]].round(3).to_string(index=False))

    # JSON para o sistema
    out = {"tabelas": {k: json.loads(v.to_json(orient="records", force_ascii=False)) for k, v in tab.items()},
           "linha_de_base": json.loads(base.to_json(orient="records", force_ascii=False)),
           "du2data": {int(k): v for k, v in du2data.items()}, "fim_du": int(fim)}
    (RAIZ / "app" / "data").mkdir(parents=True, exist_ok=True)
    (RAIZ / "app" / "data" / "g3.json").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
