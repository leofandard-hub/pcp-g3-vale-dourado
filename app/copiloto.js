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
  let relatorio = null;
  const esc = t => String(t).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

  $('#sugIA').innerHTML = SUGESTOES.map(q => `<button type="button">${q}</button>`).join('');
  $('#sugIA').onclick = e => { if (e.target.tagName === 'BUTTON') { $('#perguntaIA').value = e.target.textContent; perguntar(); } };
  $('#btnIA').onclick = () => perguntar();
  $('#btnAta').onclick = () => perguntar('ata');
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

  async function perguntar(modo) {
    const q = modo === 'ata' ? 'Ata semanal do Comitê de PCP' : $('#perguntaIA').value.trim();
    if (!q || !window.PCP?.contextoIA) return;
    $('#btnIA').disabled = $('#btnAta').disabled = true; $('#btnIA').textContent = 'pensando…';
    const caixa = document.createElement('div');
    caixa.className = 'msgIA';
    caixa.innerHTML = `<div class="q">${esc(q)}</div><div class="a">…</div>`;
    $('#respostasIA').prepend(caixa);
    try {
      relatorio = relatorio || await (await fetch('data/copiloto.json')).json();
      const contexto = { sistema: window.PCP.contextoIA(), relatorio };
      const r = await fetch('api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pergunta: q, contexto, modo }) });
      const j = await r.json().catch(() => ({ erro: 'Copiloto indisponível neste endereço (a função /api/chat só roda na Vercel).' }));
      if (!r.ok || j.erro) throw new Error(j.erro || r.status);
      caixa.querySelector('.a').textContent = j.resposta;
      const v = verificar(j.resposta, contexto);
      caixa.insertAdjacentHTML('beforeend', v.faltando.length
        ? `<div class="verif bad">⚠ Número(s) não encontrado(s) nos dados do sistema: <b>${v.faltando.map(esc).join(' · ')}</b>. Não use sem conferir.</div>`
        : `<div class="verif ok">✔ ${v.total ? `Os ${v.total} números da resposta conferem com os dados do sistema.` : 'Resposta sem números para conferir.'}</div>`);
      caixa.insertAdjacentHTML('beforeend', `<div class="meta">Gerado por IA (${esc(j.modelo)}) com os números do sistema em ${window.PCP.fD(contexto.sistema.data)} · confira no Dashboard</div>`);
    } catch (e) {
      caixa.classList.add('erro');
      caixa.querySelector('.a').textContent = String(e.message || e);
    }
    $('#btnIA').disabled = $('#btnAta').disabled = false; $('#btnIA').textContent = 'Perguntar';
  }
})();
