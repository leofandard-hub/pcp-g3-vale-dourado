// Ficha do grupo (1 página, para preencher). Uso: node scripts/ficha_grupo.js
const fs = require('fs'); const path = require('path');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, BorderStyle, ShadingType } = require('docx');
const F = 'Times New Roman'; const W = 9026;
const b = { style: BorderStyle.SINGLE, size: 4, color: '000000' }; const B = { top: b, bottom: b, left: b, right: b };
const larg = [1900, 1100, 2000, 2226, 1800];
const cel = (t, j, h) => new TableCell({ borders: B, width: { size: larg[j], type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 90, right: 90 },
  shading: h ? { fill: 'D9D9D9', type: ShadingType.CLEAR, color: 'auto' } : undefined,
  children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: t, font: F, size: 20, bold: h })] })] });
const p = (t, o = {}) => new Paragraph({ alignment: o.c ? AlignmentType.CENTER : AlignmentType.JUSTIFIED, spacing: { after: 120, line: 300 }, children: [new TextRun({ text: t, font: F, size: o.s || 24, bold: o.b })] });
const cab = ['Integrante', 'Folha manuscrita', 'Documentos (D1–D12)', 'Sistema (telas, cálculos, 3D) e commits', 'Apresentação e lançamentos'];
const doc = new Document({ sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1418, bottom: 1418, left: 1418, right: 1418 } } }, children: [
  p('UNIVERSIDADE FEDERAL DA BAHIA · ENG037 · TRABALHO FINAL 2026.2', { c: true, b: true }),
  p('FICHA DO GRUPO 3 · VALE DOURADO FRUTAS: QUEM FEZ O QUÊ', { c: true, b: true, s: 26 }),
  p('Preencher uma linha por integrante. Cada integrante assina pelo menos uma folha do caderno (M1 a M6) e a semana de campo deve ter sido lançada por pelo menos três integrantes diferentes.'),
  new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: larg, rows: [new TableRow({ children: cab.map((c, j) => cel(c, j, true)) }),
    ...[['Léo Fandard', 'M1, M2, M4', 'D1, D2, D3, D4, D8, D12; relatório gerencial', 'Sistema (importação, dashboard, cálculos), scripts de tratamento e CPM; commits: ____', 'Semana de campo 09–11/11 e plano semanal; prazo, custo e decisão na apresentação'],
     ['Raphael', 'M3, M5, M6', 'D5, D6, D7, D9, D10, D11', 'Modelo 3D, telas de lançamento, banco Supabase; commits: ____', 'Semana de campo 12–13/11, suprimentos, FVS, restrições, custos; operação e achados na apresentação']]
     .map(l => new TableRow({ height: { value: 1300, rule: 'atLeast' }, children: l.map((t, j) => cel(t, j, false)) }))] }),
  p(''), p('Grupo de 2 integrantes: a semana de campo foi dividida entre os dois, cada um com o seu nome nos lançamentos do sistema.'),
  p('Link do sistema: ______________________________   Repositório: ______________________________'),
  p('Salvador, ____ de novembro de 2026.', { c: true }) ] }] });
Packer.toBuffer(doc).then(x => { fs.writeFileSync(path.join(__dirname, '../docs/ficha_do_grupo.docx'), x); console.log('ok ficha'); });
