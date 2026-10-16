// Shared handle to the Lenis smooth-scroll instance (only exists on the landing page)
let instance = null;

export function setLenis(lenis) {
  instance = lenis;
}

export function smoothScrollTo(target, offset = -72) {
  const el = typeof target === "string" ? document.querySelector(target) : target;
  if (!el) return;
  if (instance) instance.scrollTo(el, { offset, duration: 1.6 });
  else el.scrollIntoView({ behavior: "smooth" });
}
