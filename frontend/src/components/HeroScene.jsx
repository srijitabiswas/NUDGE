import { useEffect, useRef } from "react";
import * as THREE from "three";

// Warm 3D desk scene for the landing hero.
// `progress.current.value` (0..1) is the hero's scroll progress: the camera
// pushes toward the laptop and the floating messages collapse into its screen.
const smooth = (t) => t * t * (3 - 2 * t);

function makeScreenTexture() {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 320;
  const g = c.getContext("2d");
  g.fillStyle = "#2b2118";
  g.fillRect(0, 0, 512, 320);
  g.fillStyle = "#3a2d22";
  g.fillRect(0, 0, 512, 44);
  g.fillStyle = "#faf7f2";
  g.font = "700 22px Georgia, serif";
  g.fillText("NUDGE", 20, 30);
  const rows = [
    ["#e0a58b", 300],
    ["#c9b79c", 240],
    ["#8fb39a", 270],
    ["#c9b79c", 200],
  ];
  rows.forEach(([col, w], i) => {
    const y = 74 + i * 56;
    g.fillStyle = "#3a2d22";
    g.fillRect(20, y, 472, 44);
    g.fillStyle = col;
    g.beginPath();
    g.arc(44, y + 22, 8, 0, Math.PI * 2);
    g.fill();
    g.fillStyle = "#f5efe6";
    g.fillRect(66, y + 12, w, 8);
    g.fillStyle = "#cdbfae";
    g.fillRect(66, y + 27, w * 0.55, 6);
  });
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function box(w, h, d, color, rough = 0.6, metal = 0) {
  const m = new THREE.Mesh(
    new THREE.BoxGeometry(w, h, d),
    new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: metal })
  );
  return m;
}

