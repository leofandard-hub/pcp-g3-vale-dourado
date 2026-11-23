"""Cenários da Parte 3 com custos (premissas explícitas). Gera docs/_cenarios.json."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import cenarios as S   # motor CPM com efetivo/defasagem alterados (imprime testes ao importar)
C, a, A = S.C, S.a, S.A
MULTA, GANHO, ADM_DU = 18300, 30900, 146000 / 21
ch = C.tab["05_funcoes_mao_de_obra"].set_index("funcao").custo_hora_rs
rec = C.tab["07_atividade_recursos"]
def custo_mo(i):  # custo de mão de obra orçado da atividade pela composição da equipe
    r = rec[(rec.id_atividade == i) & (rec.tipo_recurso == "MAO_DE_OBRA")].set_index("codigo_recurso").quantidade
    return a.quantidade_orcada[i] * a.rup_orcada_hh_un[i] * (r * ch[r.index]).sum() / r.sum()
PREM = {"adicional_noturno": 0.20, "perda_prod_noturna": 0.10, "iluminacao_apoio_noturno_por_frente": 20000,
        "supervisao_noturna_por_frente": 22500, "alisadoras_extra_A12": 2 * 210 * 20, "diligenciamento_F10": 60000, "ampliacao_vivencia_temporaria": 35000}
def turno2(i): return 0.5 * custo_mo(i) * (PREM["adicional_noturno"] + PREM["perda_prod_noturna"])

dep = C.tab["04_dependencias"]
def nivelar(fim, ES, EF, dur, limite=130):
    """Desloca atividades não iniciadas que têm folga (sem mudar o término) para reduzir o pico por turno."""
    vivo = [i for i in a.index if A.pct[i] < .999]
    d_ = {i: EF[i] - ES[i] + 1 for i in vivo}
    # volta: LS de cada atividade não concluída com término fixo
    LF = {}
    for i in sorted(vivo, key=lambda x: -EF[x]):
        lf = fim
        for r in dep[dep.id_atividade_predecessora == i].itertuples():
            j = r.id_atividade_sucessora
            if j not in LF: continue
            lf = min(lf, LF[j] - d_[j] - r.defasagem_du if r.tipo_dependencia == "TI" else LF[j] - d_[j] + 1 - r.defasagem_du + d_[i] - 1)
        LF[i] = lf
    es = dict(ES)
    def prof(e): 
        p = {}
        for i in vivo:
            for d in range(max(e[i], A.N + 1), e[i] + d_[i]): p[d] = p.get(d, 0) + C.efetivo.get(i, 0)
        return p
    def ok(i, s):
        for r in dep[dep.id_atividade_sucessora == i].itertuples():
            p = r.id_atividade_predecessora
            if s < (es[p] + (EF[p]-ES[p]+1 if p in d_ else 0) + r.defasagem_du if r.tipo_dependencia == "TI" else es[p] + r.defasagem_du) and p in d_: return False
        for r in dep[dep.id_atividade_predecessora == i].itertuples():
            j = r.id_atividade_sucessora
            if j in d_ and es[j] < (s + d_[i] + r.defasagem_du if r.tipo_dependencia == "TI" else s + r.defasagem_du): return False
        return True
    for _ in range(3):
        for i in sorted(vivo, key=lambda x: -es[x]):
            if A.pct[i] > 0 or LF[i] - d_[i] + 1 <= es[i]: continue
            best, bp = es[i], max(prof(es).values())
            for s in range(es[i], LF[i] - d_[i] + 2):
                if not ok(i, s): continue
                old = es[i]; es[i] = s; pk = max(prof(es).values()); es[i] = old
                if pk < bp: best, bp = s, pk
            es[i] = best
    return max(prof(es).values()), {i: (es[i], es[i] + d_[i] - 1) for i in vivo if es[i] != ES[i]}
cen = {}
for nome, f, l, extras in [
    ("1. Seguir como está", {}, {}, {}),
    ("2. Recuperar o prazo", {"A12": 2, "A26": 2}, {("A12", "A23"): 10},
     {"2º turno A12 (adic. noturno + perda)": turno2("A12"), "2º turno A26 (adic. noturno + perda)": turno2("A26"),
      "Iluminação e apoio noturno (2 frentes)": 2 * PREM["iluminacao_apoio_noturno_por_frente"], "Supervisão noturna (2 frentes)": 2 * PREM["supervisao_noturna_por_frente"],
      "2 alisadoras extras no piso (20 du)": PREM["alisadoras_extra_A12"], "Diligenciamento e frete expresso F10": PREM["diligenciamento_F10"]}),
    ("3. Replanejar (recuperação parcial)", {"A12": 2}, {("A12", "A23"): 10},
     {"2º turno A12 (adic. noturno + perda)": turno2("A12"), "Iluminação e apoio noturno (1 frente)": PREM["iluminacao_apoio_noturno_por_frente"],
      "Supervisão noturna (1 frente)": PREM["supervisao_noturna_por_frente"], "2 alisadoras extras no piso (20 du)": PREM["alisadoras_extra_A12"]})]:
    fim, ES, EF, dur, pico = S.prever(f, l)
    atraso_c = max(0, fim - 271); custo = sum(extras.values())
    cen[nome] = {"fim_du": int(fim), "fim": C.du2data[fim], "atraso_contrato_du": int(atraso_c), "custo_adicional": round(custo, 2), "itens": {k: round(v, 2) for k, v in extras.items()},
                 "multa": atraso_c * MULTA, "ganho_perdido_vs_contrato": (fim - 271) * GANHO, "adm_local_extra_vs_base": round((fim - 261) * ADM_DU, 2),
                 "pico_efetivo_simultaneo": int(max(sum(C.efetivo.get(i, 0) for i in a.index if A.pct[i] < .999 and ES[i] <= d <= EF[i]) for d in range(A.N + 1, fim + 1)))}
    pn, mov = nivelar(fim, ES, EF, dur); cen[nome]["pico_nivelado"] = int(pn); cen[nome]["deslocadas"] = {k: [int(v[0]), int(v[1])] for k, v in mov.items()}
    if pn > 130:
        cen[nome]["itens"]["Ampliação temporária da vivência (pico > 130)"] = PREM["ampliacao_vivencia_temporaria"]
        cen[nome]["custo_adicional"] = round(cen[nome]["custo_adicional"] + PREM["ampliacao_vivencia_temporaria"], 2)
    x = cen[nome]; x["impacto_total"] = round(x["custo_adicional"] + x["multa"] + x["ganho_perdido_vs_contrato"] + x["adm_local_extra_vs_base"], 2)
out = {"premissas": PREM, "cenarios": cen, "custo_mo": {i: round(custo_mo(i), 2) for i in ["A12", "A26"]}}
(C.RAIZ / "docs" / "_cenarios.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))
print(json.dumps(out, ensure_ascii=False, indent=1, default=float))
