import { useEffect } from "react";

const HEADER = 72; // height of the sticky public navbar

// Calls onProgress(p, el) with p from 0 to 1 while a tall section scrolls
// past a sticky child. onProgress must be a stable (module-level) function.
export default function useScrollSection(ref, onProgress) {
  useEffect(() => {
    let raf = 0;

    function run() {
      raf = 0;
      const el = ref.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      const total = r.height - (window.innerHeight - HEADER);
      const p = total > 0 ? Math.min(1, Math.max(0, (HEADER - r.top) / total)) : 0;
      onProgress(p, el);
    }

    function schedule() {
      if (!raf) raf = requestAnimationFrame(run);
    }

    run();
    window.addEventListener("scroll", schedule, { passive: true });
    window.addEventListener("resize", schedule);
    return () => {
      if (raf) cancelAnimationFrame(raf);
      window.removeEventListener("scroll", schedule);
      window.removeEventListener("resize", schedule);
    };
  }, [ref, onProgress]);
}