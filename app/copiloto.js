/* Copiloto IA (opcional): envia a pergunta + os números do sistema para /api/chat (função Vercel).
   A chave da IA fica só na Vercel; este arquivo não tem nenhuma senha. */
(function () {
  const $ = s => document.querySelector(s);
  const SUGESTOES = [
    'Por que a obra está atrasada?',
    'Quando a obra termina se nada mudar, e qual a multa?',
    'Compare os 3 cenários de decisão.',
    'Quais atividades críticas estão mais atrasadas?',
    'Qual é o gargalo da nova unidade?',
    'Quais encarregados têm a pior RUP?'
  ];
  let relatorio = null, historico = [];
  const REPO = 'https://github.com/leofandard-hub/pcp-g3-vale-dourado/blob/main/docs/relatorio_gerencial.pdf';
  // de onde veio o dado (linha "Fonte:" e atividades citadas) -> tela do sistema onde conferir
  const TELAS = [
    [/sistema\.(evm|ppc_semanas|causas_nao_cumprimento)|efetivo_medio/, 'dashboard', 'Dashboard'],
    [/sistema\.(atividades|fases|rup|equipamentos|pedidos|fornecedores|mao_de_obra|hh_)/, 'analises', 'Análises'],
    [/sistema\.(qualidade_fvs|restricoes_abertas|seguranca)/, 'lancamentos', 'Lançamentos'],
    [/\bA\d{2}\b/, 'modelo', 'Modelo 3D']];
  function links(texto) {
    const fonte = (texto.match(/Fonte:[^\n]*/i) || [''])[0], out = [];
    TELAS.forEach(([re, tab, nome]) => { if (re.test(tab === 'modelo' ? texto : fonte)) out.push(`<button type="button" class="ghost irTela" data-tab="${tab}">→ ver em ${nome}</button>`); });
    if (/relatorio\./.test(fonte)) out.push(`<a class="irTela" href="${REPO}" target="_blank" rel="noopener">→ relatório gerencial (PDF)</a>`);
    return out.length ? `<div class="links">${out.join(' ')}</div>` : '';
  }
  document.addEventListener('click', e => {
    const b = e.target.closest('button.irTela'); if (!b) return;
    document.querySelector(`nav button[data-tab="${b.dataset.tab}"]`).click(); window.scrollTo(0, 0);
  });
  const esc = t => String(t).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

  $('#sugIA').innerHTML = SUGESTOES.map(q => `<button type="button">${q}</button>`).join('');
  $('#sugIA').onclick = e => { if (e.target.tagName === 'BUTTON') { $('#perguntaIA').value = e.target.textContent; perguntar(); } };
  $('#btnIA').onclick = () => perguntar();
  $('#btnAta').onclick = () => perguntar('ata');
  $('#btnNovaIA').onclick = () => { historico = []; $('#respostasIA').innerHTML = ''; $('#perguntaIA').focus(); };
  $('#perguntaIA').onkeydown = e => { if (e.key === 'Enter') perguntar(); };

  /* ---------- verificador de números ----------
     Cada número da resposta precisa existir nos dados enviados à IA, com o arredondamento mostrado
     (percentual pode vir como fração: 0,6 = 60%). Datas são comparadas com as datas dos dados.
     Limite: números inteiros pequenos podem coincidir por acaso com outro dado; o teste é forte para R$, datas e decimais. */
  function valoresDoContexto(ctx) {
    const nums = new Set(), datas = new Set();
    (function andar(x) {
      if (x === null || x === undefined) return;
      if (typeof x === 'number') { if (isFinite(x)) nums.add(x); return; }
      if (typeof x === 'string') {
        (x.match(/\d{4}-\d{2}-\d{2}/g) || []).forEach(d => datas.add(d));
        (x.match(/(?<![A-Za-z\d-])\d+(\.\d+)?(?![\d-])/g) || []).forEach(n => nums.add(+n));
        return;
      }
      if (Array.isArray(x)) return x.forEach(andar);
      if (typeof x === 'object') Object.entries(x).forEach(([k, v]) => { andar(k); andar(v); });
    })(ctx);
    return { nums: [...nums], datas };
  }
  function verificar(texto, ctx) {
    const { nums, datas } = valoresDoContexto(ctx);
    const corpo = texto.split(/\n\s*Fonte:/i)[0];
    const faltando = []; let total = 0;
    // datas aaaa-mm-dd
    const semIso = corpo.replace(/\d{4}-\d{2}-\d{2}/g, t => { total++; if (!datas.has(t)) faltando.push(t); return ' '; });
    // datas dd/mm/aaaa ou dd/mm
    const semDatas = semIso.replace(/(?<!\d)(\d{1,2})\/(\d{1,2})(?:\/(\d{4}))?(?!\d)/g, (t, d, m, a) => {
      total++;
      const dd = d.padStart(2, '0'), mm = m.padStart(2, '0');
      const ok = [...datas].some(x => x.slice(8) === dd && x.slice(5, 7) === mm && (!a || x.slice(0, 4) === a));
      if (!ok) faltando.push(t);
      return ' ';
    });
    // números (formato pt-BR ou en), ignorando códigos como A12, F10, PT03, S46, 2026-S46
    const re = /(?<![A-Za-z\d_.,\-])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:[.,]\d+)?)(\s*(?:mi\b|milh(?:ão|ões)|mil\b))?(?![\dA-Za-z\-])/g;
    let mt;
    while ((mt = re.exec(semDatas))) {
      const bruto = mt[1], mult = mt[2] ? (/mil\b/.test(mt[2]) && !/milh/.test(mt[2]) ? 1e3 : 1e6) : 1;
      let s = bruto, dec = 0;
      if (/^\d{1,3}(\.\d{3})+(,\d+)?$/.test(s)) s = s.replace(/\./g, '').replace(',', '.');
      else s = s.replace(',', '.');
      if (s.includes('.')) dec = s.split('.')[1].length;
      const v = +s * mult;
      if (!dec && mult === 1 && v < 10) continue;               // contagens pequenas ("3 cenários") não são conferidas
      total++;
      const tol = 0.5 * Math.pow(10, -dec) * mult + 1e-9;
      const perto = c => Math.abs(c - v) <= tol || Math.abs(c * 100 - v) <= tol;
      const ok = nums.some(perto);
      if (!ok) faltando.push(bruto + (mt[2] || ''));
    }
    return { total, faltando };
  }
  window.PCP_verificar = verificar; // usado nos testes
  window.PCP_gravidade = (...a) => gravidade(...a);

  /* ---------- apresentação visual ---------- */
  const COR = { critico: '🔴', atencao: '🟠', ok: '🟢', info: '🔵' };
  function lerCartao(txt) {
    try { const o = JSON.parse(String(txt).replace(/^```(json)?|```$/g, '').trim()); return o && o.titulo ? o : null; } catch { return null; }
  }
  const textoDoCartao = c => [c.titulo, ...(c.numeros || []).flatMap(n => [n.valor, n.detalhe,
    n.real_pct != null ? n.real_pct + '%' : '', n.previsto_pct != null ? n.previsto_pct + '%' : '']), ...(c.pontos || []), c.acao]
    .filter(Boolean).join('\n') + '\nFonte: ' + (c.fonte || '');
  /* ---------- cor do cartão calculada pelo site (não pela IA) ----------
     Olha o que a resposta cita (atividades, IDP/IDC, PPC, multa, RUP, equipamentos, pedidos, gargalo)
     e aplica regras fixas sobre os números do sistema. Vale a pior cor encontrada. */
  const NIVEL = { info: 0, ok: 1, atencao: 2, critico: 3 };
  function gravidade(c, ctx, pergunta) {
    const S = ctx.sistema, R = ctx.relatorio || {}, f = String(c.fonte || '');
    const txt = [pergunta, c.titulo, ...(c.numeros || []).flatMap(n => [n.rotulo, n.valor, n.detalhe]), ...(c.pontos || [])].join(' ');
    if (/não está no sistema/i.test(c.titulo || '')) return { g: 'info', motivo: 'dado inexistente' };
    if (/compar|cen[aá]rio/i.test(pergunta) && /cenario/.test(f)) return { g: 'info', motivo: 'comparação de cenários' };
    let g = 'ok', motivos = [];
    const sobe = (n, m) => { if (NIVEL[n] > NIVEL[g]) { g = n; motivos = [m]; } else if (n === g) motivos.push(m); };
    const f1 = v => String(v).replace('.', ',');
    // atividades citadas
    const ids = [...new Set(txt.match(/\bA\d{2}\b/g) || [])];
    ids.forEach(id => {
      const a = S.atividades.find(x => x.id === id); if (!a) return;
      const gap = a.previsto_pct - a.real_pct;
      if (gap > 5) sobe(a.critica ? 'critico' : 'atencao', `${id}${a.critica ? ' crítica' : ''} ${f1(a.real_pct)}% × ${f1(a.previsto_pct)}% previsto`);
    });
    // índices de prazo e custo
    [['IDP', S.evm.IDP], ['IDC', S.evm.IDC]].forEach(([k, v]) => {
      if (new RegExp('\\b' + k + '\\b').test(txt)) sobe(v < 0.9 ? 'critico' : v < 1 ? 'atencao' : 'ok', `${k} ${f1(v)}`);
    });
    if (/avan[cç]o/i.test(txt) && S.evm.avanco_previsto_pct - S.evm.avanco_real_pct > 5)
      sobe('critico', `avanço ${f1(S.evm.avanco_real_pct)}% × ${f1(S.evm.avanco_previsto_pct)}%`);
    // prazo contratual e multa
    if (/multa|término|termina|prazo/i.test(txt) && R.prazo?.atraso_vs_contrato_du > 0)
      sobe('critico', `término ${R.prazo.atraso_vs_contrato_du} du após o contrato`);
    // PPC (última semana)
    const sem = Object.values(S.ppc_semanas || {}), ppcUlt = sem[sem.length - 1];
    if (/\bPPC\b/.test(txt) && ppcUlt != null) sobe(ppcUlt < 80 ? 'atencao' : 'ok', `PPC última semana ${f1(ppcUlt)}%`);
    // recursos
    if (/RUP/.test(txt) && (S.rup || []).some(r => r.desvio_pct > 0)) sobe('atencao', 'RUP real pior que a orçada');
    if (/equipament/i.test(txt) && (S.equipamentos || []).some(e => e.utilizacao_pct < 60)) sobe('atencao', 'equipamento com utilização < 60%');
    if (/pedido|fornecedor|suprimento/i.test(txt) && (S.pedidos_em_aberto || []).some(p => p.atrasado)) sobe('atencao', 'pedidos em atraso');
    if (/gargalo|capacidade/i.test(txt) && (R.cap || []).some(p => p.add > 0)) sobe('atencao', 'posto abaixo da demanda');
    if (!motivos.length) return { g: (c.numeros || []).length ? 'ok' : 'info', motivo: 'nenhum alerta nos números citados' };
    return { g, motivo: motivos.slice(0, 2).join(' · ') };
  }
  // cor de cada número com realizado × previsto: regra fixa
  function statusTile(n) {
    if (n.real_pct == null || n.previsto_pct == null) return n.status || 'neutro';
    const gap = n.previsto_pct - n.real_pct;
    return gap <= 0 ? 'bom' : gap <= 5 ? 'atencao' : 'ruim';
  }

  function htmlCartao(c, grav) {
    const g = grav.g;
    const pct = v => Math.max(0, Math.min(100, +v || 0));
    const pctDe = t => { const m = String(t || '').match(/(\d+(?:,\d+)?)\s*%/); return m ? +m[1].replace(',', '.') : null; };
    (c.numeros || []).forEach(n => { // barra também quando a IA não preencheu real_pct/previsto_pct ("0%" + "previsto 97,5%")
      if (n.real_pct == null && /%/.test(n.valor) && /previsto/i.test(n.detalhe || '')) { n.real_pct = pctDe(n.valor); n.previsto_pct = pctDe(n.detalhe); }
    });
    const tiles = (c.numeros || []).slice(0, 4).map(n => `
      <div class="tileIA ${esc(statusTile(n))}">
        <div class="v">${esc(n.valor ?? '')}</div><div class="l">${esc(n.rotulo ?? '')}</div>
        ${n.real_pct != null && n.previsto_pct != null ? `<div class="barra"><i class="prev" style="width:${pct(n.previsto_pct)}%"></i><i class="real" style="width:${pct(n.real_pct)}%"></i></div>` : ''}
        ${n.detalhe ? `<div class="d">${esc(n.detalhe)}</div>` : ''}
      </div>`).join('');
    return `<div class="cartaoIA g-${g}">
      <div class="veredito">${COR[g]} ${esc(c.titulo)}</div>
      <div class="motivoCor">cor calculada pelo sistema: ${esc(grav.motivo)}</div>
      ${tiles ? `<div class="tilesIA">${tiles}</div>` : ''}
      ${(c.pontos || []).length ? `<ul>${c.pontos.slice(0, 3).map(p => `<li>${esc(p)}</li>`).join('')}</ul>` : ''}
      ${c.acao ? `<div class="acaoIA">➜ <b>Ação:</b> ${esc(c.acao)}</div>` : ''}
    </div>`;
  }
  // ata: markdown simples (títulos, negrito, tópicos), sempre escapado antes
  function htmlAta(t) {
    return esc(t).split('\n').map(l => {
      l = l.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
      if (/^\s*[-*•]\s+/.test(l)) return `<li>${l.replace(/^\s*[-*•]\s+/, '')}</li>`;
      if (/^\s*(#+\s*)?\d+\.\s/.test(l)) return `<h4>${l.replace(/^\s*#+\s*/, '')}</h4>`;
      if (/^\s*Fonte:/i.test(l)) return `<div class="hint">${l}</div>`;
      return l.trim() ? `<p>${l}</p>` : '';
    }).join('').replace(/(<li>.*?<\/li>)+/g, m => `<ul>${m}</ul>`);
  }

  async function perguntar(modo) {
    const q = modo === 'ata' ? 'Ata semanal do Comitê de PCP' : $('#perguntaIA').value.trim();
    if (!q || !window.PCP?.contextoIA) return;
    $('#btnIA').disabled = $('#btnAta').disabled = true; $('#btnIA').textContent = 'pensando…';
    const caixa = document.createElement('div');
    caixa.className = 'msgIA';
    caixa.innerHTML = `<div class="q">${esc(q)}</div><div class="a">…</div>`;
    if (modo !== 'ata') $('#perguntaIA').value = '';   // limpa ao enviar: o usuário já pode digitar a próxima
    $('#respostasIA').append(caixa); caixa.scrollIntoView({ block: 'nearest' });
    try {
      relatorio = relatorio || await (await fetch('data/copiloto.json')).json();
      const contexto = { sistema: window.PCP.contextoIA(), relatorio };
      const r = await fetch('api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pergunta: q, contexto, modo, historico }) });
      const j = await r.json().catch(() => ({ erro: 'Copiloto indisponível neste endereço (a função /api/chat só roda na Vercel).' }));
      if (!r.ok || j.erro) throw new Error(j.erro || r.status);
      const cartao = modo === 'ata' ? null : lerCartao(j.resposta);
      const texto = cartao ? textoDoCartao(cartao) : j.resposta;
      caixa.querySelector('.a').innerHTML = cartao ? htmlCartao(cartao, gravidade(cartao, contexto, q)) : modo === 'ata' ? htmlAta(j.resposta) : esc(j.resposta);
      if (modo !== 'ata') { historico.push({ pergunta: q, resposta: j.resposta }); historico = historico.slice(-4); }
      const v = verificar(texto, contexto);
      caixa.insertAdjacentHTML('beforeend', v.faltando.length
        ? `<div class="verif bad">⚠ Número(s) não encontrado(s) nos dados do sistema: <b>${v.faltando.map(esc).join(' · ')}</b>. Não use sem conferir.</div>`
        : `<div class="verif ok">✔ ${v.total ? `Os ${v.total} números da resposta conferem com os dados do sistema.` : 'Resposta sem números para conferir.'}</div>`);
      caixa.insertAdjacentHTML('beforeend', `<div class="meta">Gerado por IA (${esc(j.modelo)}) com os números do sistema em ${window.PCP.fD(contexto.sistema.data)} </div>` + links(texto));
    } catch (e) {
      caixa.classList.add('erro');
      caixa.querySelector('.a').textContent = String(e.message || e);
    }
    $('#btnIA').disabled = $('#btnAta').disabled = false; $('#btnIA').textContent = 'Perguntar';
  }
})();
