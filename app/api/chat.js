/* Copiloto de IA · função serverless da Vercel (POST /api/chat)
   - A chave fica na variável de ambiente GEMINI_API_KEY da Vercel, nunca no repositório.
   - A IA não calcula: recebe os números já calculados pelo sistema e só responde com eles. */

const API = 'https://generativelanguage.googleapis.com/v1beta';

const REGRAS = `Você é o copiloto do Sistema de PCP do Grupo 3 (obra da packing house Vale Dourado Frutas, Juazeiro).
Responda perguntas da diretoria e dos professores sobre a obra usando SOMENTE os dados do bloco CONTEXTO.

Regras obrigatórias:
1. Use apenas números que aparecem no CONTEXTO, copiados como estão (pode arredondar e formatar em pt-BR). Nunca estime, extrapole nem faça contas: para comparar, cite os dois valores (ex.: "38,6% realizado contra 66,9% previsto") em vez de calcular a diferença. Cada número da resposta é conferido automaticamente com o CONTEXTO.
2. Se a resposta não estiver no CONTEXTO, diga exatamente: "Esse dado não está no sistema." e sugira em qual tela procurar (Dashboard, Análises, Lançamentos, Modelo 3D).
3. Diga sempre a data a que o número se refere: "sistema" = data selecionada no topo; "relatorio" = data de status 13/11/2026.
4. Seja curto: no máximo 5 frases ou 5 tópicos. Comece pela resposta direta.
5. Termine com uma linha "Fonte:" indicando o campo usado (ex.: relatorio.prazo, sistema.atividades A12).
6. Responda no idioma da pergunta.
7. Atraso de uma atividade: compare previsto_pct e real_pct em sistema.atividades (inclui atividades que nem começaram, com real 0%). relatorio.atrasos só lista atividades já iniciadas; use-o para dias de atraso. Ao falar de atividades críticas, considere as duas fontes.
8. Quando o mesmo indicador existir em "sistema" e em "relatorio", use o do sistema (data selecionada) e não misture os dois. sistema.equipamentos é por tipo (MUN, PTA…); relatorio.equip é por unidade (MUN-01, PTA-05).
9. Escreva datas no formato dd/mm/aaaa.
10. Perguntas de seguimento (ex.: "e para a A26?") referem-se às mensagens anteriores da conversa; responda com os dados do CONTEXTO.`;

const ATA = `MODO ATA: escreva a ata semanal do Comitê de PCP na data do sistema, em português, em tópicos curtos, com estes títulos:
1. Situação geral (prazo e custo: IDP, IDC, avanço real × previsto, término previsto e multa)
2. PPC da última semana e principais causas de não cumprimento
3. Atividades críticas atrasadas (previsto × realizado)
4. Suprimentos, equipamentos, qualidade e segurança (só o que tiver alerta)
5. Decisões a tomar pelo comitê (com base em relatorio.cenarios)
6. Responsáveis (encarregados e responsáveis que aparecem nos dados)
Na seção 1, IDP, IDC e avanço vêm só de sistema.evm (2 casas decimais); término e multa de relatorio.prazo. Na seção 3, liste só atividades críticas com previsto_pct maior que real_pct.
Até 25 linhas (substitui o limite de 5 frases da regra 4). Demais regras valem: nenhum número fora do CONTEXTO, nenhuma recomendação que não esteja apoiada nos dados.`;

let modeloCache = null;