export default function HeroScene({ progress, onFail }) {
  const host = useRef(null);

  useEffect(() => {
    const el = host.current;
    if (!el) return undefined;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let renderer;
    try {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "high-performance" });
    } catch {
      onFail?.();
      return undefined;
    }
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.domElement.style.cssText = "position:absolute;inset:0;width:100%;height:100%;display:block";
    el.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    scene.fog = new THREE.Fog(0x1b140e, 9, 22);
    const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 60);

    // lights
    scene.add(new THREE.AmbientLight(0xf5efe6, 0.55));
    const key = new THREE.DirectionalLight(0xfff1dc, 0.7);
    key.position.set(2, 5, 4);
    scene.add(key);
    const lampLight = new THREE.PointLight(0xffb877, 14, 9, 2);
    lampLight.position.set(2.2, 1.5, 0.2);
    scene.add(lampLight);
    const screenLight = new THREE.PointLight(0xe9dcc6, 3, 4, 2);
    screenLight.position.set(-0.4, 0.9, 0.8);
    scene.add(screenLight);

    // desk
    const desk = box(10, 0.12, 4.4, 0x4a3626, 0.45, 0.1);
    desk.position.set(0, -0.06, 0.4);
    scene.add(desk);

    // laptop
    const laptop = new THREE.Group();
    laptop.position.set(-0.6, 0, 0.3);
    laptop.rotation.y = 0.18;
    const base = box(1.9, 0.06, 1.25, 0x5a4a3c, 0.35, 0.5);
    base.position.y = 0.03;
    laptop.add(base);
    const hinge = new THREE.Group();
    hinge.position.set(0, 0.06, -0.6);
    hinge.rotation.x = -0.22;
    const lid = box(1.9, 1.2, 0.04, 0x5a4a3c, 0.35, 0.5);
    lid.position.y = 0.6;
    hinge.add(lid);
    const screenTex = makeScreenTexture();
    const screen = new THREE.Mesh(
      new THREE.PlaneGeometry(1.76, 1.08),
      new THREE.MeshBasicMaterial({ map: screenTex, toneMapped: false })
    );
    screen.position.set(0, 0.6, 0.025);
    hinge.add(screen);
    laptop.add(hinge);
    scene.add(laptop);

    // lamp
    const lamp = new THREE.Group();
    lamp.position.set(2.6, 0, 0);
    const lampBase = new THREE.Mesh(
      new THREE.CylinderGeometry(0.28, 0.32, 0.06, 28),
      new THREE.MeshStandardMaterial({ color: 0x2b2118, metalness: 0.6, roughness: 0.4 })
    );
    lampBase.position.y = 0.03;
    lamp.add(lampBase);
    const arm = new THREE.Mesh(
      new THREE.CylinderGeometry(0.025, 0.025, 1.6, 10),
      new THREE.MeshStandardMaterial({ color: 0xc9b79c, metalness: 0.7, roughness: 0.3 })
    );
    arm.position.set(-0.2, 0.8, 0);
    arm.rotation.z = 0.28;
    lamp.add(arm);
    const shade = new THREE.Mesh(
      new THREE.ConeGeometry(0.4, 0.5, 28, 1, true),
      new THREE.MeshStandardMaterial({
        color: 0xc9b79c, metalness: 0.4, roughness: 0.4, side: THREE.DoubleSide,
        emissive: 0xffb877, emissiveIntensity: 0.35,
      })
    );
    shade.position.set(-0.5, 1.55, 0);
    shade.rotation.z = 0.55;
    lamp.add(shade);
    scene.add(lamp);

    // books and mug
    const books = new THREE.Group();
    books.position.set(-3.1, 0, 0.9);
    [[1.3, 0x6b4f3a], [1.2, 0xc9b79c], [1.35, 0x82664f]].forEach(([w, col], i) => {
      const b = box(w, 0.16, 0.95, col, 0.7);
      b.position.set(i === 1 ? 0.08 : 0, 0.08 + i * 0.16, 0);
      b.rotation.y = (i - 1) * 0.07;
      books.add(b);
    });
    scene.add(books);
    const mug = new THREE.Group();
    mug.position.set(1.1, 0, 1.2);
    const cup = new THREE.Mesh(
      new THREE.CylinderGeometry(0.22, 0.19, 0.4, 24),
      new THREE.MeshStandardMaterial({ color: 0xfaf7f2, roughness: 0.35 })
    );
    cup.position.y = 0.2;
    mug.add(cup);
    const handle = new THREE.Mesh(
      new THREE.TorusGeometry(0.11, 0.028, 8, 18, Math.PI),
      new THREE.MeshStandardMaterial({ color: 0xfaf7f2, roughness: 0.35 })
    );
    handle.position.set(0.24, 0.2, 0);
    handle.rotation.z = -Math.PI / 2;
    mug.add(handle);
    scene.add(mug);

    // floating "messages" that collapse into the screen as you scroll
    const bubbleMat = (col) => new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.42, side: THREE.DoubleSide });
    const cols = [0xc9b79c, 0xfaf7f2, 0xe0a58b, 0x8fb39a, 0xcdbfae];
    const bubbles = Array.from({ length: 16 }, (_, i) => {
      const w = 0.5 + (i % 3) * 0.18;
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(w, 0.3), bubbleMat(cols[i % cols.length]));
      scene.add(mesh);
      return {
        mesh,
        r: 3.3 + (i % 5) * 0.55,
        a: (i / 16) * Math.PI * 2,
        s: 0.08 + (i % 4) * 0.03,
        h: 0.45 + (i % 6) * 0.2,
        ph: i * 1.7,
      };
    });
    const target = new THREE.Vector3(-0.6, 0.66, 0.0);

    // dust
    const N = 220;
    const pos = new Float32Array(N * 3);
    for (let i = 0; i < N; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 12;
      pos[i * 3 + 1] = Math.random() * 5;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 8;
    }
    const dustGeo = new THREE.BufferGeometry();
    dustGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const dust = new THREE.Points(
      dustGeo,
      new THREE.PointsMaterial({ color: 0xe9dcc6, size: 0.035, transparent: true, opacity: 0.55, depthWrite: false })
    );
    scene.add(dust);

    // camera rig
    const mouse = { x: 0, y: 0, sx: 0, sy: 0 };
    const onMove = (e) => {
      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = (e.clientY / window.innerHeight) * 2 - 1;
    };
    window.addEventListener("pointermove", onMove, { passive: true });

    const look = new THREE.Vector3();
    const tmp = new THREE.Vector3();
    function resize() {
      const w = el.clientWidth || 1;
      const h = el.clientHeight || 1;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(el);

    let visible = true;
    const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; });
    io.observe(el);

    const clock = new THREE.Clock();
    let raf = 0;
    function frame() {
      raf = requestAnimationFrame(frame);
      if (!visible) return;
      const t = reduced ? 0 : clock.getElapsedTime();
      const p = smooth(Math.min(1, Math.max(0, progress?.current?.value || 0)));
      const narrow = Math.min(1, camera.aspect / 1.6);

      mouse.sx += (mouse.x - mouse.sx) * 0.05;
      mouse.sy += (mouse.y - mouse.sy) * 0.05;

      // wide establishing shot -> push in on the laptop screen
      const startPos = tmp.set(0.4 + mouse.sx * 0.7, 2.7 - mouse.sy * 0.3, 7.6 + (1 - narrow) * 5);
      const endPos = new THREE.Vector3(-0.6, 1.0, 2.6);
      camera.position.copy(startPos).lerp(endPos, p);
      look.set(-0.3, 2.7, 0).lerp(new THREE.Vector3(-0.6, 0.7, 0), p);
      camera.lookAt(look);

      lampLight.intensity = 13 + Math.sin(t * 2.1) * 0.8;
      dust.rotation.y = t * 0.02;
      dust.position.y = Math.sin(t * 0.3) * 0.08;

      bubbles.forEach((b) => {
        const ang = b.a + t * b.s;
        const ox = Math.cos(ang) * b.r;
        const oz = Math.sin(ang) * b.r * 0.55 - 0.4;
        const oy = b.h + Math.sin(t * 0.9 + b.ph) * 0.12;
        const q = smooth(Math.min(1, p * 1.35));
        b.mesh.position.set(ox + (target.x - ox) * q, oy + (target.y - oy) * q, oz + (target.z - oz) * q);
        b.mesh.scale.setScalar(1 - q * 0.85);
        b.mesh.material.opacity = 0.42 * (1 - q * 0.9);
        b.mesh.lookAt(camera.position);
      });

      renderer.render(scene, camera);
    }
    frame();
    if (reduced) {
      // one still frame
      cancelAnimationFrame(raf);
      raf = 0;
      renderer.render(scene, camera);
    }

    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("pointermove", onMove);
      ro.disconnect();
      io.disconnect();
      scene.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose());
      });
      screenTex.dispose();
      renderer.dispose();
      renderer.domElement.remove();
    };
  }, [progress, onFail]);

  return <div ref={host} className="ld-canvas" aria-hidden="true" />;
}
