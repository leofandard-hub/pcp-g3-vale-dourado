// R12 · Modelo 3D do empreendimento
// Zonas = tabela 13. Avanço da zona = média das atividades da zona ponderada pelo custo orçado (Anexo B).
// O galpão é montado peça por peça pelo avanço real de cada atividade: A08 fundações, A09 estrutura,
// A10 cobertura, A11 fechamento lateral, A12 piso.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

const el = document.getElementById('view3d'), info = document.getElementById('info3d');
const slider = document.getElementById('slider3d'), label = document.getElementById('label3d');
const glob = document.getElementById('global3d'), btnPlay = document.getElementById('play3d'), btnVista = document.getElementById('vista3d');
let renderer, labelRenderer, scene, camera, controls, group, meshes = [], ready = false, inited = false, datas = [], timer = null, vistaTopo = false;

// 5 classes de avanço, cores bem distintas
const CLASSES = [[0.34, 0xe67e22], [0.67, 0xf4c430], [0.999, 0x8bc34a], [Infinity, 0x1e8449]];
const corClasse = p => (p === undefined || p <= 0) ? 0xd5d9df : CLASSES.find(([lim]) => p < lim)[1];
const tipo = z => String(z.tipo_zona).toUpperCase();
const W = 205, L = 174.7, CX = W / 2, CZ = -L / 2;   // terreno (m); y da planta → −z do three.js
const mats = {};
const mat = (cor, op = 1) => mats[cor + '_' + op] = mats[cor + '_' + op] ||
  new THREE.MeshLambertMaterial({ color: cor, transparent: op < 1, opacity: op, depthWrite: op === 1, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });

function camera3d() { camera.position.set(-10, 112, 52); controls.target.set(CX, 0, CZ + 8); controls.update(); }
function cameraTopo() { camera.position.set(CX, 290, CZ + 0.01); controls.target.set(CX, 0, CZ); controls.update(); }

function init() {
  if (inited) return; inited = true;
  scene = new THREE.Scene(); scene.background = new THREE.Color(0xf3f6f9);
  camera = new THREE.PerspectiveCamera(38, el.clientWidth / el.clientHeight, 1, 4000);
  renderer = new THREE.WebGLRenderer({ antialias: true, logarithmicDepthBuffer: true }); renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(el.clientWidth, el.clientHeight); el.appendChild(renderer.domElement);
  labelRenderer = new CSS2DRenderer(); labelRenderer.setSize(el.clientWidth, el.clientHeight);
  labelRenderer.domElement.className = 'labels3d'; el.appendChild(labelRenderer.domElement);
  controls = new OrbitControls(camera, renderer.domElement); controls.maxPolarAngle = Math.PI / 2.05;
  camera3d();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x9aa0aa, 0.9));
  const sol = new THREE.DirectionalLight(0xffffff, 1.0); sol.position.set(-90, 200, 140); scene.add(sol);
  const contra = new THREE.DirectionalLight(0xffffff, 0.35); contra.position.set(200, 120, -200); scene.add(contra);
  group = new THREE.Group(); scene.add(group);
  new ResizeObserver(() => {
    const w = el.clientWidth, h = el.clientHeight; if (!w || !h) return;
    camera.aspect = w / h; camera.updateProjectionMatrix(); renderer.setSize(w, h); labelRenderer.setSize(w, h);
  }).observe(el);
  const ray = new THREE.Raycaster(), m = new THREE.Vector2();
  renderer.domElement.addEventListener('click', e => {
    const r = renderer.domElement.getBoundingClientRect();
    m.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(m, camera);
    const hit = ray.intersectObjects(meshes)[0];
    if (hit) mostrar(hit.object.userData);
  });
  (function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); labelRenderer.render(scene, camera); })();
}

// ---------- primitivas (coordenadas da planta: x, y, base, largura, comprimento, altura) ----------
function caixa(x, y, base, w, l, h, cor, ud, op = 1) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, l), mat(cor, op));
  m.position.set(x + w / 2, base + h / 2, -(y + l / 2)); group.add(m);
  if (ud) { m.userData = ud; meshes.push(m); }
  return m;
}
function arame(x, y, base, w, l, h, cor = 0x7b8594, op = 0.55) {
  const e = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, l)), new THREE.LineBasicMaterial({ color: cor, transparent: true, opacity: op }));
  e.position.set(x + w / 2, base + h / 2, -(y + l / 2)); group.add(e);
}
function moldura(x, y, w, l, cor = 0xc0392b, t = 0.9) {   // contorno no chão (crítica atrasada)
  caixa(x - t, y - t, 0, w + 2 * t, t, 0.5, cor); caixa(x - t, y + l, 0, w + 2 * t, t, 0.5, cor);
  caixa(x - t, y, 0, t, l, 0.5, cor); caixa(x + w, y, 0, t, l, 0.5, cor);
}
function etiqueta(texto, p, atraso, x, y, alt) {
  const d = document.createElement('div');
  d.className = 'lbl3d' + (atraso ? ' atraso' : '');
  d.innerHTML = `<b>${texto}</b>${p === undefined ? '' : ' ' + Math.round(p * 100) + '%'}`;
  const o = new CSS2DObject(d); o.position.set(x, alt, -y); group.add(o);
}
const N = (p, n) => Math.round(Math.max(0, Math.min(1, p || 0)) * n);

