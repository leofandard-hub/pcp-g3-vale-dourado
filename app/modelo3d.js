// R12 · Modelo 3D do empreendimento (tabela 13 + avanço das atividades por zona, Anexo B)
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { CSS2DRenderer, CSS2DObject } from 'three/addons/renderers/CSS2DRenderer.js';

const el = document.getElementById('view3d'), info = document.getElementById('info3d');
const slider = document.getElementById('slider3d'), label = document.getElementById('label3d');
const glob = document.getElementById('global3d'), btnPlay = document.getElementById('play3d'), btnVista = document.getElementById('vista3d');
let renderer, labelRenderer, scene, camera, controls, group, meshes = [], ready = false, inited = false, datas = [], timer = null, vistaTopo = false;

const CINZA = new THREE.Color(0xc9ced6), LARANJA = new THREE.Color(0xf2a541), VERDE = new THREE.Color(0x2e9e5b);
const cor = p => p === undefined ? CINZA.clone() : p < 0.5 ? CINZA.clone().lerp(LARANJA, p / 0.5) : LARANJA.clone().lerp(VERDE, (p - 0.5) / 0.5);
const tipo = z => String(z.tipo_zona).toUpperCase();
const W = 205, L = 174.7, CX = W / 2, CZ = -L / 2; // terreno (m); y da planta → −z

function camera3d() { camera.position.set(-10, 112, 52); controls.target.set(CX, 0, CZ + 8); controls.update(); }
function cameraTopo() { camera.position.set(CX, 290, CZ + 0.01); controls.target.set(CX, 0, CZ); controls.update(); }

function init() {
  if (inited) return; inited = true;
  scene = new THREE.Scene(); scene.background = new THREE.Color(0xeef3f7);
  camera = new THREE.PerspectiveCamera(38, el.clientWidth / el.clientHeight, 1, 4000);
  renderer = new THREE.WebGLRenderer({ antialias: true }); renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(el.clientWidth, el.clientHeight); el.appendChild(renderer.domElement);
  labelRenderer = new CSS2DRenderer(); labelRenderer.setSize(el.clientWidth, el.clientHeight);
  labelRenderer.domElement.className = 'labels3d'; el.appendChild(labelRenderer.domElement);
  controls = new OrbitControls(camera, renderer.domElement); controls.maxPolarAngle = Math.PI / 2.05;
  camera3d();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8f99, 1.0));
  const sol = new THREE.DirectionalLight(0xffffff, 0.9); sol.position.set(-80, 200, 120); scene.add(sol);
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

function etiqueta(texto, p, atraso, x, y, z) {
  const d = document.createElement('div');
  d.className = 'lbl3d' + (atraso ? ' atraso' : '');
  d.innerHTML = `<b>${texto}</b>${p === undefined ? '' : ' ' + Math.round(p * 100) + '%'}`;
  const o = new CSS2DObject(d); o.position.set(x, y, z); group.add(o);
}

function caixa(w, h, l, mat, x, y, z) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, l), mat); m.position.set(x, y, z); group.add(m); return m;
}
function arestas(w, h, l, cor, x, y, z, op = 1) {
  const e = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, l)), new THREE.LineBasicMaterial({ color: cor, transparent: op < 1, opacity: op }));
  e.position.set(x, y, z); group.add(e); return e;
}

function build() {
  if (!ready) return;
  init();
  const P = window.PCP, data = datas[Math.round(slider.value / 1000 * (datas.length - 1))];
  label.textContent = P.fD(data);
  const c = P.calc(data), Z = avancoZonas(c);
  glob.textContent = 'avanço global ' + P.fP(c.VA / c.BAC) + ' · previsto ' + P.fP(c.VP / c.BAC);
  group.clear(); meshes = [];
  for (const z of P.zonas()) {
    const zz = Z[z.id_zona], p = zz?.p, atraso = zz?.atraso && p < 0.999;
    const w = z.largura_x_m, l = z.comprimento_y_m, cx = z.x_m + w / 2, cz = -(z.y_m + l / 2);
    const ud = { id: z.id_zona, nome: z.nome_zona, p, ativ: zz?.ativ, atraso };
    const t = tipo(z);
    let alvo;
    if (t === 'TERRENO') {
      alvo = caixa(w, 0.4, l, new THREE.MeshLambertMaterial({ color: 0xe4dcc8 }), cx, -0.2, cz);
      alvo.userData = ud; meshes.push(alvo);
      etiqueta('Terreno', p, atraso, z.x_m + 14, 1, -(z.y_m + z.comprimento_y_m - 6));
      continue;
    }
    if (t === 'EDIFICACAO') {
      // envoltória prevista em fio de arame + volume construído que sobe com o avanço
      arestas(w, z.altura_m, l, 0x4a5263, cx, z.altura_m / 2, cz, 0.55);
      const h = Math.max(0.2, z.altura_m * (p ?? 0));
      alvo = caixa(w, h, l, new THREE.MeshLambertMaterial({ color: cor(p), transparent: true, opacity: 0.18, depthWrite: false }), cx, h / 2, cz);
      if (atraso) arestas(w, h, l, 0xc0392b, cx, h / 2, cz);
      alvo.userData = ud; meshes.push(alvo);
      etiqueta('Galpão (estrutura)', p, atraso, cx, z.altura_m + 4, cz - l / 2);
      continue;
    }
    // zonas de processo, pátio, docas, apoio, utilidades, canteiro
    const plano = t === 'PATIO' || z.altura_m < 1.5;
    const hMax = plano ? Math.max(z.altura_m, 0.4) : z.altura_m;
    const h = p === undefined ? 0.3 : Math.max(0.3, hMax * Math.max(p, 0.04));
    const mat = new THREE.MeshLambertMaterial({ color: cor(p), transparent: !p, opacity: p ? 1 : 0.55 });
    alvo = caixa(w - 0.8, h, l - 0.8, mat, cx, h / 2 + 0.02, cz);
    if (!plano) arestas(w - 0.8, z.altura_m, l - 0.8, 0x9aa3b0, cx, z.altura_m / 2, cz, 0.45);
    arestas(w - 0.8, h, l - 0.8, atraso ? 0xc0392b : 0x5b6472, cx, h / 2 + 0.02, cz, atraso ? 1 : 0.6);
    alvo.userData = ud; meshes.push(alvo);
    etiqueta(z.id_zona, p, atraso, cx, (plano ? hMax : z.altura_m) + 1.5, cz);
  }
}

function setData(data) {
  const i = datas.indexOf(data); if (i >= 0) slider.value = Math.round(i / (datas.length - 1) * 1000);
}
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
