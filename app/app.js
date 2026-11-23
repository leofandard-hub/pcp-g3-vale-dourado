/* Sistema de PCP · G3 · Vale Dourado Frutas
   - Histórico tratado (até 06/11) vem de data/g3.json (gerado por scripts/calculos.py).
   - Lançamentos feitos pelas telas vão para o Supabase (R2) ou, sem conexão, ficam no navegador.
   - Todas as fórmulas seguem o Anexo D do enunciado. */

let G = null;            // dados base
let LANC = [];           // lançamentos [{id, tabela, dados, autor, criado_em}]
const charts = {};
const $ = s => document.querySelector(s);

/* ---------------- formatação ---------------- */
const nf = (v, d = 0) => isFinite(v) ? v.toLocaleString('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d }) : '–';
const fR = v => isFinite(v) ? 'R$ ' + nf(v, 0) : '–';
const fM = v => isFinite(v) ? 'R$ ' + nf(v / 1e6, 2) + ' mi' : '–';
const fP = v => isFinite(v) ? nf(v * 100, 1) + '%' : '–';
const fD = s => s ? s.split('-').reverse().join('/') : '–';
const num = v => v === '' || v === null || v === undefined ? NaN : +String(v).replace(',', '.');

/* ---------------- acesso aos dados ---------------- */
const NUMCOLS = new Set();
function rows(t) {
  const base = G.tabelas[t] || [];
  const man = LANC.filter(l => l.tabela === t).map(l => {
    const r = { ...l.dados, _lanc: l.id, _autor: l.autor };
    for (const k in r) if (NUMCOLS.has(t + '.' + k) && r[k] !== '') r[k] = num(r[k]);
    return r;
  });
  return base.concat(man);
}
const D = () => $('#dataFiltro').value;
const ATIV = () => G.tabelas['03_atividades'];
const BASE = () => G.linha_de_base;
function duAte(data) { // nº de dias úteis do projeto até a data (inclusive)
  let n = 0;
  for (const c of G.tabelas['11_calendario']) if (c.data <= data && c.dia_util_projeto) n = Math.max(n, c.dia_util_projeto);
  return n;
}

/* ---------------- cálculos (Anexo D) ---------------- */
function calc(data) {
  const n = duAte(data);
  const prod = rows('16_rdo_producao').filter(r => r.data <= data);
  const cust = rows('20_custos_apropriados').filter(r => r.data <= data);
  const qExec = {}; prod.forEach(r => qExec[r.id_atividade] = (qExec[r.id_atividade] || 0) + num(r.quantidade_executada));
  const crAt = {}; let crSem = 0, crInd = 0;
  cust.forEach(r => {
    if (r.categoria === 'INDIRETO') { crInd += num(r.valor_rs); return; }
    if (r.id_atividade) crAt[r.id_atividade] = (crAt[r.id_atividade] || 0) + num(r.valor_rs); else crSem += num(r.valor_rs);
  });
  const at = ATIV().map(a => {
    const b = BASE().find(x => x.id_atividade === a.id_atividade);
    const pPlan = Math.min(1, Math.max(0, (n - b.es_du + 1) / b.duracao_du));
    const pReal = Math.min(1, (qExec[a.id_atividade] || 0) / a.quantidade_orcada);
    const O = b.custo_orcado_rs;
    return { ...a, b, pPlan, pReal, O, VP: O * pPlan, VA: O * pReal, CR: crAt[a.id_atividade] || 0 };
  });
  const tot = k => at.reduce((s, a) => s + a[k], 0);
  const BAC = tot('O'), VP = tot('VP'), VA = tot('VA'), CR = tot('CR') + crSem;
  return { data, n, at, BAC, VP, VA, CR, crInd, IDP: VA / VP, IDC: VA / CR, EAC: BAC / (VA / CR) };
}

function porFase(c) {
  const f = {};
  c.at.forEach(a => {
    const x = f[a.fase] = f[a.fase] || { fase: a.fase, eap: a.codigo_eap.split('.').slice(0, 2).join('.'), O: 0, VP: 0, VA: 0, CR: 0 };
    x.O += a.O; x.VP += a.VP; x.VA += a.VA; x.CR += a.CR;
  });
  return Object.values(f);
}

function ppc(data) {
  const ps = rows('21_plano_semanal').filter(r => r.data_inicio_semana <= data);
  const sem = {}, causas = {};
  ps.forEach(r => {
    const meta = num(r.meta_quantidade), real = num(r.quantidade_realizada);
    const ok = isFinite(meta) && isFinite(real) && meta > 0 ? real / meta >= 0.97   // Anexo D: concluído = ≥ 97% da meta
      : (+r.concluido === 1 || String(r.concluido).toLowerCase() === 'sim');
    const s = sem[r.semana] = sem[r.semana] || { p: 0, c: 0 };
    s.p++; if (ok) s.c++;
    if (!ok && r.causa_nao_cumprimento) causas[r.causa_nao_cumprimento] = (causas[r.causa_nao_cumprimento] || 0) + 1;
  });
  const ks = Object.keys(sem).sort();
  return { ks, sem, causas };
}

function histograma(data) {
  const cal = G.tabelas['11_calendario'].filter(c => c.dia_util_projeto);
  const real = {}, prev = {};
  rows('15_rdo_mao_de_obra').filter(r => r.data <= data).forEach(r => {
    real[r.data] = (real[r.data] || 0) + num(r.efetivo_presente);
  });
  const fim = Math.max(...BASE().map(b => b.ef_du));
  const sem = {};
  cal.filter(c => c.dia_util_projeto <= fim).forEach(c => {
    const p = BASE().filter(b => b.es_du <= c.dia_util_projeto && c.dia_util_projeto <= b.ef_du).reduce((s, b) => s + b.efetivo, 0);
    const w = sem[c.semana] = sem[c.semana] || { p: 0, r: 0, d: 0, dr: 0 };
    w.p += p; w.d++;
    if (c.data <= data) { w.r += real[c.data] || 0; w.dr++; }
  });
  const ks = Object.keys(sem).sort();
  return { ks, prev: ks.map(k => sem[k].p / sem[k].d), real: ks.map(k => sem[k].dr ? sem[k].r / sem[k].dr : null) };
}

function rup(data) {
  const hh = {}, q = {};
  rows('15_rdo_mao_de_obra').filter(r => r.data <= data).forEach(r => hh[r.id_atividade] = (hh[r.id_atividade] || 0) + num(r.horas_normais) + num(r.horas_extras));
  rows('16_rdo_producao').filter(r => r.data <= data).forEach(r => q[r.id_atividade] = (q[r.id_atividade] || 0) + num(r.quantidade_executada));
  const L = ATIV().filter(a => a.rup_orcada_hh_un && hh[a.id_atividade] && q[a.id_atividade]).map(a => {
    const real = hh[a.id_atividade] / q[a.id_atividade];
    return { id: a.id_atividade, nome: a.nome_atividade, enc: a.encarregado, orc: a.rup_orcada_hh_un, real, desvio: real / a.rup_orcada_hh_un - 1, hh: hh[a.id_atividade], hhOrc: q[a.id_atividade] * a.rup_orcada_hh_un };
  }).sort((x, y) => y.desvio - x.desvio);
  const enc = {};
  L.forEach(r => { const e = enc[r.enc] = enc[r.enc] || { hh: 0, hhOrc: 0, n: 0 }; e.hh += r.hh; e.hhOrc += r.hhOrc; e.n++; });
  return { L, enc };
}

function hhTotal(data) { return rows('15_rdo_mao_de_obra').filter(r => r.data <= data).reduce((s, r) => s + num(r.horas_normais) + num(r.horas_extras), 0); }

/* ---------------- dashboard ---------------- */
function kpi(l, v, cls = '', sub = '') { return `<div class="kpi ${cls}"><div class="v">${v}</div><div class="l">${l}${sub ? '<br>' + sub : ''}</div></div>`; }
const cl = (v, ok, w) => !isFinite(v) ? '' : v >= ok ? 'ok' : v >= w ? 'warn' : 'bad';

function renderDash() {
  const d = D(), c = calc(d), P = ppc(d);
  const ult = P.ks.at(-1), ppcUlt = ult ? P.sem[ult].c / P.sem[ult].p : NaN;
  const fimBase = G.du2data[G.fim_du];
  $('#kpis').innerHTML =
    kpi('Avanço físico real', fP(c.VA / c.BAC), '', 'previsto ' + fP(c.VP / c.BAC)) +
    kpi('IDP = VA/VP', nf(c.IDP, 2), cl(c.IDP, .95, .85)) +
    kpi('IDC = VA/CR', nf(c.IDC, 2), cl(c.IDC, .95, .85)) +
    kpi('Custo real (CR)', fM(c.CR), '', 'VA ' + fM(c.VA)) +
    kpi('Estimativa no término', fM(c.EAC), c.EAC > c.BAC ? 'bad' : 'ok', 'orçado ' + fM(c.BAC)) +
    kpi('PPC ' + (ult || ''), fP(ppcUlt), cl(ppcUlt, .8, .6)) +
    kpi('Término linha de base', fD(fimBase), '', 'contrato 23/03/2027');

  // curva S mensal
  const meses = [...new Set(G.tabelas['11_calendario'].map(x => x.mes))].filter(m => m <= '2027-03');
  const pts = meses.map(m => { const dd = G.tabelas['11_calendario'].filter(x => x.mes === m).at(-1).data; return { m, dd, c: calc(dd) }; });
  draw('chartS', 'line', {
    labels: pts.map(p => p.m),
    datasets: [
      { label: 'VP', data: pts.map(p => p.c.VP / 1e6), borderColor: '#6b7385', pointRadius: 0, tension: .2 },
      { label: 'VA', data: pts.map(p => p.dd <= d ? p.c.VA / 1e6 : null), borderColor: '#2e9e5b', pointRadius: 2, tension: .2 },
      { label: 'CR', data: pts.map(p => p.dd <= d ? p.c.CR / 1e6 : null), borderColor: '#c0392b', pointRadius: 2, tension: .2 }]
  });
  const ks = P.ks.slice(-16);
  draw('chartPPC', 'bar', {
    labels: ks.map(k => k.slice(5)),
    datasets: [{ label: 'PPC %', data: ks.map(k => P.sem[k].c / P.sem[k].p * 100), backgroundColor: ks.map(k => P.sem[k].c / P.sem[k].p >= .8 ? '#2e9e5b' : '#1f4d3a') },
      { type: 'line', label: 'meta', data: ks.map(() => 80), borderColor: '#d4880f', pointRadius: 0 }]
  }, { scales: { y: { min: 0, max: 100 } } });
  const cs = Object.entries(P.causas).sort((a, b) => b[1] - a[1]), tot = cs.reduce((s, x) => s + x[1], 0); let acc = 0;
  draw('chartPareto', 'bar', {
    labels: cs.map(x => x[0]),
    datasets: [{ label: 'ocorrências', data: cs.map(x => x[1]), backgroundColor: '#3b6ea5', yAxisID: 'y' },
      { type: 'line', label: '% acum.', data: cs.map(x => (acc += x[1]) / tot * 100), borderColor: '#c0392b', yAxisID: 'y2' }]
  }, { scales: { y: { beginAtZero: true, position: 'left' }, y2: { position: 'right', min: 0, max: 100, grid: { display: false } } } });
  const H = histograma(d);
  draw('chartHist', 'bar', {
    labels: H.ks.map(k => k.slice(2)),
    datasets: [{ label: 'real', data: H.real, backgroundColor: '#2e9e5b' },
      { type: 'line', label: 'previsto (linha de base)', data: H.prev, borderColor: '#6b7385', pointRadius: 0, stepped: true },
      { type: 'line', label: 'máx. canteiro 130', data: H.ks.map(() => 130), borderColor: '#c0392b', borderDash: [4, 4], pointRadius: 0 }]
  });
  const F = porFase(c);
  draw('chartFases', 'bar', {
    labels: F.map(f => f.eap),
    datasets: [{ label: '% previsto', data: F.map(f => f.VP / f.O * 100), backgroundColor: '#c9ced6' },
      { label: '% real', data: F.map(f => f.VA / f.O * 100), backgroundColor: '#2e9e5b' }]
  }, { scales: { y: { min: 0, max: 100 } } });

  // alertas
  const al = [];
  c.at.filter(a => a.b.critica && a.pPlan - a.pReal > .05).forEach(a => al.push(`<b>Crítica atrasada</b> ${a.id_atividade} ${a.nome_atividade}: real ${fP(a.pReal)} × previsto ${fP(a.pPlan)}`));
  if (c.IDP < .9) al.push(`<b>Prazo</b>: IDP ${nf(c.IDP, 2)} — ${fM(c.VP - c.VA)} de trabalho previsto não realizado`);
  if (c.IDC < 1) al.push(`<b>Custo</b>: IDC ${nf(c.IDC, 2)} — estimativa no término ${fM(c.EAC)} (${fM(c.EAC - c.BAC)} acima)`);
  pedidos(d).filter(p => p.atrasado).slice(0, 5).forEach(p => al.push(`<b>Pedido atrasado</b> ${p.id_pedido} ${p.id_material} (${p.id_fornecedor}) — prometido ${fD(p.data_prometida)}`));
  limitesPedido(d).filter(x => x.alerta).slice(0, 5).forEach(x => al.push(`<b>Data-limite de pedido</b> ${x.mat} p/ ${x.ativ}: pedir até ${fD(x.limite)}`));
  $('#alertas').innerHTML = al.map(a => `<li>${a}</li>`).join('') || '<li>Sem alertas.</li>';
}
function draw(id, type, data, options = {}) {
  if (charts[id]) charts[id].destroy();
  charts[id] = new Chart(document.getElementById(id), { type, data, options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, font: { size: 10 } } } }, ...options } });
}

