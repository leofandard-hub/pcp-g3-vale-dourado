// Relatório gerencial (≤ 15 slides). Uso: node scripts/relatorio_gerencial.js
const path = require('path');
const fs = require('fs');
const pptxgen = require('pptxgenjs');
const { applyTheme } = require('/root/.claude/skills/synced/10559047-4394-4465-8af6-8e7b895dbe14_133e69e1-8d67-40df-b6b4-69ff0233ba50/pptx/scripts/apply_theme.js');

const ROOT = path.resolve(__dirname, '..');
const J = JSON.parse(fs.readFileSync(path.join(ROOT, 'docs/_relatorio.json'), 'utf8'));
const OUT = path.join(ROOT, 'docs/relatorio_gerencial.pptx');

const THEME = { name: 'Vale Dourado', headFontFace: 'Cambria', bodyFontFace: 'Calibri',
  colors: { dk1: '1B2A22', lt1: 'FFFFFF', dk2: '1F4D3A', lt2: 'EEF3EF', accent1: 'F2A541', accent2: '1F4D3A', accent3: 'C0392B', accent4: '6B7385', accent5: '2E9E5B', accent6: '3B6EA5', hlink: '3B6EA5', folHlink: '6B7385' } };
const HX = THEME.colors;
const br = (v, d = 0) => Number(v).toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d });
const mi = v => 'R$ ' + br(v / 1e6, 2) + ' mi';
const mil = v => 'R$ ' + br(v / 1e3, 0) + ' mil';
const dt = s => s.split('-').reverse().join('/');

const pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = 'Comitê de PCP · Vale Dourado Frutas'; pres.author = 'Grupo 3';
const C = pres.SchemeColor;

pres.defineSlideMaster({ title: 'CAPA', background: { color: HX.dk2 },
  placeholders: [], objects: [] });
pres.defineSlideMaster({ title: 'CONTEUDO', background: { color: 'FFFFFF' },
  objects: [{ placeholder: { options: { name: 'title', type: 'title', x: 0.45, y: 0.22, w: 9.1, h: 0.75, fontFace: THEME.headFontFace, fontSize: 22, bold: true, color: C.text2, valign: 'top', align: 'left', margin: 0 }, text: '' } },
    { text: { text: 'ENG037 · Comitê de PCP · G3 Vale Dourado Frutas · status 13/11/2026', options: { x: 0.45, y: 5.3, w: 6, h: 0.25, fontSize: 9, color: C.accent4, margin: 0 } } }],
  slideNumber: { x: 9.2, y: 5.3, w: 0.4, h: 0.25, fontSize: 9, color: HX.accent4 } });

const fonte = (s, t) => s.addText('Fonte: ' + t, { x: 0.45, y: 5.02, w: 9.1, h: 0.25, fontSize: 10, italic: true, color: C.accent4, margin: 0, isTextBox: true });
const card = (s, x, y, w, h, rot, txt, cor) => {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: cor || C.background2 }, line: { type: 'none' }, rectRadius: 0.08, objectName: 'card ' + rot });
  s.addText([{ text: rot, options: { bold: true, color: C.text2, fontSize: 12, breakLine: true } }, { text: txt, options: { color: C.text1, fontSize: 12 } }],
    { x: x + 0.1, y: y + 0.05, w: w - 0.2, h: h - 0.1, valign: 'top', margin: 2, isTextBox: true, paraSpaceAfter: 2 });
};
const achado = (s, itens) => { // 4 cartões à direita, altura proporcional ao texto
  const linhas = itens.map(i => 1 + Math.ceil(i[1].length / 50));
  const tot = linhas.reduce((a, b) => a + b, 0), disp = 3.88 - 0.08 * (itens.length - 1);
  let y = 1.05; const hs = linhas.map(l => disp * l / tot);
  itens.forEach(([r, t], k) => { card(s, 5.6, y, 3.95, hs[k], r, t); y += hs[k] + 0.08; });
};
const chartBase = { catAxisLabelFontFace: '+mn-lt', valAxisLabelFontFace: '+mn-lt', dataLabelFontFace: '+mn-lt', catAxisLabelFontSize: 10, valAxisLabelFontSize: 10, dataLabelFontSize: 10,
  catAxisLabelColor: HX.dk1, valAxisLabelColor: HX.accent4, valGridLine: { color: 'E3E6EA', size: 0.5 }, catGridLine: { style: 'none' }, legendFontSize: 10, legendFontFace: '+mn-lt' };
