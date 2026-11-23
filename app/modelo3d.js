import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const el = document.getElementById('view3d'), info = document.getElementById('info3d');
const slider = document.getElementById('slider3d'), label = document.getElementById('label3d');
let renderer, scene, camera, controls, group, meshes = [], ready = false, inited = false, datas = [];
const COR = { nao: 0xc9ced6, and: 0xf2b134, ok: 0x2e9e5b, atraso: 0xc0392b };

function init() {
  if (inited) return; inited = true;
  scene = new THREE.Scene(); scene.background = new THREE.Color(0xeef1f4);
  camera = new THREE.PerspectiveCamera(40, el.clientWidth / el.clientHeight, 1, 3000);
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(el.clientWidth, el.clientHeight); el.appendChild(renderer.domElement);
  controls = new OrbitControls(camera, renderer.domElement);
  camera.position.set(102, 120, 95); controls.target.set(102, 0, -95);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x777777, 1.1));
  const sun = new THREE.DirectionalLight(0xffffff, 0.8); sun.position.set(150, 250, 100); scene.add(sun);
  group = new THREE.Group(); scene.add(group);
  window.addEventListener('resize', () => { camera.aspect = el.clientWidth / el.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(el.clientWidth, el.clientHeight); });
  const ray = new THREE.Raycaster(), m = new THREE.Vector2();
  renderer.domElement.addEventListener('click', e => {
    const r = renderer.domElement.getBoundingClientRect();
    m.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
    ray.setFromCamera(m, camera);
    const hit = ray.intersectObjects(meshes)[0];
    if (hit) mostrar(hit.object.userData);
  });
  (function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); })();
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
  info.innerHTML = `<b>${u.id} · ${u.nome}</b><br>Avanço da zona: <b>${u.p === undefined ? 'sem atividades' : P.fP(u.p)}</b>` +
    (u.ativ?.length ? '<table>' + u.ativ.map(a => `<tr><td>${a.id_atividade}${a.b.critica ? ' ★' : ''}</td><td>${a.nome_atividade.slice(0, 30)}</td><td>${P.fP(a.pReal)}</td><td class="hint">prev ${P.fP(a.pPlan)}</td></tr>`).join('') + '</table><span class="hint">★ caminho crítico</span>' : '');
}

function build() {
  if (!ready) return;
  init();
  const P = window.PCP, data = datas[Math.round(slider.value / 1000 * (datas.length - 1))];
  label.textContent = P.fD(data);
  const c = P.calc(data), Z = avancoZonas(c);
  group.clear(); meshes = [];
  for (const z of P.zonas()) {
    const zz = Z[z.id_zona], p = zz ? zz.p : undefined;
    const cor = zz?.atraso && p < 1 ? COR.atraso : p === undefined ? COR.nao : p >= 0.999 ? COR.ok : p > 0 ? COR.and : COR.nao;
    const W = z.largura_x_m, L = z.comprimento_y_m;
    const cx = z.x_m + W / 2, cz = -(z.y_m + L / 2); // y da planta → -z do three.js (norte para o fundo)
    let mesh;
    if (z.tipo_zona === 'Terreno') {
      mesh = new THREE.Mesh(new THREE.BoxGeometry(W, 0.4, L), new THREE.MeshLambertMaterial({ color: 0xd9cfb8 }));
      mesh.position.set(cx, -0.2, cz);
    } else if (z.id_zona === 'GALPAO') {
      const h = Math.max(0.3, z.altura_m * (p ?? 0));
      mesh = new THREE.Mesh(new THREE.BoxGeometry(W, h, L), new THREE.MeshLambertMaterial({ color: cor, transparent: true, opacity: 0.25, depthWrite: false }));
      mesh.position.set(cx, h / 2, cz);
      const ed = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(W, z.altura_m, L)), new THREE.LineBasicMaterial({ color: 0x4a5263 }));
      ed.position.set(cx, z.altura_m / 2, cz); group.add(ed);
    } else {
      const h = Math.max(0.15, z.altura_m * (p === undefined ? 0.05 : Math.max(p, 0.02)));
      mesh = new THREE.Mesh(new THREE.BoxGeometry(W - 0.6, h, L - 0.6), new THREE.MeshLambertMaterial({ color: cor, transparent: p === undefined || p === 0, opacity: (p === undefined || p === 0) ? 0.45 : 1 }));
      mesh.position.set(cx, h / 2 + 0.05, cz);
      const ed = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(W - 0.6, z.altura_m, L - 0.6)), new THREE.LineBasicMaterial({ color: 0x8a93a3, transparent: true, opacity: 0.5 }));
      ed.position.set(cx, z.altura_m / 2, cz); group.add(ed);
    }
    mesh.userData = { id: z.id_zona, nome: z.nome_zona, p, ativ: zz?.ativ };
    group.add(mesh); meshes.push(mesh);
  }
}

function onReady() { if (ready) return; datas = window.PCP.datas(); ready = true; syncSlider(); if (document.getElementById('modelo').classList.contains('active')) build(); }
window.addEventListener('pcp:ready', onReady);
if (window.PCP?.ready) onReady();
function syncSlider() { const i = datas.indexOf(window.PCP.D()); if (i >= 0) slider.value = Math.round(i / (datas.length - 1) * 1000); }
window.addEventListener('pcp:data', () => { syncSlider(); if (inited) build(); });
window.addEventListener('pcp:show3d', () => requestAnimationFrame(() => { build(); if (renderer) { camera.aspect = el.clientWidth / el.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(el.clientWidth, el.clientHeight); } }));
slider.oninput = build;