/* ---------------- suprimentos e equipamentos ---------------- */
function pedidos(d) {
  return rows('18_compras_pedidos').filter(p => p.data_pedido <= d).map(p => {
    const entregue = p.data_entrega && p.data_entrega <= d;
    return { ...p, aberto: !entregue, atrasado: !entregue && p.data_prometida < d, atrasoEntrega: entregue ? diasUteis(p.data_prometida, p.data_entrega) : null };
  });
}
function diasUteis(a, b) { // dias úteis de a até b (negativo se adiantado)
  const cal = G.tabelas['11_calendario'];
  const s = a < b ? 1 : -1, [x, y] = a < b ? [a, b] : [b, a];
  return s * cal.filter(c => c.data > x && c.data <= y && +c.dia_util === 1).length;
}
function limitesPedido(d) { // itens A/B: data de uso − lead time − margem (5 du), sem pedido emitido
  const mats = Object.fromEntries(G.tabelas['08_materiais'].map(m => [m.id_material, m]));
  const ped = rows('18_compras_pedidos');
  const out = [];
  G.tabelas['09_atividade_materiais'].forEach(am => {
    const b = BASE().find(x => x.id_atividade === am.id_atividade), m = mats[am.id_material];
    if (!b || !m) return;
    const uso = b.es_du, lim = uso - m.lead_time_du - 5;
    const limite = G.du2data[Math.max(1, lim)];
    const temPedido = ped.some(p => p.id_material === am.id_material && p.id_atividade === am.id_atividade && p.data_pedido <= d);
    out.push({ mat: am.id_material, ativ: am.id_atividade, limite, alerta: !temPedido && limite <= addDias(d, 10) });
  });
  return out.sort((x, y) => x.limite < y.limite ? -1 : 1);
}
function addDias(d, n) { const x = new Date(d); x.setDate(x.getDate() + n); return x.toISOString().slice(0, 10); }