const stat = (s, x, y, w, num, lab, cor) => {
  s.addText(num, { x, y, w, h: 0.6, fontFace: THEME.headFontFace, fontSize: 26, bold: true, color: cor || C.text2, margin: 0, isTextBox: true });
  s.addText(lab, { x, y: y + 0.6, w, h: 0.45, fontSize: 12, color: C.text1, margin: 0, valign: 'top', isTextBox: true });
};

const FASES = ['1.1 Projetos', '1.2 Canteiro', '1.3 Estrutura', '1.4 Instalações', '1.5 Equip. processo', '1.6 Sistemas', '1.7 Comission.'];
const E = J.evm, P = J.prazo, CE = J.cen, c1 = CE['1. Seguir como está'], c2 = CE['2. Recuperar o prazo'], c3 = CE['3. Replanejar (recuperação parcial)'];

// 1 · capa
pres.addSection({ title: 'Conclusão' });
let s = pres.addSlide({ masterName: 'CAPA', sectionTitle: 'Conclusão' });
s.addText('Comitê de PCP', { x: 0.6, y: 0.6, w: 8.8, h: 0.4, fontSize: 16, color: C.accent1, bold: true, margin: 0, isTextBox: true });
s.addText('Packing house de manga sai em 07/05/2027 se nada mudar. Recomendamos recuperar o prazo.', { x: 0.6, y: 1.1, w: 8.6, h: 1.6, fontFace: THEME.headFontFace, fontSize: 30, bold: true, color: C.background1, margin: 0, valign: 'top', isTextBox: true });
s.addText('Vale Dourado Frutas · Juazeiro (BA) · data de status 13/11/2026', { x: 0.6, y: 3.3, w: 8.6, h: 0.35, fontSize: 14, color: 'CFE0D6', margin: 0, isTextBox: true });
s.addText('ENG037 · Planejamento e Controle da Produção · UFBA · Grupo 3: Léo Fandard e Raphael · Prof. Lucas Magalhães', { x: 0.6, y: 4.7, w: 8.6, h: 0.3, fontSize: 12, color: 'CFE0D6', margin: 0, isTextBox: true });

// 2 · conclusão
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Conclusão' });
s.addText('Recuperar o prazo custa R$ 266 mil e evita R$ 1,55 mi de multa e perda', { placeholder: 'title' });
stat(s, 0.45, 1.15, 2.9, dt(c1.fim), `término se nada mudar: ${c1.atraso_contrato_du} du após o contrato (23/03/2027)`, C.accent3);
stat(s, 3.55, 1.15, 2.9, dt(c2.fim), 'término com o cenário 2, 2 du antes do contrato', C.accent5);
stat(s, 6.65, 1.15, 2.9, mil(c2.custo_adicional), 'custo adicional do cenário 2 (2º turno, apoio, F10)', C.text2);
s.addText([
  { text: 'O que pedimos à diretoria', options: { bold: true, color: C.text2, breakLine: true } },
  { text: '2º turno no piso industrial (A12) e na tubulação frigorífica (A26), os dois gargalos do caminho crítico.', options: { bullet: true, breakLine: true } },
  { text: 'Concretar primeiro a área das câmaras para antecipar a montagem dos painéis (A23).', options: { bullet: true, breakLine: true } },
  { text: 'Diligenciamento semanal do fornecedor F10 (tanques, linha de seleção, portas, sensores).', options: { bullet: true, breakLine: true } },
  { text: 'Aprovar R$ 1,23 mi para 2 tanques hidrotérmicos e 1 paletizadora: sem isso a unidade não atende o pico.', options: { bullet: true } }],
  { x: 0.45, y: 2.45, w: 9.1, h: 2.4, fontSize: 14, color: C.text1, valign: 'top', margin: 0, paraSpaceAfter: 4, isTextBox: true });
fonte(s, 'scripts analise.py e cenarios_custos.py (tabelas 01, 03, 04, 07, 11, 15–21 + boletins 09–13/11).');

