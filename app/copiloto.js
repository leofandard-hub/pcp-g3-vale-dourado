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
  $('#btnIA').onclick = perguntar;
  $('#perguntaIA').onkeydown = e => { if (e.key === 'Enter') perguntar(); };

  async function perguntar() {
    const q = $('#perguntaIA').value.trim();
    if (!q || !window.PCP?.contextoIA) return;
    $('#btnIA').disabled = true; $('#btnIA').textContent = 'pensando…';
    const caixa = document.createElement('div');
    caixa.className = 'msgIA';
    caixa.innerHTML = `<div class="q">${esc(q)}</div><div class="a">…</div>`;
    $('#respostasIA').prepend(caixa);
    try {
      relatorio = relatorio || await (await fetch('data/copiloto.json')).json();
      const contexto = { sistema: window.PCP.contextoIA(), relatorio };
      const r = await fetch('api/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ pergunta: q, contexto }) });
      const j = await r.json().catch(() => ({ erro: 'Copiloto indisponível neste endereço (a função /api/chat só roda na Vercel).' }));
      if (!r.ok || j.erro) throw new Error(j.erro || r.status);
      caixa.querySelector('.a').textContent = j.resposta;
      caixa.insertAdjacentHTML('beforeend', `<div class="meta">Gerado por IA (${esc(j.modelo)}) com os números do sistema em ${window.PCP.fD(contexto.sistema.data)} · confira no Dashboard</div>`);
    } catch (e) {
      caixa.classList.add('erro');
      caixa.querySelector('.a').textContent = String(e.message || e);
    }
    $('#btnIA').disabled = false; $('#btnIA').textContent = 'Perguntar';
  }
})();
