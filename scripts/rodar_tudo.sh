#!/bin/bash
# Regenera dados tratados, cálculos, documentos e relatório na ordem certa.
set -e
cd "$(dirname "$0")/.."
python3 scripts/limpeza.py
python3 scripts/calculos.py > /dev/null          # D2 csv, valor agregado, app/data/g3.json
python3 scripts/analise.py > /dev/null           # diagnóstico 13/11
python3 scripts/docs_planilhas.py                # D1–D8
python3 scripts/docs_d9_d10.py > /dev/null       # D9, D10 + figuras
python3 scripts/cenarios_custos.py > /dev/null   # cenários da Parte 3
python3 scripts/docs_pdfs.py                     # PDFs D9–D12
python3 scripts/dados_relatorio.py > /dev/null
python3 scripts/contexto_copiloto.py           # números que o copiloto de IA pode citar
node scripts/relatorio_gerencial.js              # relatório gerencial (pptx)
node scripts/ficha_grupo.js
python3 scripts/guias.py > /dev/null            # kit da semana de campo + guia do caderno
(cd docs && soffice --headless --convert-to ods D3_Gantt.xlsx > /dev/null && soffice --headless --convert-to ods D2_rede_caminho_critico.xlsx > /dev/null && soffice --headless --convert-to pdf relatorio_gerencial.pptx > /dev/null)
echo "Pronto. Abra as planilhas no LibreOffice/Excel para recalcular as fórmulas."