// 3 · diagnóstico
pres.addSection({ title: 'Diagnóstico' });
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Diagnóstico' });
s.addText('A obra fez 39% do que deveria ter feito 67%; o custo ainda está perto do orçado', { placeholder: 'title' });
const k = [[br(E.VA / E.O * 100, 1) + '%', 'avanço físico real\n(previsto ' + br(E.VP / E.O * 100, 1) + '%)', C.text2], [br(E.IDP, 2), 'IDP = VA ÷ VP\nprazo', C.accent3],
  [br(E.IDC, 2), 'IDC = VA ÷ CR\ncusto', C.accent1], [br(E.EAC / 1e6, 1) + ' mi', 'estimativa no término, R$\n(orçado ' + br(E.O / 1e6, 1) + ' mi)', C.accent3], [br(J.ppc.media_ult8 * 100, 0) + '%', 'PPC médio das\núltimas 8 semanas (meta 80%)', C.accent3]];
k.forEach(([n, l, c], i) => stat(s, 0.45 + i * 1.84, 1.1, 1.75, n, l, c));
s.addChart(pres.charts.BAR, J.fase.map(f => ({ name: f.fase, labels: [], values: [] })).length ? [
  { name: '% previsto', labels: FASES, values: J.fase.map(f => +(f.VP / f.O * 100).toFixed(1)) },
  { name: '% real', labels: FASES, values: J.fase.map(f => +(f.VA / f.O * 100).toFixed(1)) }] : [],
  { x: 0.45, y: 2.4, w: 9.1, h: 2.55, barDir: 'col', barGrouping: 'clustered', chartColors: [HX.accent4, HX.accent5], showLegend: true, legendPos: 't', showValue: true, dataLabelPosition: 'outEnd',
    dataLabelFormatCode: '0', valAxisMaxVal: 110, valAxisHidden: true, ...chartBase });
fonte(s, 'valor agregado em 13/11 (Anexo D): tabelas 12, 16 e 20 + boletins da semana de campo; PPC: tabela 21 + B10.');

// 4 · prazo
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Diagnóstico' });
s.addText('O caminho crítico perdeu 41 dias úteis: a estrutura atrasou e o piso ainda não começou', { placeholder: 'title' });
const at = J.atrasos;
s.addChart(pres.charts.BAR, [{ name: 'Atraso no início (du)', labels: ['A07 Terraplenagem', 'A08 Fundações', 'A09 Estrutura', 'A10 Cobertura', 'A11 Fechamento'], values: ['A07', 'A08', 'A09', 'A10', 'A11'].map(i => at[i].ini_atraso) },
  { name: 'Atraso no término (du)', labels: ['A07 Terraplenagem', 'A08 Fundações', 'A09 Estrutura', 'A10 Cobertura', 'A11 Fechamento'], values: ['A07', 'A08', 'A09', 'A10', 'A11'].map(i => at[i].dias ?? 0) }],
  { x: 0.45, y: 1.05, w: 5.0, h: 3.85, barDir: 'bar', chartColors: [HX.accent4, HX.accent3], showValue: true, dataLabelPosition: 'outEnd', showLegend: true, legendPos: 'b', valAxisHidden: true, catAxisOrientation: 'maxMin', ...chartBase });
achado(s, [['Hoje', `A12 (piso) com 0% contra 97,5% previsto. A10 a 97,6% e A11 a 83%. A09 terminou em 14/10, 26 du depois da linha de base.`, 1.1],
  ['Previsão se nada mudar', `Término em ${dt(P.fim_previsto)} (du ${P.fim_previsto_du}): +${P.atraso_vs_base_du} du sobre a linha de base e +${P.atraso_vs_contrato_du} du sobre o contrato.`, 1.0],
  ['Caminho crítico atual', 'A10 → A12 → A23 → A26 → A35 → A37 → A38', 0.75],
  ['Impacto', `Multa de ${mil(P.multa_rs)} + ${mil(P.atraso_vs_contrato_du * 30900)} de ganho operacional perdido.`, 0.8]]);
fonte(s, 'linha de base D2 (tabelas 03, 04, 07, 11); datas reais: tabela 16 (1º e último apontamento); previsão: scripts/analise.py.');

