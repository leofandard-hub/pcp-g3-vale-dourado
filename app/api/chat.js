/* Copiloto de IA · função serverless da Vercel (POST /api/chat)
   - A chave fica na variável de ambiente GEMINI_API_KEY da Vercel, nunca no repositório.
   - A IA não calcula: recebe os números já calculados pelo sistema e só responde com eles. */

const API = 'https://generativelanguage.googleapis.com/v1beta';

const REGRAS = `Você é o copiloto do Sistema de PCP do Grupo 3 (obra da packing house Vale Dourado Frutas, Juazeiro).
Responda perguntas da diretoria e dos professores sobre a obra usando SOMENTE os dados do bloco CONTEXTO.

Regras obrigatórias:
1. Use apenas números que aparecem no CONTEXTO, copiados como estão (pode arredondar e formatar em pt-BR). Nunca estime, extrapole nem faça contas novas além de somar ou comparar dois valores do CONTEXTO.
2. Se a resposta não estiver no CONTEXTO, diga exatamente: "Esse dado não está no sistema." e sugira em qual tela procurar (Dashboard, Análises, Lançamentos, Modelo 3D).
3. Diga sempre a data a que o número se refere: "sistema" = data selecionada no topo; "relatorio" = data de status 13/11/2026.
4. Seja curto: no máximo 5 frases ou 5 tópicos. Comece pela resposta direta.
5. Termine com uma linha "Fonte:" indicando o campo usado (ex.: relatorio.prazo, sistema.atividades A12).
6. Responda no idioma da pergunta.`;

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
  nomes.sort((a, b) => versao(b) - versao(a) || a.length - b.length);
  modeloCache = [...nomes.slice(0, 4), 'gemini-flash-latest'];
  return modeloCache;
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ erro: 'Use POST.' });
  const key = process.env.GEMINI_API_KEY;
  if (!key) return res.status(500).json({ erro: 'GEMINI_API_KEY não configurada na Vercel.' });

  const { pergunta, contexto } = req.body || {};
  if (!pergunta || String(pergunta).length > 500) return res.status(400).json({ erro: 'Pergunta vazia ou longa demais (máx. 500 caracteres).' });
  const ctx = JSON.stringify(contexto || {});
  if (ctx.length > 120000) return res.status(400).json({ erro: 'Contexto grande demais.' });

  const corpo = {
    systemInstruction: { parts: [{ text: REGRAS }] },
    contents: [{ role: 'user', parts: [{ text: `CONTEXTO:\n${ctx}\n\nPERGUNTA: ${pergunta}` }] }],
    generationConfig: { temperature: 0, maxOutputTokens: 2000 }
  };

  // tenta os modelos em ordem; se um estiver sobrecarregado (429/503), espera um pouco e tenta de novo
  const erros = [], inicio = Date.now(), espera = ms => new Promise(r => setTimeout(r, ms));
  try {
    for (const m of await modelos(key)) {
      for (let tentativa = 0; tentativa < 2 && Date.now() - inicio < 40000; tentativa++) {
        const r = await fetch(`${API}/models/${m}:generateContent`, {
          method: 'POST', headers: { 'Content-Type': 'application/json', 'x-goog-api-key': key }, body: JSON.stringify(corpo)
        });
        const j = await r.json().catch(() => ({}));
        if (r.ok) {
          const texto = (j.candidates?.[0]?.content?.parts || []).filter(p => !p.thought).map(p => p.text || '').join('').trim();
          return res.status(200).json({ resposta: texto || 'Sem resposta do modelo.', modelo: m });
        }
        erros.push(`${m}: ${r.status}`);
        if (r.status === 400 || r.status === 401 || r.status === 403) throw new Error((j.error?.message || 'chave ou pedido inválido').slice(0, 150));
        if (r.status !== 429 && r.status !== 503) break; // outro erro: passa para o próximo modelo
        await espera(1500);
      }
    }
  } catch (e) { erros.push(String(e.message || e)); }
  const ultimoErro = erros.join('; ');
  return res.status(502).json({ erro: 'A IA não respondeu agora (' + ultimoErro.slice(0, 200) + '). O resto do sistema funciona normalmente.' });
};
