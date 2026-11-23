"""Cenários de decisão (Parte 3): mesma rede, mudando efetivo/defasagens das atividades que faltam."""
import math, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).parent))
import analise as A
C = A.C; a = A.a; base = A.base; N = A.N; pct = A.pct
dep0 = C.tab["04_dependencias"]
rec = C.tab["07_atividade_recursos"]; ch = C.tab["05_funcoes_mao_de_obra"].set_index("funcao").custo_hora_rs

def prever(fator_ef=None, lag=None):
    fator_ef = fator_ef or {}; lag = lag or {}
    dur = {}
    for i in a.index:
        f = fator_ef.get(i, 1)
        if a.tipo_duracao[i] == "FIXA": dur[i] = base.duracao_du[i]
        else: dur[i] = math.ceil(a.quantidade_orcada[i] * a.rup_orcada_hh_un[i] / (C.efetivo[i] * f * 8) - 1e-9)
    ES, EF = {}, {}
    preds = {i: [(r.id_atividade_predecessora, r.tipo_dependencia, lag.get((r.id_atividade_predecessora, i), int(r.defasagem_du)))
                 for r in dep0[dep0.id_atividade_sucessora == i].itertuples()] for i in a.index}
    pend = set(a.index)
    while pend:
        for i in sorted(pend):
            if not all(p in EF for p, _, _ in preds[i]): continue
            if pct[i] >= 0.999: ES[i], EF[i] = int(A.ini.get(i, base.es_du[i])), int(A.fimr.get(i, base.ef_du[i]))
            elif pct[i] > 0: ES[i], EF[i] = int(A.ini[i]), N + A.rest[i]
            else:
                es = N + 1
                for p, tp, l in preds[i]: es = max(es, EF[p] + 1 + l if tp == "TI" else ES[p] + l)
                ES[i], EF[i] = es, es + dur[i] - 1
            pend.discard(i)
    # pico de efetivo diário
    pico = max(sum(C.efetivo.get(i, 0) * fator_ef.get(i, 1) for i in a.index if pct[i] < .999 and ES[i] <= d <= EF[i] and d > N) for d in range(N + 1, max(EF.values()) + 1))
    return max(EF.values()), ES, EF, dur, pico

base_fim, *_ , pico0 = prever()
print("seguir:", base_fim, "pico", pico0)
for nome, f, l in [
  ("A26 x2", {"A26": 2}, {}),
  ("A26 x2 + A31 x2", {"A26": 2, "A31": 2}, {}),
  ("lag A12->A23 20->10", {}, {("A12", "A23"): 10}),
  ("lag10 + A26 x2 + A31 x2", {"A26": 2, "A31": 2}, {("A12", "A23"): 10}),
  ("lag10 + A26 x1.5", {"A26": 1.5}, {("A12", "A23"): 10}),
  ("lag10 + A26 x2", {"A26": 2}, {("A12", "A23"): 10}),
  ("lag5 + A26 x2 + A31 x2 + A38?", {"A26": 2, "A31": 2}, {("A12", "A23"): 5}),
  ("lag0 + A26 x2 + A31x2", {"A26": 2, "A31": 2}, {("A12", "A23"): 0}),
]:
    fim, ES, EF, dur, pico = prever(f, l)
    crit = sorted([i for i in a.index if pct[i] < .999 and EF[i] >= fim - 0], key=lambda i: ES[i])
    print(f"{nome:35s} fim {fim} ({C.du2data.get(fim)}) ganho {base_fim-fim} du · pico {pico:.0f} · A35 ES {ES['A35']} · preds A35: " +
          ", ".join(f"{p}:{EF[p]}" for p in ["A24","A26","A27","A28","A30","A31","A17","A21"]))
# composição das equipes
for i in ["A12", "A23", "A26", "A31"]:
    r = rec[(rec.id_atividade == i) & (rec.tipo_recurso == "MAO_DE_OBRA")]
    print(i, r[["codigo_recurso","quantidade"]].values.tolist(), "Hh", a.quantidade_orcada[i]*a.rup_orcada_hh_un[i],
          "custo/h equipe", (r.set_index("codigo_recurso").quantidade * ch).sum(), "regime", a.regime_execucao[i])

print("----")
for nome, f, l in [
  ("A12x2 + A26x2 + lag10", {"A12": 2, "A26": 2}, {("A12", "A23"): 10}),
  ("A12x1.5 + A26x2 + lag10", {"A12": 1.5, "A26": 2}, {("A12", "A23"): 10}),
  ("A12x2 + A26x2 + A31x1.5 + lag10", {"A12": 2, "A26": 2, "A31": 1.5}, {("A12", "A23"): 10}),
  ("A12x1.5 + lag10 (replanejar)", {"A12": 1.5}, {("A12", "A23"): 10}),
  ("A12x2 + lag10", {"A12": 2}, {("A12", "A23"): 10}),
]:
    fim, ES, EF, dur, pico = prever(f, l)
    print(f"{nome:35s} fim {fim} ({C.du2data.get(fim)}) ganho {base_fim-fim} du · pico {pico:.0f} · " +
          ", ".join(f"{p}:{ES[p]}-{EF[p]}" for p in ["A12","A23","A26","A28","A29","A30","A31","A35","A38"]))