// 5 · custo
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Diagnóstico' });
s.addText('O IDC de 0,95 esconde equipamento e mão de obra muito acima e R$ 14 mi ainda por gastar', { placeholder: 'title' });
const cs = J.curvaS;
s.addChart(pres.charts.LINE, [{ name: 'VP', labels: cs.map(x => x[0] === '2026-11' ? '13/11' : x[0].slice(2)), values: cs.map(x => x[1]) },
  { name: 'VA', labels: cs.map(x => x[0]), values: cs.map(x => x[2]) }, { name: 'CR', labels: cs.map(x => x[0]), values: cs.map(x => x[3]) }],
  { x: 0.45, y: 1.05, w: 5.0, h: 3.85, chartColors: [HX.accent4, HX.accent5, HX.accent3], lineSize: 2, lineDataSymbol: 'circle', lineDataSymbolSize: 4, showLegend: true, legendPos: 'b',
    valAxisTitle: 'R$ mi', showValAxisTitle: true, valAxisTitleFontSize: 10, ...chartBase });
const N = J.nat;
achado(s, [['Por natureza (IDC)', `Equipamento ${br(N.EQUIPAMENTO.IDC, 2)} (+${mil(N.EQUIPAMENTO.desvio)}) · Mão de obra ${br(N.MAO_DE_OBRA.IDC, 2)} (+${mil(N.MAO_DE_OBRA.desvio)}) · Material ${br(N.MATERIAL.IDC, 2)} · Subcontrato ${br(N.SUBCONTRATO.IDC, 2)}`, 1.15],
  ['Por fase', 'Canteiro e infraestrutura com IDC 0,86 (+R$ 179 mil). Estrutura 0,95.', 0.8],
  ['O que o total esconde', 'Instalações e equipamentos de processo (R$ 14 mi) ainda não têm custo: o IDC só mede o que já foi feito.', 0.95],
  ['Estimativa no término', `${mi(E.EAC)}: +${mi(E.EAC - E.O)} (+${br((E.EAC / E.O - 1) * 100, 1)}%).`, 0.75]]);
fonte(s, 'tabela 20 (naturezas exceto INDIRETO, DIVERSOS reapropriados) + B9; VA por natureza: tabela 12 × avanço (tabela 16).');

// 6–12 · achados
pres.addSection({ title: 'Achados' });
const rupL = J.rup.filter(r => r.enc === 'Lúcia Farias');
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Achados' });
s.addText('Achado 1 · As empreitadas de estrutura, cobertura e fechamento rendem até 81% abaixo do orçado', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: 'RUP real ÷ orçada', labels: J.rup.map(r => r.id + ' ' + r.enc.split(' ')[0]), values: J.rup.map(r => +(r.real / r.orc).toFixed(2)) }],
  { x: 0.45, y: 1.05, w: 5.0, h: 3.85, barDir: 'bar', chartColors: J.rup.map(r => r.desvio > 0.3 ? HX.accent3 : HX.accent5), showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00',
    showLegend: false, valAxisHidden: true, catAxisOrientation: 'maxMin', invertedColors: J.rup.map(r => r.desvio > 0.3 ? HX.accent3 : HX.accent5), ...chartBase });
achado(s, [['Evidência', `A09 ${br(J.rup.find(r => r.id === 'A09').real, 1)} Hh/t contra 35,2 orçados; A10 e A11 também +57% a +81%. ${br(rupL.reduce((a, r) => a + r.hh_excedente, 0))} Hh excedentes.`, 1.1],
  ['Causa provável', 'Equipe da empreiteira subdimensionada e parada por equipamento (8 das 22 causas de não cumprimento nas frentes de Lúcia Farias).', 1.0],
  ['Impacto', `${br(rupL.reduce((a, r) => a + r.du_perdidos, 0), 0)} du de equipe perdidos; a A09 sozinha atrasou 26 du no caminho crítico.`, 0.8],
  ['Ação e dono', 'Cláusula de produtividade e reforço contratual nas próximas empreitadas (A23). Dono: Suprimentos/Contratos.', 0.95]]);
fonte(s, 'RUP real = (Hh normais + extras) ÷ qtd executada: tabelas 15 e 16 + B2–B6; RUP orçada: tabela 03.');