// ---------- galpão montado pelas atividades ----------
function galpao(z, pa, ud) {
  const x0 = z.x_m, y0 = z.y_m, w = z.largura_x_m, l = z.comprimento_y_m, H = z.altura_m;
  arame(x0, y0, 0, w, l, H, 0x4a5263, 0.45);                                   // volume previsto
  const nP = 24;                                                                // A12 piso: faixas ao longo de x
  for (let i = 0; i < N(pa.A12, nP); i++) caixa(x0 + i * w / nP, y0, 0, w / nP, l, 0.15, 0xaeb5bf, ud);
  const xs = Array.from({ length: 11 }, (_, i) => x0 + i * w / 10), ys = [y0, y0 + l / 2, y0 + l];
  const pilares = xs.flatMap(x => ys.map(y => [x, y]));
  pilares.slice(0, N(pa.A08, pilares.length)).forEach(([x, y]) => caixa(x - 0.9, y - 0.9, 0, 1.8, 1.8, 0.5, 0x8d8d8d, ud));   // A08
  const hC = H * Math.min(1, pa.A09 || 0);                                                                                 // A09
  if (hC > 0) pilares.forEach(([x, y]) => caixa(x - 0.3, y - 0.3, 0.5, 0.6, 0.6, hC, 0x3f5a78, ud));
  if ((pa.A09 || 0) >= 0.999) {                                                 // vigas de cobertura
    xs.forEach(x => caixa(x - 0.25, y0, H, 0.5, l, 0.5, 0x3f5a78, ud));
    caixa(x0, y0 - 0.25, H, w, 0.5, 0.5, 0x3f5a78, ud); caixa(x0, y0 + l - 0.25, H, w, 0.5, 0.5, 0x3f5a78, ud);
  }
  const nR = 20;                                                                // A10 cobertura: placas ao longo de x
  for (let i = 0; i < N(pa.A10, nR); i++) caixa(x0 + i * w / nR + 0.15, y0, H + 0.5, w / nR - 0.3, l, 0.2, 0x9fb7cf, ud, 0.55);
  const lados = [];                                                             // A11 fechamento: painéis no perímetro
  for (let x = x0; x < x0 + w - 0.1; x += 7.5) lados.push([x, y0 - 0.15, 7.4, 0.3]);
  for (let y = y0; y < y0 + l - 0.1; y += 7.5) lados.push([x0 + w - 0.15, y, 0.3, 7.4]);
  for (let x = x0 + w - 7.5; x > x0 - 0.1; x -= 7.5) lados.push([x, y0 + l - 0.15, 7.4, 0.3]);
  for (let y = y0 + l - 7.5; y > y0 - 0.1; y -= 7.5) lados.push([x0 - 0.15, y, 0.3, 7.4]);
  lados.slice(0, N(pa.A11, lados.length)).forEach(([x, y, a, b]) => caixa(x, y, 0.5, a, b, H - 0.5, 0xdfe4ea, ud, 0.45));
}

function avancoZonas(c) {
  const z = {};
  c.at.forEach(a => {
    if (!a.id_zona) return;
    const x = z[a.id_zona] = z[a.id_zona] || { s: 0, w: 0, ativ: [], atraso: false };
    x.s += a.O * a.pReal; x.w += a.O; x.ativ.push(a);
    if (a.b.critica && a.pPlan - a.pReal > 0.05) x.atraso = true;
  });
  for (const k in z) z[k].p = z[k].s / z[k].w;
  return z;
}

function mostrar(u) {
  const P = window.PCP;
  info.classList.remove('hidden');
  info.innerHTML = `<button class="fechar" title="fechar">×</button><b>${u.id} · ${u.nome}</b><br>Avanço da zona: <b>${u.p === undefined ? 'sem atividades' : P.fP(u.p)}</b>` +
    (u.atraso ? '<br><span class="tag">crítica atrasada</span>' : '') +
    (u.ativ?.length ? '<table>' + u.ativ.map(a => `<tr><td>${a.id_atividade}${a.b.critica ? ' ★' : ''}</td><td>${a.nome_atividade.slice(0, 28)}</td><td><b>${P.fP(a.pReal)}</b></td><td class="hint">prev. ${P.fP(a.pPlan)}</td></tr>`).join('') + '</table><span class="hint">★ caminho crítico</span>' : '');
  info.querySelector('.fechar').onclick = () => info.classList.add('hidden');
}

