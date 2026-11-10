import { useEffect, useRef, useState } from "react";

// Hero media slot. Plays the three-scene student montage when the file exists at
// /media/nudge-hero.mp4 (public/media). Until then, or if it fails to load, the
// existing HeroDemo (passed as children) is shown, so the hero never breaks.
const SRC_MP4 = "/media/nudge-hero.mp4";
const SRC_WEBM = "/media/nudge-hero.webm";
const POSTER = "/media/nudge-hero-poster.jpg";
const SCENES = ["Remembered the deadline", "Prepared for the test", "Found an opportunity"];

export default function HeroMontage({ children }) {
  const ref = useRef(null);
  const [ready, setReady] = useState(false);
  const [scene, setScene] = useState(0);
  const [reduced] = useState(() => window.matchMedia("(prefers-reduced-motion: reduce)").matches);

  useEffect(() => {
    const v = ref.current;
    if (!v || reduced) return undefined;
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) v.play().catch(() => {});
      else v.pause();
    }, { threshold: 0.35 });
    io.observe(v);
    return () => io.disconnect();
  }, [reduced]);

  const onTime = (e) => {
    const { currentTime, duration } = e.currentTarget;
    if (duration) setScene(Math.min(2, Math.floor((currentTime / duration) * 3)));
  };

  return (
    <>
      <div className={`hm-frame${ready ? " is-ready" : ""}`} hidden={!ready}>
        <video
          ref={ref}
          className="hm-video"
          muted
          loop={!reduced}
          playsInline
          preload="metadata"
          poster={POSTER}
          autoPlay={!reduced}
          onLoadedMetadata={() => setReady(true)}
          onTimeUpdate={onTime}
          aria-label="A short student-life montage: remembering a deadline, preparing for a test and finding an opportunity"
        >
          <source src={SRC_WEBM} type="video/webm" />
          <source src={SRC_MP4} type="video/mp4" />
        </video>
        <div className="hm-cap" aria-hidden="true">
          {SCENES.map((s, i) => (
            <span key={s} className={i === scene ? "on" : ""}>{s}</span>
          ))}
        </div>
      </div>
      {!ready && children}
    </>
  );
}