s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Achados' });
s.addText('Achado 2 · A hora extra não acelera a obra: a produtividade cai 38% nos dias com hora extra', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: 'RUP real ÷ orçada (mediana)', labels: ['Dias sem hora extra', 'Dias com hora extra'], values: [+J.he.rup_rel_sem_HE.toFixed(2), +J.he.rup_rel_com_HE.toFixed(2)] }],
  { x: 0.45, y: 1.05, w: 5.0, h: 3.85, barDir: 'col', chartColors: [HX.accent5, HX.accent3], invertedColors: [HX.accent5, HX.accent3], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.00', showLegend: false, valAxisHidden: true, valAxisMinVal: 0, ...chartBase });
achado(s, [['Evidência', `${br(J.he.hh_extras_total)} Hh extras (13% do total). RUP mediana ${br(J.he.rup_rel_com_HE, 2)}× a orçada com hora extra e ${br(J.he.rup_rel_sem_HE, 2)}× sem.`, 1.0],
  ['Causa provável', 'Fadiga e jornadas de 10 h sem frente liberada: a hora extra foi usada para compensar paradas, não para produzir.', 1.0],
  ['Impacto', `${mil(J.he.custo_adicional_HE)} de adicional de 60% pagos sem ganho de prazo.`, 0.7],
  ['Ação e dono', 'Suspender hora extra como ferramenta de recuperação; usar 2º turno nas frentes críticas. Dono: Engenharia de produção + RH.', 1.05]]);
fonte(s, 'tabelas 15 (horas extras por dia e atividade), 16 (produção) e 05 (custo hora, adicional 60%).');

const eq = J.equip.slice(0, 6);
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Achados' });
s.addText(`Achado 3 · Pagamos ${mil(J.equip_ocioso_total)} de locação por equipamento parado`, { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: 'Locação em horas ociosas (R$ mil)', labels: eq.map(e => e.id_equipamento), values: eq.map(e => +(e.custo_ocioso / 1000).toFixed(1)) }],
  { x: 0.45, y: 1.05, w: 5.0, h: 3.85, barDir: 'bar', chartColors: [HX.accent1], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', showLegend: false, valAxisHidden: true, catAxisOrientation: 'maxMin', ...chartBase });
achado(s, [['Evidência', `Utilização média de 50% a 70%. MUN-01: 8 falhas e 18 dias sem operar. PTA-01 e PTA-02: 19 dias sem operar, 4 deles na semana de campo à espera de telha.`, 1.15],
  ['Causa provável', 'Equipamento mobilizado antes da frente liberada e mantido sem frente; diária paga por dia, não por hora.', 0.9],
  ['Impacto', `IDC de equipamento ${br(N.EQUIPAMENTO.IDC, 2)}: +${mil(N.EQUIPAMENTO.desvio)} sobre o orçado.`, 0.7],
  ['Ação e dono', 'Mobilizar só com frente liberada no lookahead; devolver PTAs ao fim da A10; trocar o MUN-01. Dono: Engenharia de equipamentos.', 1.05]]);
fonte(s, 'tabelas 17 (apontamento diário) e 06 (diária contratada) + B2–B6; custo ocioso = horas ociosas ÷ 8 × diária.');

const fr = J.forn.slice().sort((a, b) => b.atraso_medio - a.atraso_medio).slice(0, 6);
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Achados' });
s.addText('Achado 4 · O fornecedor dos equipamentos de processo atrasa 11 dias úteis em média', { placeholder: 'title' });
s.addChart(pres.charts.BAR, [{ name: 'Atraso médio de entrega (du)', labels: fr.map(f => f.id_fornecedor), values: fr.map(f => +(+f.atraso_medio).toFixed(1)) }],
  { x: 0.45, y: 1.05, w: 5.0, h: 3.85, barDir: 'bar', chartColors: [HX.accent3], showValue: true, dataLabelPosition: 'outEnd', dataLabelFormatCode: '0.0', showLegend: false, valAxisHidden: true, catAxisOrientation: 'maxMin', ...chartBase });
achado(s, [['Evidência', 'F10 (R$ 10,3 mi em pedidos): 5 pedidos vencidos em 13/11 (tanques, linha de seleção, portas, sensores). A telha da A10 (F05) chegou 16 dias após a necessidade.', 1.2],
  ['Causa provável', `${J.ped_tardios} pedidos emitidos depois do lead time; sem diligenciamento nem inspeção na fábrica.`, 0.85],
  ['Impacto', 'Cada du de atraso no caminho crítico custa R$ 49,2 mil (multa + ganho operacional). Tanques e linha de seleção viram críticos no cenário 2.', 1.0],
  ['Ação e dono', 'Diligenciamento semanal e inspeção em fábrica do F10; plano B para os tanques. Dono: Suprimentos (Carla Mota).', 0.85]]);
fonte(s, 'tabela 18 (data prometida × entrega, dias úteis da tabela 11) e tabela 08 (lead time); B7.');

const pp = J.ppc_sem.slice(-14);
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Achados' });
s.addText('Achado 5 · O planejamento semanal deixou de ser confiável: PPC caiu de 91% para 39%', { placeholder: 'title' });
s.addChart([{ type: pres.charts.BAR, data: [{ name: 'PPC', labels: pp.map(x => x[0].slice(5)), values: pp.map(x => +(x[1] * 100).toFixed(0)) }], options: { chartColors: [HX.accent2], barGapWidthPct: 60 } },
  { type: pres.charts.LINE, data: [{ name: 'Meta 80%', labels: pp.map(x => x[0].slice(5)), values: pp.map(() => 80) }], options: { chartColors: [HX.accent1], lineSize: 2, lineDataSymbol: 'none' } }],
  { x: 0.45, y: 1.05, w: 5.0, h: 3.85, showLegend: true, legendPos: 'b', valAxisMaxVal: 100, valAxisMinVal: 0, showValue: false, ...chartBase });
const cz = J.ppc.causas;
achado(s, [['Evidência', `PPC médio ${br(J.ppc.media_prim8 * 100, 0)}% nas 8 primeiras semanas e ${br(J.ppc.media_ult8 * 100, 0)}% nas 8 últimas. Causas: equipamento ${cz.EQUIPAMENTO}, serviço anterior ${cz.SERVICO_ANTERIOR}, produtividade ${cz.PRODUTIVIDADE}.`, 1.15],
  ['Causa provável', `Pacotes comprometidos com restrição pendente: ${J.restr_abertas} restrições abertas; A25 entrou no plano da S46 sem serviço anterior liberado.`, 1.0],
  ['Impacto', 'Na S46, 226 m² de cobertura (caminho crítico) ficaram por fazer: ≈ 1 du a mais na A10.', 0.75],
  ['Ação e dono', 'Lookahead de 6 semanas; só entra no plano o pacote sem restrição. Dono: Coordenação de PCP.', 0.8]]);
fonte(s, 'tabela 21 + B10 (concluído = realizado ≥ 97% da meta), causas padronizadas por scripts/limpeza.py; tabela 22 + B8.');

const q = J.qual;
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Achados' });
s.addText('Achado 6 · Uma em cada cinco inspeções reprova, com retrabalho concentrado nas fundações', { placeholder: 'title' });
const qa = Object.entries(q.por_atividade).sort((a, b) => b[1] - a[1]);
s.addChart(pres.charts.BAR, [{ name: 'Hh de retrabalho estimado', labels: qa.map(x => x[0]), values: qa.map(x => +x[1].toFixed(0)) }],
  { x: 0.45, y: 1.05, w: 5.0, h: 3.85, barDir: 'bar', chartColors: [HX.accent3], showValue: true, dataLabelPosition: 'outEnd', showLegend: false, valAxisHidden: true, catAxisOrientation: 'maxMin', ...chartBase });
achado(s, [['Evidência', `${q.reprovadas} de 55 FVS reprovadas no histórico (20%); ${br(q.hh_retrab_fvs)} Hh de retrabalho estimado. Reprovação de 24% nas frentes de Jair Bispo e Lúcia Farias.`, 1.15],
  ['Causa provável', 'Inspeção feita depois do serviço concluído; sem FVS por lote antes de liberar o serviço seguinte.', 0.9],
  ['Impacto', `${br(q.hh_retrab_rdo)} Hh de retrabalho apontados no RDO (≈ ${mil(q.custo_retrab_rs)}). Só nas fundações, 420 Hh = 1,7 du da equipe de 31 pessoas.`, 0.8],
  ['Ação e dono', 'FVS por lote no piso (A12) e na tubulação (A26), com liberação só após aprovação (D11). Dono: Qualidade.', 0.95]]);
fonte(s, 'tabela 23 (FVS) e tabela 16 (hh_retrabalho); custo pela média do custo hora da tabela 05.');

const cap = J.cap;
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Achados' });
s.addText('Achado 7 · Pronta, a unidade não atende o pico: o hidrotérmico faz só 76% da demanda', { placeholder: 'title' });
s.addChart([{ type: pres.charts.BAR, data: [{ name: 'Capacidade (mil cx/dia)', labels: cap.map(c => c.posto), values: cap.map(c => +(c.cap / 1000).toFixed(1)) }], options: { chartColors: [HX.accent5], barGapWidthPct: 50 } },
  { type: pres.charts.LINE, data: [{ name: 'Demanda 42 mil', labels: cap.map(c => c.posto), values: cap.map(() => 42) }], options: { chartColors: [HX.accent3], lineSize: 2, lineDataSymbol: 'none' } }],
  { x: 0.45, y: 1.05, w: 5.0, h: 3.85, showLegend: true, legendPos: 'b', valAxisMinVal: 0, ...chartBase });
achado(s, [['Evidência', 'PT03 (hidrotérmico) 31,9 mil cx/dia e PT05 (paletização) 39,1 mil para 42 mil de demanda. OEE real do site atual abaixo do previsto em todos os postos.', 1.15],
  ['Causa provável', 'Projeto manteve os 4 tanques do site atual; embalagem foi superdimensionada (28 estações para 19 necessárias).', 0.95],
  ['Impacto', 'No pico, 10 mil caixas por dia sem tratamento (24%). Investimento: 2 tanques + 1 paletizadora = R$ 1,23 mi.', 0.85],
  ['Ação e dono', 'Pedir os tanques já (lead time de 80 du) e rever as estações de embalagem. Dono: Engenharia de processos.', 0.85]]);
fonte(s, 'tabela 26 e Anexo D (takt 1,234 s; capacidade = recursos × tempo disponível ÷ ciclo × OEE previsto); D9.');

// 13 · cenários
pres.addSection({ title: 'Decisão' });
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Decisão' });
s.addText('Recuperar o prazo tem o menor impacto total, com risco concentrado no fornecedor F10', { placeholder: 'title' });
const H = { fill: { color: HX.dk2 }, color: 'FFFFFF', bold: true, fontSize: 12, align: 'center', valign: 'middle' };
const cel = (t, o = {}) => ({ text: String(t), options: { fontSize: 12, color: HX.dk1, align: 'center', valign: 'middle', ...o } });
const rows = [[{ text: '', options: H }, { text: '1. Seguir como está', options: H }, { text: '2. Recuperar o prazo', options: { ...H, fill: { color: HX.accent5 } } }, { text: '3. Replanejar', options: H }],
  [cel('O que muda', { align: 'left', bold: true }), cel('nada'), cel('2º turno A12 e A26 + câmaras antes'), cel('2º turno só no A12')],
  [cel('Término', { align: 'left', bold: true }), cel(dt(c1.fim)), cel(dt(c2.fim), { bold: true }), cel(dt(c3.fim))],
  [cel('Atraso sobre o contrato', { align: 'left', bold: true }), cel(c1.atraso_contrato_du + ' du'), cel('0 du', { bold: true }), cel(c3.atraso_contrato_du + ' du')],
  [cel('Custo adicional', { align: 'left', bold: true }), cel('R$ 0'), cel(mil(c2.custo_adicional)), cel(mil(c3.custo_adicional))],
  [cel('Multa evitada', { align: 'left', bold: true }), cel('R$ 0'), cel(mil(c1.multa)), cel(mil(c1.multa - c3.multa))],
  [cel('Ganho operacional (vs contrato)', { align: 'left', bold: true }), cel('−' + mil(c1.ganho_perdido_vs_contrato)), cel('+' + mil(-c2.ganho_perdido_vs_contrato)), cel('−' + mil(c3.ganho_perdido_vs_contrato))],
  [cel('Impacto total', { align: 'left', bold: true }), cel(mi(c1.impacto_total), { bold: true, color: HX.accent3 }), cel(mil(c2.impacto_total), { bold: true, color: HX.accent5 }), cel(mi(c3.impacto_total), { bold: true })]];
s.addTable(rows, { x: 0.45, y: 1.05, w: 9.1, colW: [2.5, 2.2, 2.2, 2.2], rowH: 0.4, border: { type: 'solid', pt: 0.5, color: 'C9CED6' }, fontFace: THEME.bodyFontFace });
s.addText('Impacto total = custo adicional + multa + ganho operacional perdido + administração local além da linha de base. Cada du recuperado vale R$ 49,2 mil; o cenário 2 custa ≈ R$ 8 mil por du.',
  { x: 0.45, y: 4.45, w: 9.1, h: 0.5, fontSize: 12, color: C.text1, margin: 0, isTextBox: true });
fonte(s, 'scripts/cenarios_custos.py (rede D2 + avanço em 13/11); premissas de custo detalhadas no D12.');

// 14 · plano
s = pres.addSlide({ masterName: 'CONTEUDO', sectionTitle: 'Decisão' });
s.addText('Plano das próximas quatro semanas', { placeholder: 'title' });
const plano = [['Semana 47', 'Fechar A10 e liberar o piso na área das câmaras; mobilizar 2º turno da A12', 'Jair Bispo'],
  ['Semana 47', 'Diligenciar F10: tanques, linha de seleção, portas e sensores; pedir 2 tanques extras', 'Suprimentos'],
  ['Semana 48', 'Lookahead de 6 semanas; remover restrições de A24, A28–A31', 'Coordenação de PCP'],
  ['Semana 48', 'Devolver PTAs sem frente; trocar o MUN-01', 'Eng. de equipamentos'],
  ['Semana 49', 'Iniciar A23 (painéis) 10 du após o piso; contratar equipe noturna para A26', 'Hélio Prado'],
  ['Semanal', 'FVS por lote no piso; PPC, IDP e IDC no comitê de sexta', 'Qualidade + PCP']];
s.addTable([[{ text: 'Quando', options: H }, { text: 'Ação', options: H }, { text: 'Dono', options: H }], ...plano.map(r => [cel(r[0], { bold: true }), cel(r[1], { align: 'left' }), cel(r[2])])],
  { x: 0.45, y: 1.05, w: 9.1, colW: [1.3, 5.6, 2.2], rowH: 0.44, border: { type: 'solid', pt: 0.5, color: 'C9CED6' }, fontFace: THEME.bodyFontFace });
s.addText('Ponto de revisão: se até meados de dezembro o F10 confirmar atraso acima de 10 du nos tanques, migrar para o cenário 3 e renegociar a data contratual.',
  { x: 0.45, y: 4.42, w: 9.1, h: 0.5, fontSize: 12, italic: true, color: C.accent3, margin: 0, isTextBox: true });
fonte(s, 'decisão do grupo a partir dos achados 1 a 7 e do cenário 2.');

// 15 · fechamento
s = pres.addSlide({ masterName: 'CAPA', sectionTitle: 'Decisão' });
s.addText('Decisão pedida', { x: 0.6, y: 0.7, w: 8.8, h: 0.4, fontSize: 16, color: C.accent1, bold: true, margin: 0, isTextBox: true });
s.addText(`Aprovar ${mil(c2.custo_adicional)} para recuperar o prazo e R$ 1,23 mi para os tanques e a paletizadora.`, { x: 0.6, y: 1.2, w: 8.6, h: 1.5, fontFace: THEME.headFontFace, fontSize: 28, bold: true, color: C.background1, margin: 0, valign: 'top', isTextBox: true });
s.addText(`Sem decisão: término em ${dt(c1.fim)}, ${mil(c1.multa)} de multa e unidade limitada a 31,9 mil caixas por dia no pico.`, { x: 0.6, y: 3.0, w: 8.6, h: 0.8, fontSize: 16, color: 'CFE0D6', margin: 0, valign: 'top', isTextBox: true });
s.addText('Números: sistema de PCP do grupo e scripts do repositório (tabela e filtro indicados em cada slide).', { x: 0.6, y: 4.7, w: 8.6, h: 0.3, fontSize: 11, color: 'CFE0D6', margin: 0, isTextBox: true });

pres.writeFile({ fileName: OUT }).then(async () => { await applyTheme(OUT, THEME); console.log('ok', OUT); });
