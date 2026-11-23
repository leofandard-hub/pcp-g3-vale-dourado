"""Diagnóstico na data de status (13/11/2026) = histórico tratado + semana de campo.
Uso: python scripts/analise.py  → imprime os números e grava docs/analise_13-11.json
"""
import json, math, sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import calculos as C
import semana_campo as S

RAIZ = C.RAIZ
STATUS = "2026-11-13"
t = C.tab
a, base = C.a, C.base.set_index("id_atividade")
N = C.du_ate(STATUS)  # 184

mo = pd.concat([t["15_rdo_mao_de_obra"], S.mao_de_obra], ignore_index=True)
prod = pd.concat([t["16_rdo_producao"], S.producao], ignore_index=True)
cus = pd.concat([t["20_custos_apropriados"], S.custos], ignore_index=True)
eqp = pd.concat([t["17_equipamentos_apontamento"], S.equipamentos], ignore_index=True)
pla = pd.concat([t["21_plano_semanal"], S.plano], ignore_index=True)
for d in (mo, prod, cus, eqp):
    d["du"] = d.data.map(C.data2du)

R = {}
R["controle_13_11"] = {"hh": round((mo.horas_normais + mo.horas_extras).sum(), 1),
                       "custo_direto": round(cus[cus.categoria != "INDIRETO"].valor_rs.sum(), 2)}

# ---------- valor agregado em 13/11 ----------
q = prod.groupby("id_atividade").quantidade_executada.sum()
pct = (q / a.quantidade_orcada).clip(upper=1).reindex(a.index).fillna(0)
ini = prod.groupby("id_atividade").du.min(); fimr = prod.groupby("id_atividade").du.max()
cr_at = cus[cus.categoria != "INDIRETO"].groupby("id_atividade").valor_rs.sum()
ev = pd.DataFrame({"fase": a.fase, "O": base.custo_orcado_rs,
                   "pplan": [min(1, max(0, (N - base.es_du[i] + 1) / base.duracao_du[i])) for i in a.index], "preal": pct})
ev["VP"], ev["VA"], ev["CR"] = ev.O * ev.pplan, ev.O * ev.preal, cr_at.reindex(a.index).fillna(0)
tot = ev[["O", "VP", "VA", "CR"]].sum()
R["evm"] = {k: round(v, 2) for k, v in tot.items()} | {"IDP": tot.VA / tot.VP, "IDC": tot.VA / tot.CR, "EAC": tot.O / (tot.VA / tot.CR)}
ef = ev.groupby("fase", sort=False)[["O", "VP", "VA", "CR"]].sum()
ef["IDP"], ef["IDC"] = ef.VA / ef.VP, ef.VA / ef.CR
R["evm_fase"] = ef.round(3).reset_index().to_dict("records")

# custo por natureza: orçado do executado × real
orc = t["12_orcamento_linha_de_base"].set_index("id_atividade")
nat = {}
for cat, col in [("MAO_DE_OBRA", "custo_mao_de_obra_rs"), ("SUBCONTRATO", "custo_subcontrato_rs"),
                 ("MATERIAL", "custo_material_rs"), ("EQUIPAMENTO", "custo_equipamento_rs")]:
    va = (orc[col] * pct.reindex(orc.index).fillna(0)).sum()
    cr = cus[cus.categoria == cat].valor_rs.sum()
    nat[cat] = {"VA": round(va, 2), "CR": round(cr, 2), "desvio": round(cr - va, 2), "IDC": va / cr if cr else None}
R["custo_natureza"] = nat
R["indireto"] = {"real": round(cus[cus.categoria == "INDIRETO"].valor_rs.sum(), 2),
                 "orcado_ate_status": round(146000 * (pd.Timestamp(STATUS) - pd.Timestamp("2026-02-16")).days / 30.4375, 2)}

# ---------- previsão de término (se nada mudar) ----------
ef_mo = C.efetivo
hh_at = (mo.horas_normais + mo.horas_extras).groupby(mo.id_atividade).sum()
rup_real = (hh_at / q).dropna()
rest = {}
for i in a.index:
    p = pct[i]
    if p >= 0.999:
        continue
    if p > 0:  # em andamento: saldo com a produtividade real
        if a.tipo_duracao[i] == "FIXA":
            rest[i] = math.ceil((1 - p) * base.duracao_du[i])
        else:
            rr = rup_real.get(i, a.rup_orcada_hh_un[i])
            rest[i] = math.ceil((1 - p) * a.quantidade_orcada[i] * rr / (ef_mo[i] * 8))