function equipamentos(d) {
  const t = {};
  rows('17_equipamentos_apontamento').filter(r => r.data <= d).forEach(r => {
    const k = String(r.id_equipamento).split('-')[0];
    const x = t[k] = t[k] || { disp: 0, op: 0, cor: 0, prev: 0, oc: 0, f: 0, dias: 0, semAtiv: 0 };
    x.disp += num(r.horas_disponiveis); x.op += num(r.horas_operando); x.cor += num(r.horas_manutencao_corretiva);
    x.prev += num(r.horas_manutencao_preventiva); x.oc += num(r.horas_ociosas); x.f += num(r.numero_falhas) || 0; x.dias++;
    if (!r.id_atividade) x.semAtiv++;
  });
  return Object.entries(t).map(([k, x]) => ({ tipo: k, ...x, dispon: 1 - (x.cor + x.prev) / x.disp, util: x.op / x.disp, mtbf: x.f ? x.op / x.f : NaN, mttr: x.f ? x.cor / x.f : NaN }));
}

/* ---------------- tela Análises ---------------- */
function tabela(id, cab, linhas) {
  $(id).innerHTML = '<tr>' + cab.map(c => `<th>${c}</th>`).join('') + '</tr>' + linhas.join('');
}
function renderAnalises() {
  const d = D(), c = calc(d), F = porFase(c);
  const tr = (cells, cls = '') => `<tr class="${cls}">` + cells.map(x => `<td class="${typeof x === 'string' && !/^R\$|%$|^[\d.,–-]+$/.test(x) ? '' : 'num'}">${x}</td>`).join('') + '</tr>';
  const lf = F.map(f => tr([f.eap + ' ' + f.fase, fR(f.O), fP(f.VP / f.O), fP(f.VA / f.O), fR(f.VP), fR(f.VA), fR(f.CR), fR(f.VA - f.VP), fR(f.VA - f.CR), nf(f.VA / f.VP, 2), nf(f.VA / f.CR, 2)]));
  lf.push(tr(['<b>TOTAL</b>', fR(c.BAC), fP(c.VP / c.BAC), fP(c.VA / c.BAC), fR(c.VP), fR(c.VA), fR(c.CR), fR(c.VA - c.VP), fR(c.VA - c.CR), nf(c.IDP, 2), nf(c.IDC, 2)]));
  tabela('#tabFases', ['Fase', 'Orçamento', '% prev.', '% real', 'VP', 'VA', 'CR', 'VPr (VA−VP)', 'VC (VA−CR)', 'IDP', 'IDC'], lf);
  $('#tabFases').insertAdjacentHTML('afterend', '');
  tabela('#tabAtiv', ['Ativ.', 'Nome', 'Fase', 'Dur. (du)', 'Início LB', 'Término LB', 'Folga', '% prev.', '% real', 'VP', 'VA', 'CR'],
    c.at.map(a => tr([a.id_atividade, a.nome_atividade, a.codigo_eap, a.b.duracao_du, fD(a.b.inicio_cedo), fD(a.b.termino_cedo), a.b.folga_total_du, fP(a.pPlan), fP(a.pReal), fR(a.VP), fR(a.VA), fR(a.CR)], a.b.critica ? 'crit' : '')));

  const R = rup(d);
  const sel = R.L.length > 10 ? R.L.slice(0, 5).concat(R.L.slice(-5)) : R.L;
  tabela('#tabRup', ['Ativ.', 'Encarregado', 'RUP orçada', 'RUP real', 'Desvio'],
    sel.map((r, i) => tr([r.id + ' ' + r.nome.slice(0, 28), r.enc, nf(r.orc, 3), nf(r.real, 3), fP(r.desvio)], r.desvio > 0 ? 'crit' : '')));
  if (R.L.length > 10) $('#tabRup').rows[6].insertAdjacentHTML('beforebegin', '<tr><td colspan="5" class="hint">… 5 piores acima · 5 melhores abaixo</td></tr>');
  tabela('#tabRupEnc', ['Encarregado', 'Atividades', 'Hh reais', 'Hh orçadas p/ o executado', 'Real ÷ orçado'],
    Object.entries(R.enc).map(([e, x]) => tr([e, x.n, nf(x.hh, 0), nf(x.hhOrc, 0), fP(x.hh / x.hhOrc)], x.hh > x.hhOrc ? 'crit' : '')));
  const m = rows('15_rdo_mao_de_obra').filter(r => r.data <= d);
  const pv = m.reduce((s, r) => s + num(r.efetivo_previsto), 0), pr = m.reduce((s, r) => s + num(r.efetivo_presente), 0);
  $('#absent').innerHTML = `Absenteísmo acumulado: <b>${fP(1 - pr / pv)}</b> (${nf(pv - pr)} faltas em ${nf(pv)} homens-dia previstos) · Hh apontadas: <b>${nf(hhTotal(d), 1)}</b>`;

  const P = pedidos(d).filter(p => p.aberto);
  tabela('#tabPedidos', ['Pedido', 'Material', 'Ativ.', 'Forn.', 'Pedido em', 'Necessidade', 'Prometida', 'Situação'],
    P.map(p => tr([p.id_pedido, p.id_material, p.id_atividade, p.id_fornecedor, fD(p.data_pedido), fD(p.data_necessidade_obra), fD(p.data_prometida), p.atrasado ? 'ATRASADO' : 'em aberto'], p.atrasado ? 'crit' : '')));
  const fo = {};
  pedidos(d).forEach(p => { const x = fo[p.id_fornecedor] = fo[p.id_fornecedor] || { n: 0, ent: 0, atr: 0, soma: 0, abertoAtr: 0 }; x.n++; if (p.atrasoEntrega !== null) { x.ent++; x.soma += p.atrasoEntrega; if (p.atrasoEntrega > 0) x.atr++; } if (p.atrasado) x.abertoAtr++; });
  const nomes = Object.fromEntries(G.tabelas['10_fornecedores'].map(f => [f.id_fornecedor, f.nome_fornecedor]));
  tabela('#tabForn', ['Fornecedor', 'Pedidos', 'Entregues', 'Entregues c/ atraso', 'Atraso médio (du)', 'Em atraso hoje'],
    Object.entries(fo).sort((a, b) => b[1].soma / b[1].ent - a[1].soma / a[1].ent).map(([f, x]) => tr([f + ' ' + (nomes[f] || ''), x.n, x.ent, x.atr, nf(x.soma / x.ent, 1), x.abertoAtr], x.soma / x.ent > 2 ? 'crit' : '')));
  tabela('#tabEquip', ['Tipo', 'Diárias apontadas', 'Horas disp.', 'Operando', 'Disponibilidade', 'Utilização', 'Falhas', 'MTBF (h)', 'MTTR (h)', 'Ociosas (h)', 'Dias sem atividade'],
    equipamentos(d).map(e => tr([e.tipo, e.dias, nf(e.disp, 0), nf(e.op, 0), fP(e.dispon), fP(e.util), e.f, nf(e.mtbf, 1), nf(e.mttr, 1), nf(e.oc, 0), e.semAtiv], e.util < .6 ? 'crit' : '')));
}

