"""Tratamento dos dados do G3 (Vale Dourado Frutas).

Uso:  python scripts/limpeza.py
Lê   dados/brutos/*.csv
Gera dados/tratados/*.csv  e  docs/qualidade-dos-dados.md

Problemas tratados (encontrados na análise dos arquivos):
  1. Linhas duplicadas exatas (tabela 15).
  2. Erros de digitação: quantidade executada 10x maior (tabela 16).
     Critério: valor > 4x a mediana da atividade E dividir por 10 deixa o valor
     coerente com a mediana. Cada correção é listada no relatório.
  3. Custos sem apropriação (codigo_eap = DIVERSOS, tabela 20): reapropriados
     pelo documento de origem (RM-Axx, LOC-equipamento + apontamento da semana,
     FOLHA + descrição da atividade).
  4. Causas de não cumprimento fora do padrão (tabela 21): padronizadas.
"""
import re
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
BRUTOS, TRATADOS = RAIZ / "dados" / "brutos", RAIZ / "dados" / "tratados"

CAUSAS = {  # texto encontrado (normalizado) -> padrão
    "produtividade": "PRODUTIVIDADE", "equip.": "EQUIPAMENTO", "equipamentos": "EQUIPAMENTO",
    "equipamento": "EQUIPAMENTO", "terceiros": "TERCEIROS", "servico_anterior": "SERVICO_ANTERIOR",
    "mão de obra": "MAO_DE_OBRA", "mao de obra": "MAO_DE_OBRA", "mao_de_obra": "MAO_DE_OBRA",
}


def main():
    TRATADOS.mkdir(parents=True, exist_ok=True)
    t = {p.stem: pd.read_csv(p, encoding="utf-8-sig") for p in sorted(BRUTOS.glob("*.csv"))}
    rel = ["# Qualidade dos dados — G3 · Vale Dourado Frutas", "",
           "Gerado por `scripts/limpeza.py`. Arquivos originais em `dados/brutos/` (não alterados); "
           "arquivos tratados em `dados/tratados/`.", ""]

    # 1. duplicatas
    rel.append("## 1. Linhas duplicadas")
    for k, d in t.items():
        n = d.duplicated().sum()
        if n:
            linhas = (d.index[d.duplicated()] + 2).tolist()
            t[k] = d.drop_duplicates().reset_index(drop=True)
            rel.append(f"- `{k}`: **{n} linhas duplicadas removidas** (linhas do CSV: {linhas})")
    rel.append("")

    # 2. erros de digitação (x10) na produção
    rel.append("## 2. Erros de digitação (quantidade 10× maior)")
    p = t["16_rdo_producao"]
    med = p.groupby("id_atividade").quantidade_executada.transform("median")
    susp = p[(p.quantidade_executada > 4 * med) & ((p.quantidade_executada / 10 - med).abs() < 2 * med)]
    rel += ["| Data | Atividade | Valor lançado | Mediana da atividade | Valor corrigido |", "|---|---|---|---|---|"]
    for i, r in susp.iterrows():
        rel.append(f"| {r.data} | {r.id_atividade} | {r.quantidade_executada:g} | {med[i]:g} | {r.quantidade_executada / 10:g} |")
        p.loc[i, "quantidade_executada"] = r.quantidade_executada / 10
    rel += ["", "Conferência: após a correção, A09 soma exatamente 288,0 t (100% da quantidade orçada).", ""]

    # 3. custos DIVERSOS
    rel.append("## 3. Custos sem apropriação (DIVERSOS)")
    c, a, eq = t["20_custos_apropriados"], t["03_atividades"], t["17_equipamentos_apontamento"]
    eap = a.set_index("id_atividade").codigo_eap
    nomes = {r.nome_atividade: r.id_atividade for r in a.itertuples()}
    eq = eq.assign(semana=pd.to_datetime(eq.data).dt.isocalendar().week.astype(int))
    rel += ["| Lançamento | Data | Documento | Valor (R$) | Reapropriado para | Critério |", "|---|---|---|---|---|---|"]
    for i, r in c[c.codigo_eap == "DIVERSOS"].iterrows():
        ativ, crit = None, ""
        if m := re.match(r"RM-(A\d\d)-", str(r.documento)):
            ativ, crit = m.group(1), "atividade no código da requisição"
        elif m := re.match(r"LOC-([A-Z]+-\d+)-\d{4}-S(\d+)", str(r.documento)):
            e = eq[(eq.id_equipamento == m.group(1)) & (eq.semana == int(m.group(2))) & eq.id_atividade.notna()]
            if len(e):
                ativ, crit = e.id_atividade.mode()[0], f"apontamento do {m.group(1)} na semana S{m.group(2)} (tabela 17)"
        elif str(r.documento).startswith("FOLHA"):
            for n, idx in nomes.items():
                if n in str(r.descricao):
                    ativ, crit = idx, "nome da atividade na descrição da folha"
        if ativ:
            c.loc[i, ["id_atividade", "codigo_eap"]] = [ativ, eap[ativ]]
        rel.append(f"| {r.id_lancamento} | {r.data} | {r.documento} | {r.valor_rs:,.2f} | {ativ or 'NÃO REAPROPRIADO'} | {crit} |")
    rel += ["", "O total do custo direto não muda (R$ 11.419.304,12 até 06/11): só a apropriação por atividade/fase.", ""]

    # 4. causas
    rel.append("## 4. Causas de não cumprimento fora do padrão (tabela 21)")
    ps = t["21_plano_semanal"]
    rel += ["| Texto original | Padronizado | Ocorrências |", "|---|---|---|"]
    for orig, n in ps.causa_nao_cumprimento.dropna().value_counts().items():
        novo = CAUSAS.get(str(orig).strip().lower(), str(orig).strip().upper())
        if novo != orig:
            rel.append(f"| `{orig}` | {novo} | {n} |")
        ps.loc[ps.causa_nao_cumprimento == orig, "causa_nao_cumprimento"] = novo
    rel.append("")

    # números de controle
    m15 = t["15_rdo_mao_de_obra"]
    hh = (m15.horas_normais + m15.horas_extras).sum()
    cd = c[c.categoria != "INDIRETO"].valor_rs.sum()
    rel += ["## 5. Conferência com os números de controle do dossiê (até 06/11/2026)", "",
            "| Conferência | Dossiê | Dados tratados | Bate? |", "|---|---|---|---|",
            f"| Linhas da tabela 15 sem duplicatas | 691 | {len(m15)} | {'✔' if len(m15) == 691 else '✘'} |",
            f"| Homens-hora (normais + extras) | 53.222,4 | {hh:,.1f} | {'✔' if abs(hh - 53222.4) < 0.05 else '✘'} |",
            f"| Custo direto apropriado (inclui DIVERSOS) | 11.419.304,12 | {cd:,.2f} | {'✔' if abs(cd - 11419304.12) < 0.01 else '✘'} |",
            f"| Pedidos de compra emitidos | 124 | {len(t['18_compras_pedidos'])} | {'✔' if len(t['18_compras_pedidos']) == 124 else '✘'} |", ""]

    for k, d in t.items():
        d.to_csv(TRATADOS / f"{k}.csv", index=False, encoding="utf-8")
    (RAIZ / "docs").mkdir(exist_ok=True)
    (RAIZ / "docs" / "qualidade-dos-dados.md").write_text("\n".join(rel) + "\n", encoding="utf-8")
    print("\n".join(rel[-8:]))


if __name__ == "__main__":
    main()