// escolhe automaticamente um modelo "flash" disponível para a chave (rápido e com cota gratuita)
async function modelos(key) {
  if (process.env.GEMINI_MODEL) return [process.env.GEMINI_MODEL];
  if (modeloCache) return modeloCache;
  const r = await fetch(`${API}/models?pageSize=200`, { headers: { 'x-goog-api-key': key } });
  if (!r.ok) throw new Error('lista de modelos: ' + r.status);
  const nomes = (await r.json()).models
    .filter(m => (m.supportedGenerationMethods || []).includes('generateContent'))
    .map(m => m.name.replace('models/', ''))
    .filter(n => /flash/.test(n) && !/image|tts|audio|live|embed|vision|exp|preview/.test(n));
  const versao = n => +(n.match(/(\d+(\.\d+)?)/) || [0, 0])[1];
  nomes.sort((a, b) => /lite/.test(b) - /lite/.test(a) || versao(b) - versao(a) || a.length - b.length);
  modeloCache = [...nomes.slice(0, 4), 'gemini-flash-lite-latest', 'gemini-flash-latest'];
  return modeloCache;
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ erro: 'Use POST.' });
  const key = process.env.GEMINI_API_KEY;
  if (!key) return res.status(500).json({ erro: 'GEMINI_API_KEY não configurada na Vercel.' });

  const { pergunta, contexto, modo, historico } = req.body || {};
  if (!pergunta || String(pergunta).length > 500) return res.status(400).json({ erro: 'Pergunta vazia ou longa demais (máx. 500 caracteres).' });
  const ctx = JSON.stringify(contexto || {});
  if (ctx.length > 120000) return res.status(400).json({ erro: 'Contexto grande demais.' });

  const corpo = {
    systemInstruction: { parts: [{ text: REGRAS + (modo === 'ata' ? '\n\n' + ATA : '') + '\n\nCONTEXTO:\n' + ctx }] },
    contents: [
      // conversa anterior (até 4 trocas), para permitir perguntas de seguimento
      ...(Array.isArray(historico) && modo !== 'ata' ? historico.slice(-4) : []).flatMap(h => [
        { role: 'user', parts: [{ text: String(h.pergunta || '').slice(0, 500) }] },
        { role: 'model', parts: [{ text: String(h.resposta || '').slice(0, 3000) }] }]),
      { role: 'user', parts: [{ text: pergunta }] }],
    generationConfig: { temperature: 0, maxOutputTokens: modo === 'ata' ? 4000 : 2000 }
  };

  // Raciocínio interno no mínimo: a IA só lê números, e "pensar" deixava a resposta lenta (30 s a 2 min).
  // Cada geração de modelo aceita um formato; tenta do mais novo ao mais antigo.
  const PENSAR = [{ thinkingLevel: 'low' }, { thinkingBudget: 0 }, null];
  const chamar = (m, pensar) => fetch(`${API}/models/${m}:generateContent`, {
    method: 'POST', signal: AbortSignal.timeout(25000),
    headers: { 'Content-Type': 'application/json', 'x-goog-api-key': key },
    body: JSON.stringify({ ...corpo, generationConfig: { ...corpo.generationConfig, ...(pensar ? { thinkingConfig: pensar } : {}) } })
  });

  // tenta os modelos em ordem; sobrecarga (429/503) ou lentidão: tenta o próximo
  const erros = [], inicio = Date.now();
  try {
    for (const m of await modelos(key)) {
      if (Date.now() - inicio > 45000) break;
      for (const pensar of PENSAR) {
        let r, j;
        try { r = await chamar(m, pensar); j = await r.json().catch(() => ({})); }
        catch (e) { erros.push(`${m}: tempo esgotado`); break; }
        if (r.ok) {
          const texto = (j.candidates?.[0]?.content?.parts || []).filter(p => !p.thought).map(p => p.text || '').join('').trim();
          return res.status(200).json({ resposta: texto || 'Sem resposta do modelo.', modelo: m, segundos: Math.round((Date.now() - inicio) / 1000) });
        }
        const msg = j.error?.message || '';
        if (r.status === 400 && /think/i.test(msg)) continue;          // formato de raciocínio não aceito: tenta o próximo formato
        if (r.status === 401 || r.status === 403 || (r.status === 400 && /key/i.test(msg))) throw new Error('chave inválida: ' + msg.slice(0, 120));
        erros.push(`${m}: ${r.status}`); break;                          // sobrecarga, modelo inexistente etc.: próximo modelo
      }
    }
  } catch (e) { erros.push(String(e.message || e)); }
  const ultimoErro = erros.join('; ');
  return res.status(502).json({ erro: 'A IA não respondeu agora (' + ultimoErro.slice(0, 200) + '). O resto do sistema funciona normalmente.' });
};