/* ---------------- R3 · telas de lançamento ---------------- */
const TELAS = {
  '15_rdo_mao_de_obra': 'RDO · mão de obra', '16_rdo_producao': 'RDO · produção e ocorrências',
  '17_equipamentos_apontamento': 'Equipamentos (apontamento diário)', '18_compras_pedidos': 'Pedido de compra',
  '19_estoque_movimentos': 'Recebimento / requisição de material', '21_plano_semanal': 'Plano semanal e fechamento',
  '22_restricoes': 'Restrições (lookahead)', '23_inspecoes_qualidade': 'FVS (inspeção de serviço)',
  '24_ocorrencias_seguranca': 'Ocorrências de segurança', '20_custos_apropriados': 'Custos (apropriação)'
};
function renderForm() {
  const t = $('#formTabela').value, base = G.tabelas[t];
  const cols = Object.keys(base[0]);
  $('#form').innerHTML = cols.map(c => {
    const vals = [...new Set(base.map(r => r[c]).filter(v => v !== null && v !== ''))];
    const isNum = NUMCOLS.has(t + '.' + c);
    if (c.startsWith('data')) return `<label>${c}<input type="date" name="${c}" value="${localStorage.getItem('pcp_ultima_data') || ''}"></label>`;
    if (!isNum && vals.length && vals.length <= 40) {
      const opts = c === 'id_atividade' ? ATIV().map(a => a.id_atividade) : vals.sort();
      return `<label>${c}<input name="${c}" list="dl_${c}"><datalist id="dl_${c}">${opts.map(o => `<option value="${o}">`).join('')}</datalist></label>`;
    }
    return `<label>${c}<input name="${c}" ${isNum ? 'type="number" step="any"' : ''}></label>`;
  }).join('');
  renderLancTab();
}
function renderLancTab() {
  const t = $('#formTabela').value, L = LANC.filter(l => l.tabela === t);
  const cols = Object.keys(G.tabelas[t][0]);
  $('#lancInfo').textContent = `(${L.length} lançado(s) · ${G.tabelas[t].length} do histórico)`;
  $('#tabLanc').innerHTML = L.length ? '<tr><th></th><th>por</th>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr>' +
    L.map(l => `<tr><td><button class="danger mini" data-id="${l.id}">x</button></td><td>${l.autor || ''}</td>` + cols.map(c => `<td>${l.dados[c] ?? ''}</td>`).join('') + '</tr>').join('')
    : '<tr><td>Nenhum lançamento nesta tela.</td></tr>';
  // apagar em dois cliques (sem janela de confirmação, que alguns navegadores bloqueiam)
  document.querySelectorAll('#tabLanc button').forEach(b => b.onclick = () => {
    if (b.dataset.ok) return apagar(b.dataset.id);
    b.dataset.ok = '1'; b.textContent = 'apagar?'; setTimeout(() => { delete b.dataset.ok; b.textContent = 'x'; }, 4000);
  });
}
$('#btnLancar').onclick = async e => {
  e.preventDefault();
  const autor = $('#autor').value.trim();
  if (!autor) { $('#formMsg').textContent = ' informe quem lança'; return; }
  localStorage.setItem('pcp_autor', autor);
  const dados = {}; new FormData($('#form')).forEach((v, k) => dados[k] = v);
  if ('data' in dados && !dados.data) { $('#formMsg').textContent = ' informe a data'; return; }
  if (dados.data) localStorage.setItem('pcp_ultima_data', dados.data);
  await salvar({ tabela: $('#formTabela').value, dados, autor });
  $('#formMsg').textContent = ' ✓ lançado';
  $('#form').querySelectorAll('input:not([type=date])').forEach(i => i.value = '');
};