ES, EF = {}, {}
dep = t["04_dependencias"]
preds = {i: [(r.id_atividade_predecessora, r.tipo_dependencia, int(r.defasagem_du)) for r in dep[dep.id_atividade_sucessora == i].itertuples()] for i in a.index}
pend = set(a.index)
while pend:
    for i in sorted(pend):
        if not all(p in EF for p, _, _ in preds[i]):
            continue
        if pct[i] >= 0.999:
            ES[i], EF[i] = int(ini.get(i, base.es_du[i])), int(fimr.get(i, base.ef_du[i]))
        elif pct[i] > 0:
            ES[i], EF[i] = int(ini[i]), N + rest[i]
        else:
            es = N + 1
            for p, tp, lag in preds[i]:
                es = max(es, EF[p] + 1 + lag if tp == "TI" else ES[p] + lag)
            ES[i], EF[i] = es, es + base.duracao_du[i] - 1
        pend.discard(i)
fim_prev = max(EF.values())
cal_ext = {du: d for du, d in C.du2data.items()}
R["prazo"] = {"fim_linha_base_du": int(C.fim), "fim_linha_base": C.du2data[C.fim], "fim_previsto_du": fim_prev,
              "fim_previsto": cal_ext.get(fim_prev), "contrato_du": 271, "atraso_vs_base_du": fim_prev - C.fim,
              "atraso_vs_contrato_du": fim_prev - 271, "multa_rs": max(0, fim_prev - 271) * 18300,
              "ganho_perdido_rs": (fim_prev - C.fim) * 30900}
# caminho crítico previsto (backward simples nas não concluídas)
prev = pd.DataFrame({"ES": ES, "EF": EF}).assign(pct=pct, rest=pd.Series(rest))
R["previsao_atividades"] = prev.reset_index(names="id").to_dict("records")

# ---------- PPC ----------
pla["ok"] = (pla.quantidade_realizada / pla.meta_quantidade >= 0.97)
ppc_s = pla.groupby("semana").ok.mean()
R["ppc"] = {"geral": pla.ok.mean(), "ultimas4": ppc_s.tail(4).round(3).to_dict(), "media_ult8": ppc_s.tail(8).mean(),
            "media_prim8": ppc_s.head(8).mean(), "S46": ppc_s["2026-S46"],
            "causas": pla[~pla.ok].causa_nao_cumprimento.value_counts().to_dict(),
            "por_encarregado": pla.groupby("encarregado").ok.mean().round(3).to_dict()}

# ---------- produtividade ----------
rup = pd.DataFrame({"orc": a.rup_orcada_hh_un, "real": rup_real, "hh": hh_at, "q": q, "enc": a.encarregado}).dropna(subset=["orc", "real"])
rup["desvio"] = rup.real / rup.orc - 1
custo_h = t["05_funcoes_mao_de_obra"].set_index("funcao").custo_hora_rs
mo["custo"] = mo.funcao.map(custo_h) * (mo.horas_normais + mo.horas_extras * 1.6)
rup["hh_excedente"] = rup.hh - rup.q * rup.orc
R["rup"] = rup.round(3).reset_index(names="id").to_dict("records")
# hora extra × produtividade (dias com e sem HE)
dia = mo.groupby(["data", "id_atividade"]).agg(hh=("horas_normais", "sum"), he=("horas_extras", "sum")).reset_index()
dia = dia.merge(prod.groupby(["data", "id_atividade"]).quantidade_executada.sum().reset_index(), on=["data", "id_atividade"])
dia = dia[dia.id_atividade.isin(rup.index)]
dia["rup"] = (dia.hh + dia.he) / dia.quantidade_executada
dia["rel"] = dia.rup / dia.id_atividade.map(a.rup_orcada_hh_un)
R["hora_extra"] = {"rup_rel_com_HE": dia[dia.he > 0].rel.median(), "rup_rel_sem_HE": dia[dia.he == 0].rel.median(),
                   "hh_extras_total": mo.horas_extras.sum(), "custo_adicional_HE": (mo.funcao.map(custo_h) * mo.horas_extras * 0.6).sum()}
pr = prod.copy()
R["perdas_hh"] = {"chuva": pr.horas_perdidas_chuva.sum(), "equipamento": pr.horas_perdidas_equipamento.sum(),
                  "material": pr.horas_paradas_material.sum(), "retrabalho": pr.hh_retrabalho.sum()}

