"""Gera app/data/copiloto.json: os números do relatório gerencial (data de status 13/11/2026)
que o copiloto de IA pode citar. A IA não calcula nada: só lê estes números e os do sistema."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
rel = json.loads((RAIZ / "docs/_relatorio.json").read_text(encoding="utf-8"))
cen = json.loads((RAIZ / "docs/_cenarios.json").read_text(encoding="utf-8"))

saida = {
    "data_status": "2026-11-13",
    "legenda": {
        "evm": "valor agregado acumulado (R$): O = orçamento total (BAC), VP, VA, CR, IDP, IDC, EAC",
        "prazo": "datas e dias úteis (du): linha de base, previsão sem ação, contrato, multa e ganho perdido",
        "ppc": "PPC geral, últimas semanas e causas de não cumprimento (contagem)",
        "he": "efeito das horas extras na RUP e custo adicional",
        "qual": "FVS: inspeções, reprovações e retrabalho (Hh e R$)",
        "cap": "capacidade da nova unidade por posto (caixas/dia), OEE e máquinas necessárias",
        "rup": "RUP real × orçada por atividade (desvio em fração)",
        "equip": "equipamentos: utilização, dias parados e custo ocioso (R$)",
        "forn": "fornecedores: atraso médio (dias), pedidos atrasados hoje, valor (R$)",
        "atrasos": "atividades atrasadas: fim da linha de base × fim real ou previsto",
        "cenarios": "3 cenários de decisão com fim previsto, custo adicional, multa e impacto total (R$)",
    },
    **{k: v for k, v in rel.items() if k not in ("curvaS", "cen")},
    "cenarios": cen["cenarios"],
    "premissas_cenarios": cen.get("premissas", {}),
}
destino = RAIZ / "app/data/copiloto.json"
destino.write_text(json.dumps(saida, ensure_ascii=False, separators=(",", ":")).replace("NaN", "null"), encoding="utf-8")
print(f"{destino.relative_to(RAIZ)}: {destino.stat().st_size / 1024:.1f} kB")