/* ---------------- R2 · persistência (Supabase REST) ---------------- */
const SB = { url: localStorage.getItem('sb_url') || '', key: localStorage.getItem('sb_key') || '' };
const sbOn = () => SB.url && SB.key;
// chave legada (JWT "eyJ...") vai também no Authorization; a chave nova "sb_publishable_..." só no header apikey
const sbH = () => ({ apikey: SB.key, ...(SB.key.startsWith('eyJ') ? { Authorization: 'Bearer ' + SB.key } : {}), 'Content-Type': 'application/json', Prefer: 'return=representation' });
async function carregarLanc() {
  if (sbOn()) {
    try {
      const r = await fetch(`${SB.url}/rest/v1/lancamentos?select=*&order=id`, { headers: sbH() });
      if (!r.ok) throw new Error(r.status + ' ' + await r.text());
      LANC = await r.json(); setSync('nuvem ✓', true); return;
    } catch (e) { setSync('nuvem ✗ (local)', false); console.error(e); }
  } else setSync('modo local', false);
  try { LANC = JSON.parse(localStorage.getItem('pcp_lanc') || '[]'); } catch { LANC = []; }
}
async function salvar(l) {
  if (sbOn()) {
    const r = await fetch(`${SB.url}/rest/v1/lancamentos`, { method: 'POST', headers: sbH(), body: JSON.stringify(l) });
    if (r.ok) { await carregarLanc(); return refresh(); }
    alert('Erro ao gravar no Supabase: ' + await r.text());
  }
  LANC.push({ ...l, id: 'L' + Date.now(), criado_em: new Date().toISOString() });
  localStorage.setItem('pcp_lanc', JSON.stringify(LANC.filter(x => String(x.id).startsWith('L'))));
  refresh();
}
async function apagar(id) {
  if (sbOn() && !String(id).startsWith('L')) {
    const r = await fetch(`${SB.url}/rest/v1/lancamentos?id=eq.${id}`, { method: 'DELETE', headers: sbH() });
    if (!r.ok) alert('Erro ao apagar no Supabase: ' + await r.text());
  }
  else { LANC = LANC.filter(l => l.id !== id); localStorage.setItem('pcp_lanc', JSON.stringify(LANC)); }
  await carregarLanc(); refresh();
}
function setSync(t, ok) { $('#syncStatus').textContent = t; $('#syncStatus').style.background = ok ? '#2e9e5b' : 'rgba(255,255,255,.15)'; }
$('#btnSb').onclick = async () => {
  SB.url = $('#sbUrl').value.trim().replace(/\/$/, ''); SB.key = $('#sbKey').value.trim();
  localStorage.setItem('sb_url', SB.url); localStorage.setItem('sb_key', SB.key);
  await carregarLanc(); $('#sbMsg').textContent = $('#syncStatus').textContent; refresh();
};