# ---------- retrabalho / qualidade ----------
fvs = t["23_inspecoes_qualidade"]
R["qualidade"] = {"fvs": len(fvs) + 3, "reprovadas": int((fvs.resultado == "REPROVADO").sum()),
                  "hh_retrab_fvs": fvs.hh_retrabalho_estimado.sum(), "hh_retrab_rdo": pr.hh_retrabalho.sum(),
                  "por_atividade": fvs[fvs.resultado == "REPROVADO"].groupby("id_atividade").hh_retrabalho_estimado.sum().to_dict(),
                  "por_encarregado": fvs.groupby("encarregado").apply(lambda g: (g.resultado == "REPROVADO").mean(), include_groups=False).round(3).to_dict()}
R["qualidade"]["custo_retrab_rs"] = R["qualidade"]["hh_retrab_rdo"] * (mo.custo.sum() / (mo.horas_normais + mo.horas_extras).sum())

# ---------- suprimentos ----------
ped = t["18_compras_pedidos"].copy()
ent = ped.data_entrega.notna()
ped["atraso_du"] = [C.data2du.get(e, 0) - C.data2du.get(p, 0) if isinstance(e, str) else None for e, p in zip(ped.data_entrega, ped.data_prometida)]
ped["atrasado_hoje"] = (~ent) & (ped.data_prometida < STATUS)
ped["custo"] = ped.quantidade_pedida * ped.preco_unitario_rs + ped.frete_rs
f = ped.groupby("id_fornecedor").agg(n=("id_pedido", "count"), atraso_medio=("atraso_du", "mean"), atrasados_hoje=("atrasado_hoje", "sum"),
                                       valor=("custo", "sum"), expresso=("frete_expresso", "sum"), rejeitado=("quantidade_rejeitada_fvm", "sum"))
R["fornecedores"] = f.round(2).reset_index().to_dict("records")
R["pedidos_atrasados"] = ped[ped.atrasado_hoje][["id_pedido", "id_material", "id_atividade", "id_fornecedor", "data_prometida", "data_necessidade_obra"]].to_dict("records")
R["frete_expresso_rs"] = ped[ped.frete_expresso == 1].frete_rs.sum()
R["emergencial_reposicao"] = ped.tipo_pedido.value_counts().to_dict()
# pedido depois do necessário (lead time não respeitado)
mat = t["08_materiais"].set_index("id_material")
ped["folga_pedido_du"] = [C.data2du.get(n, 0) - C.data2du.get(p, 0) - mat.lead_time_du.get(m, 0) for n, p, m in zip(ped.data_necessidade_obra, ped.data_pedido, ped.id_material)]
R["pedidos_tardios"] = int((ped.folga_pedido_du < 0).sum())

# ---------- equipamentos ----------
eq = t["06_equipamentos"].set_index("id_equipamento")
g = eqp.groupby("id_equipamento").agg(dias=("data", "count"), op=("horas_operando", "sum"), oc=("horas_ociosas", "sum"),
                                      disp=("horas_disponiveis", "sum"), cor=("horas_manutencao_corretiva", "sum"), f=("numero_falhas", "sum"))
g["util"] = g.op / g.disp
g["dias_zero"] = eqp[eqp.horas_operando == 0].groupby("id_equipamento").size().reindex(g.index).fillna(0)
g["custo_locacao"] = g.dias * eq.diaria_contratada_rs.reindex(g.index)
g["custo_ocioso"] = g.oc / 8 * eq.diaria_contratada_rs.reindex(g.index)
R["equipamentos"] = g.round(3).reset_index().to_dict("records")
R["locacao_ociosa_total"] = g.custo_ocioso.sum()
R["diaria_contratada_acima"] = ((eq.diaria_contratada_rs - eq.diaria_orcada_rs) / eq.diaria_orcada_rs).round(3).to_dict()

# ---------- segurança ----------
R["seguranca"] = t["24_ocorrencias_seguranca"].to_dict("records")

if __name__ == "__main__":
    out = RAIZ / "docs" / "analise_13-11.json"
    out.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    import pprint
    for k in ["controle_13_11", "evm", "custo_natureza", "indireto", "prazo", "ppc", "hora_extra", "perdas_hh", "qualidade",
              "frete_expresso_rs", "emergencial_reposicao", "pedidos_tardios", "locacao_ociosa_total"]:
        print(k, "=>", R[k])
    print(pd.DataFrame(R["evm_fase"]).to_string())
    print(rup[["orc", "real", "desvio", "hh_excedente", "enc"]].sort_values("desvio").to_string())
    print(f.to_string())
    print(g.sort_values("custo_ocioso", ascending=False).head(8).to_string())
    print(prev[prev.pct < 1].sort_values("ES").to_string())
