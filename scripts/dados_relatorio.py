"""Junta os números do relatório gerencial em docs/_relatorio.json (cada número com tabela/filtro de origem)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import analise as A, calculos as C
import pandas as pd
D = C.RAIZ / "docs"
CE = json.loads((D / "_cenarios.json").read_text()); X = json.loads((D / "_d9_d10.json").read_text())
R = A.R; a = A.a
out = {"evm": R["evm"], "prazo": R["prazo"], "ppc": R["ppc"], "he": R["hora_extra"], "qual": R["qualidade"], "nat": R["custo_natureza"], "ind": R["indireto"],
       "cen": CE["cenarios"], "cap": X["cap"]}
# curva S mensal (VP base, VA e CR reais até 13/11)
cal = C.tab["11_calendario"]; meses = [m for m in sorted(cal.mes.unique()) if "2026-02" <= m <= "2027-03"]
mo, prod, cus = A.mo, A.prod, A.cus
pts = []
for m in meses:
    dd = "2026-11-13" if m == "2026-11" else min(cal[cal.mes == m].data.max(), "2027-03-31"); n = C.du_ate(dd)
    vp = sum(A.base.custo_orcado_rs[k] * min(1, max(0, (n - A.base.es_du[k] + 1) / A.base.duracao_du[k])) for k in A.base.index)
    if dd <= "2026-11-30":
    	dc = min(dd, "2026-11-13")
    	q = prod[prod.data <= dc].groupby("id_atividade").quantidade_executada.sum()
    	va = sum(C.orc[k] * min(1, q.get(k, 0) / a.quantidade_orcada[k]) for k in a.index)
    	cr = cus[(cus.data <= dc) & (cus.categoria != "INDIRETO")].valor_rs.sum()
    else: va = cr = None
    pts.append([m, round(vp / 1e6, 3), None if va is None else round(va / 1e6, 3), None if cr is None else round(cr / 1e6, 3)])
out["curvaS"] = pts
# atrasos A07–A15
out["atrasos"] = {i: {"base_fim": C.du2data[int(A.base.ef_du[i])], "real_fim": C.du2data.get(int(A.fimr[i])), "dias": int(A.fimr[i] - A.base.ef_du[i]) if A.pct[i] >= .999 else None,
                      "ini_atraso": int(A.ini[i] - A.base.es_du[i]), "pct": round(float(A.pct[i]), 3)} for i in ["A07", "A08", "A09", "A10", "A11", "A13", "A14", "A15"]}
# RUP e du perdidos
rup = pd.DataFrame(R["rup"]).set_index("id")
rup["du_perdidos"] = rup.hh_excedente / (rup.index.map(C.efetivo) * 8)
out["rup"] = rup[["orc", "real", "desvio", "hh_excedente", "du_perdidos", "enc"]].round(3).reset_index().to_dict("records")
# equipamentos
eq = pd.DataFrame(R["equipamentos"]).sort_values("custo_ocioso", ascending=False)
out["equip"] = eq[["id_equipamento", "util", "dias_zero", "custo_ocioso", "f", "cor"]].round(3).to_dict("records"); out["equip_ocioso_total"] = R["locacao_ociosa_total"]
out["forn"] = R["fornecedores"]; out["ped_atrasados"] = R["pedidos_atrasados"]; out["ped_tardios"] = R["pedidos_tardios"]
ps = A.pla.groupby("semana").ok.mean(); out["ppc_sem"] = [[k, round(v, 3)] for k, v in ps.items()]
out["restr_abertas"] = int((C.tab["22_restricoes"].status == "EM_ANDAMENTO").sum())
out["fase"] = R["evm_fase"]
(D / "_relatorio.json").write_text(json.dumps(out, ensure_ascii=False, default=float, indent=1).replace("NaN", "null"))
print(json.dumps({k: out[k] for k in ["atrasos", "rup"]}, ensure_ascii=False, default=float, indent=0)[:2500]); print(out["curvaS"])