/* ---------------- números de controle ---------------- */
function renderControle() {
  const linhas = [
    ['Linhas da tabela 15 (sem duplicatas) — histórico', 691, G.tabelas['15_rdo_mao_de_obra'].length, 0],
    ['Hh apontadas até 06/11/2026', 53222.4, hhTotal('2026-11-06'), 1],
    ['Custo direto apropriado até 06/11/2026', 11419304.12, calc('2026-11-06').CR, 2],
    ['Pedidos de compra emitidos até 06/11/2026', 124, rows('18_compras_pedidos').filter(p => p.data_pedido <= '2026-11-06').length, 0],
    ['Hh apontadas até 13/11/2026 (após semana de campo)', 55086.8, hhTotal('2026-11-13'), 1],
    ['Custo direto apropriado até 13/11/2026 (após semana de campo)', 11689047.31, calc('2026-11-13').CR, 2]];
  tabela('#tabControle', ['Conferência', 'Dossiê', 'Sistema', 'Bate?'],
    linhas.map(([l, e, s, d]) => `<tr><td>${l}</td><td class="num">${nf(e, d)}</td><td class="num">${nf(s, d)}</td><td>${Math.abs(e - s) < 0.05 ? '✔' : '✘'}</td></tr>`));
}

/* ---------------- API p/ o modelo 3D ---------------- */
window.PCP = {
  zonas: () => G.tabelas['13_layout_zonas'],
  calc, D, fP, fD,
  datas: () => G.tabelas['11_calendario'].filter(c => c.dia_util_projeto && c.data <= '2027-03-31').map(c => c.data)
};

