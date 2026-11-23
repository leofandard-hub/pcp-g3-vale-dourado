"""Estilo comum das planilhas D1–D10: capa, cabeçalho, fontes. Fórmulas simples (SOMA, SE, MÁXIMO, PROCV, SOMASE)."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ARIAL = "Arial"
VERDE = "1F4D3A"
F_N = Font(name=ARIAL, size=10)
F_B = Font(name=ARIAL, size=10, bold=True)
F_IN = Font(name=ARIAL, size=10, color="0000FF")        # dado de entrada (azul)
F_H = Font(name=ARIAL, size=10, bold=True, color="FFFFFF")
FILL_H = PatternFill("solid", fgColor=VERDE)
FILL_T = PatternFill("solid", fgColor="E6F1EC")
FILL_Y = PatternFill("solid", fgColor="FFF2CC")
THIN = Side(style="thin", color="BFBFBF")
BORDA = Border(top=THIN, bottom=THIN, left=THIN, right=THIN)
R = '#,##0.00'; R0 = '#,##0'; P = '0.0%'; D = 'DD/MM/YYYY'


RESPONSAVEL = {"D1": "Léo Fandard", "D2": "Léo Fandard", "D3": "Léo Fandard", "D4": "Léo Fandard", "D8": "Léo Fandard", "D12": "Léo Fandard",
               "D5": "Raphael", "D6": "Raphael", "D7": "Raphael", "D9": "Raphael", "D10": "Raphael", "D11": "Raphael"}


def novo(titulo, doc, premissas, fontes, responsavel=None):
    responsavel = responsavel or RESPONSAVEL.get(doc, "(preencher)")
    wb = Workbook()
    ws = wb.active; ws.title = "Capa"
    ws.column_dimensions["A"].width = 22; ws.column_dimensions["B"].width = 110
    ws["A1"] = f"{doc} · {titulo}"; ws["A1"].font = Font(name=ARIAL, size=14, bold=True, color=VERDE)
    ws["A2"] = "ENG037 · Trabalho Final · Grupo 3 · Vale Dourado Frutas (packing house de manga, Juazeiro) · data de status 13/11/2026"
    ws["A2"].font = Font(name=ARIAL, size=10, italic=True)
    linha = 4
    for rot, itens in [("Premissas", premissas), ("Fonte dos dados", fontes), ("Responsável", [responsavel]),
                       ("Legenda", ["Texto azul = dado de entrada (vem das tabelas ou é premissa); texto preto = fórmula.",
                                    "Fundo amarelo = premissa que o grupo pode alterar."])]:
        ws.cell(linha, 1, rot).font = F_B
        for it in itens:
            c = ws.cell(linha, 2, it); c.font = F_N; c.alignment = Alignment(wrap_text=True, vertical="top")
            linha += 1
        linha += 1
    return wb


def aba(wb, nome, larguras=None):
    ws = wb.create_sheet(nome)
    for i, w in enumerate(larguras or [], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    return ws


def titulo(ws, linha, texto):
    c = ws.cell(linha, 1, texto); c.font = Font(name=ARIAL, size=12, bold=True, color=VERDE)


def cab(ws, linha, nomes, col=1):
    for j, n in enumerate(nomes):
        c = ws.cell(linha, col + j, n); c.font = F_H; c.fill = FILL_H; c.border = BORDA
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
    ws.row_dimensions[linha].height = 32


def put(ws, linha, col, v, fmt=None, entrada=False, bold=False, fill=None):
    c = ws.cell(linha, col, v)
    c.font = F_B if bold else (F_IN if entrada and not (isinstance(v, str) and v.startswith("=")) else F_N)
    c.border = BORDA
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    return c


def linha(ws, r, valores, fmts=None, entrada_cols=(), bold=False, fill=None):
    for j, v in enumerate(valores, 1):
        put(ws, r, j, v, (fmts or {}).get(j), entrada=j in entrada_cols, bold=bold, fill=fill)


def nota(ws, r, texto, col=1):
    c = ws.cell(r, col, texto); c.font = Font(name=ARIAL, size=9, italic=True, color="555555")


def calendario(wb, cal):
    """Aba Calendario (dia útil do projeto → data) para PROCV."""
    ws = aba(wb, "Calendario", [12, 14, 10])
    cab(ws, 1, ["Dia útil", "Data", "Semana"])
    r = 2
    for c in cal.itertuples():
        if c.dia_util_projeto == c.dia_util_projeto:  # não NaN
            put(ws, r, 1, int(c.dia_util_projeto), entrada=True); put(ws, r, 2, c.data_dt, D, entrada=True); put(ws, r, 3, c.semana, entrada=True)
            r += 1
    return f"Calendario!$A$2:$C${r - 1}"