function build() {
  if (!ready) return;
  init();
  const P = window.PCP, data = datas[Math.round(slider.value / 1000 * (datas.length - 1))];
  label.textContent = P.fD(data);
  const c = P.calc(data), Z = avancoZonas(c);
  const pa = Object.fromEntries(c.at.map(a => [a.id_atividade, a.pReal]));
  glob.textContent = 'avanço global ' + P.fP(c.VA / c.BAC) + ' · previsto ' + P.fP(c.VP / c.BAC);
  group.clear(); meshes = [];
  for (const z of P.zonas()) {
    const zz = Z[z.id_zona], p = zz?.p, atraso = !!(zz?.atraso && p < 0.999);
    const x = z.x_m, y = z.y_m, w = z.largura_x_m, l = z.comprimento_y_m, H = z.altura_m, t = tipo(z);
    const ud = { id: z.id_zona, nome: z.nome_zona, p, ativ: zz?.ativ, atraso };
    if (t === 'TERRENO') {
      caixa(x, y, -0.4, w, l, 0.4, (p ?? 0) >= 0.999 ? 0xe6e9e1 : 0xd8c9a8, ud);   // terraplenagem
      etiqueta('Terreno', p, atraso, x + 14, y + l - 6, 1);
      continue;
    }
    if (t === 'EDIFICACAO') {
      galpao(z, pa, ud);
      if (atraso) moldura(x, y, w, l);
      etiqueta('Galpão', p, atraso, x + w / 2, y + l, H + 4);
      continue;
    }
    const plano = H < 1.5;
    const base = String(z.id_zona_pai || '').toUpperCase() === 'GALPAO' ? 0.16 : 0;
    const m = 0.6;   // folga entre zonas vizinhas
    if (plano) {     // pátio, docas: fração executada ocupa parte da área
      caixa(x + m, y + m, base, w - 2 * m, l - 2 * m, 0.08, 0xcfc4ae, ud);
      const f = Math.max(0, Math.min(1, p || 0));
      if (f > 0) caixa(x + m, y + m, base + 0.08, (w - 2 * m) * f, l - 2 * m, Math.max(H, 0.3), corClasse(p), ud);
    } else {         // edificações e zonas de processo: enchem até a altura proporcional ao avanço
      arame(x + m, y + m, base, w - 2 * m, l - 2 * m, H, 0x7b8594, 0.5);
      caixa(x + m, y + m, base, w - 2 * m, l - 2 * m, 0.12, 0xd5d9df, ud);
      const h = H * Math.max(0, Math.min(1, p || 0));
      if (h > 0.05) caixa(x + m, y + m, base + 0.12, w - 2 * m, l - 2 * m, h, corClasse(p), ud);
    }
    if (atraso) moldura(x + m, y + m, w - 2 * m, l - 2 * m);
    etiqueta(z.id_zona, p, atraso, x + w / 2, y + l / 2, (plano ? 1 : H) + base + 1.5);
  }
}

function setData(data) { const i = datas.indexOf(data); if (i >= 0) slider.value = Math.round(i / (datas.length - 1) * 1000); }
function onReady() {
  if (ready) return; datas = window.PCP.datas(); ready = true; setData(window.PCP.D());
  if (document.getElementById('modelo').classList.contains('active')) build();
}
window.addEventListener('pcp:ready', onReady);
if (window.PCP?.ready) onReady();
window.addEventListener('pcp:data', () => { setData(window.PCP.D()); if (inited) build(); });
window.addEventListener('pcp:show3d', () => requestAnimationFrame(build));
slider.oninput = () => { stop(); build(); };

function stop() { clearInterval(timer); timer = null; btnPlay.textContent = '▶ animar'; }
btnPlay.onclick = () => {
  if (timer) return stop();
  if (+slider.value >= 1000) slider.value = 0;
  btnPlay.textContent = '❚❚ pausar';
  timer = setInterval(() => { slider.value = Math.min(1000, +slider.value + 8); build(); if (+slider.value >= 1000) stop(); }, 120);
};
btnVista.onclick = () => { init(); vistaTopo = !vistaTopo; vistaTopo ? cameraTopo() : camera3d(); btnVista.textContent = vistaTopo ? 'Vista 3D' : 'Vista de cima'; };
document.getElementById('hoje3d').onclick = () => { stop(); setData(window.PCP.D()); build(); };