/* ---------------- navegação e inicialização ---------------- */
document.querySelectorAll('nav button').forEach(b => b.onclick = () => {
  document.querySelectorAll('nav button, .tab').forEach(x => x.classList.remove('active'));
  b.classList.add('active'); $('#' + b.dataset.tab).classList.add('active');
  refresh();
});
$('#dataFiltro').onchange = () => { window.dispatchEvent(new Event('pcp:data')); refresh(); };
$('#formTabela').onchange = renderForm;

function refresh() {
  const tab = document.querySelector('.tab.active').id;
  if (tab === 'dashboard') renderDash();
  if (tab === 'analises') renderAnalises();
  if (tab === 'lancamentos') renderLancTab();
  if (tab === 'config') renderControle();
  if (tab === 'modelo') window.dispatchEvent(new Event('pcp:show3d'));
}

(async function init() {
  G = await (await fetch('data/g3.json')).json();
  for (const [t, rs] of Object.entries(G.tabelas)) if (rs[0]) for (const k in rs[0]) if (rs.every(r => r[k] === null || typeof r[k] === 'number')) NUMCOLS.add(t + '.' + k);
  $('#formTabela').innerHTML = Object.entries(TELAS).map(([k, v]) => `<option value="${k}">${v}</option>`).join('');
  $('#autor').value = localStorage.getItem('pcp_autor') || '';
  $('#sbUrl').value = SB.url; $('#sbKey').value = SB.key;
  await carregarLanc();
  renderForm(); refresh();
  window.PCP.ready = true; window.dispatchEvent(new Event('pcp:ready'));
})();
