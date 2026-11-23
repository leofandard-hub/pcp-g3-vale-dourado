// Gera um .docx acadêmico (ABNT, Times 12, 1,5, justificado) a partir de um JSON.
// Uso: node scripts/gerar_docx.js spec.json saida.docx
const fs = require('fs');
const path = require('path');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, ImageRun, BorderStyle,
  ShadingType, PageBreak, Footer, PageNumber, HeadingLevel, LevelFormat } = require('docx');

const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const F = 'Times New Roman';
const W = 9026; // largura útil A4 com margens de 2,5 cm (DXA)
const run = (t, o = {}) => new TextRun({ text: t, font: F, size: o.size || 24, bold: o.bold, italics: o.italics });
const par = (t, o = {}) => new Paragraph({
  alignment: o.align || AlignmentType.JUSTIFIED, spacing: { line: o.line || 360, before: o.before || 0, after: o.after ?? 120 },
  indent: o.indent === false ? undefined : { firstLine: o.first ?? 709 }, keepNext: o.keepNext,
  children: Array.isArray(t) ? t : [run(t, o)]
});
const center = (t, o = {}) => par(t, { ...o, align: AlignmentType.CENTER, first: 0 });
const borda = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
const B = { top: borda, bottom: borda, left: borda, right: borda };

let nTab = 0, nFig = 0;
const corpo = [];

// ---------- folha de rosto ----------
const r = spec.rosto;
corpo.push(center('UNIVERSIDADE FEDERAL DA BAHIA', { bold: true, after: 0 }));
corpo.push(center('ESCOLA POLITÉCNICA · ENGENHARIA DE PRODUÇÃO', { after: 0 }));
corpo.push(center('ENG037 · Planejamento e Controle da Produção · Trabalho Final 2026.2', { after: 1200 }));
corpo.push(center(r.grupo, { after: 1000 }));
corpo.push(center(r.titulo.toUpperCase(), { bold: true, size: 28, after: 120 }));
if (r.subtitulo) corpo.push(center(r.subtitulo, { after: 900 }));
const blocos = [['Premissas', r.premissas], ['Fonte dos dados', r.fontes], ['Responsável', [r.responsavel]]];
for (const [rot, itens] of blocos) {
  corpo.push(par(rot, { bold: true, first: 0, after: 60, size: 22, keepNext: true }));
  for (const it of itens) corpo.push(par(it, { first: 0, size: 22, line: 276, after: 60 }));
}
corpo.push(center(`Professor: Lucas Magalhães`, { before: 600, after: 0, size: 22 }));
corpo.push(center(`Salvador, ${r.data}`, { size: 22 }));
corpo.push(new Paragraph({ children: [new PageBreak()] }));

// ---------- conteúdo ----------
for (const b of spec.corpo) {
  if (b.h1) corpo.push(par(b.h1.toUpperCase(), { bold: true, first: 0, before: 240, after: 120, keepNext: true }));
  else if (b.h2) corpo.push(par(b.h2, { bold: true, first: 0, before: 180, after: 100, keepNext: true }));
  else if (b.p) corpo.push(par(b.p));
  else if (b.lista) b.lista.forEach((it, i) => corpo.push(par(`${b.numerada ? (i + 1) + '. ' : '– '}${it}`, { first: 0, indent: false })));
  else if (b.tabela) {
    const t = b.tabela; nTab++;
    corpo.push(center(`Tabela ${nTab} – ${t.titulo}`, { bold: true, size: 22, after: 60, keepNext: true, line: 276 }));
    const n = t.cab.length;
    const larg = t.larg ? t.larg.map(x => Math.round(x / t.larg.reduce((s, y) => s + y, 0) * W)) : Array(n).fill(Math.floor(W / n));
    larg[n - 1] += W - larg.reduce((s, x) => s + x, 0);
    const cel = (txt, j, head) => new TableCell({
      borders: B, width: { size: larg[j], type: WidthType.DXA }, margins: { top: 60, bottom: 60, left: 90, right: 90 },
      shading: head ? { fill: 'D9D9D9', type: ShadingType.CLEAR, color: 'auto' } : undefined,
      children: [new Paragraph({ alignment: head ? AlignmentType.CENTER : (j === 0 ? AlignmentType.LEFT : (t.alin?.[j] === 'L' ? AlignmentType.LEFT : AlignmentType.CENTER)),
        spacing: { line: 240, before: 0, after: 0 }, children: [run(String(txt ?? ''), { size: t.fonte || 20, bold: head })] })]
    });
    corpo.push(new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: larg,
      rows: [new TableRow({ tableHeader: true, cantSplit: true, children: t.cab.map((c, j) => cel(c, j, true)) }),
        ...t.linhas.map(l => new TableRow({ cantSplit: true, children: l.map((c, j) => cel(c, j, false)) }))] }));
    corpo.push(par(`Fonte: ${t.fonte_txt || 'elaborado pelo grupo a partir das tabelas do projeto.'}`, { size: 20, first: 0, after: 200, line: 240 }));
  } else if (b.figura) {
    const f = b.figura; nFig++;
    const img = fs.readFileSync(path.resolve(path.dirname(process.argv[2]), f.arquivo));
    const ratio = f.ratio || 0.62; const w = f.largura || 560;
    corpo.push(new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: 'png', data: img, transformation: { width: w, height: Math.round(w * ratio) } })] }));
    corpo.push(center(`Figura ${nFig} – ${f.titulo}`, { bold: true, size: 22, after: 0, line: 276 }));
    corpo.push(center(`Fonte: ${f.fonte || 'elaborado pelo grupo.'}`, { size: 20, after: 200, line: 240 }));
  } else if (b.quebra) corpo.push(new Paragraph({ children: [new PageBreak()] }));
}
if (spec.referencias) {
  corpo.push(par('REFERÊNCIAS', { bold: true, first: 0, before: 240, after: 120, keepNext: true }));
  for (const ref of spec.referencias) corpo.push(par(ref, { first: 0, align: AlignmentType.LEFT, line: 240, after: 160 }));
}

const doc = new Document({
  styles: { default: { document: { run: { font: F, size: 24 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1418, bottom: 1418, left: 1418, right: 1418 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 20 })] })] }) },
    children: corpo
  }]
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(process.argv[3], buf); console.log('ok', process.argv[3]); });
