import { useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CustomEase } from "gsap/CustomEase";
import Lenis from "lenis";
import { useAuth } from "../hooks/useAuth";
import Icon from "../components/Icon";
import logoImg from "../assets/nudge-logo.png";
import { setLenis, smoothScrollTo } from "../lib/lenis";
import HeroDemo from "../components/HeroDemo";
import Stickers from "../components/Stickers";
import HeroMontage from "../components/HeroMontage";
import { CONTACT_EMAIL } from "../config";

// Curved divider: painted in the previous section's colour at the top of the next one.
const Curve = ({ from }) => (
  <svg className={`ld-curve ld-curve-${from}`} viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true">
    <path d="M0 0H1440V64C1290 112 1110 116 930 84C750 52 610 18 420 30C250 40 120 78 0 100Z" fill="currentColor" />
  </svg>
);

gsap.registerPlugin(ScrollTrigger, CustomEase);
CustomEase.create("reveal", "0.16, 1, 0.3, 1");


const CHANNELS = [
  { label: "WhatsApp groups", color: "#8fb39a" },
  { label: "Faculty emails", color: "#e0a58b" },
  { label: "LMS portals", color: "#c9b79c" },
  { label: "Notice boards", color: "#e3c27a" },
  { label: "Exam timetables", color: "#b8a38a" },
  { label: "PDF syllabi", color: "#cdbfae" },
];

const FEATURES = [
  { icon: "add", title: "Messages to tasks", text: "Paste a message or notice. NUDGE finds the title, type, date and time, and you confirm before it is saved." },
  { icon: "tasks", title: "Priority with reasons", text: "Every task gets a priority and a plain-language reason, so you know what to do first and why." },
  { icon: "bell", title: "Change and clash alerts", text: "See when a deadline changes and when two tasks overlap, before it becomes a problem." },
  { icon: "calendar", title: "Calendar and timetable", text: "Deadlines and your weekly classes together, in month and week views." },
  { icon: "academics", title: "Assignments and exams", text: "A countdown tracker for what is due next, grouped by subject." },
  { icon: "analytics", title: "Workload analytics", text: "Open work, completion rate and early risks in one clear picture." },
  { icon: "dashboard", title: "One focused dashboard", text: "Your next priority and today's tasks first. Everything else a click away." },
  { icon: "user", title: "Your academic profile", text: "Keep your course, semester and subjects in one place." },
];

const HX = [
  { label: "Messages", text: "Bring scattered messages together in one place", img: "messages", c: "sage" },
  { label: "Deadlines", text: "Catch deadline changes before they catch you", img: "deadline", c: "peach" },
  { label: "Priorities", text: "See what to do first, and why", img: "priorities", c: "butter" },
  { label: "Timetable", text: "Keep classes and deadlines on one calendar", img: "calendar", c: "sky" },
  { label: "Clashes", text: "Spot clashes between exams and submissions", img: "clashes", c: "rose" },
  { label: "Subjects", text: "Track assignments and exams by subject", img: "coursework", c: "sand" },
];
const HX_STATS = [
  { n: "1", t: "place for every deadline" },
  { n: "2", t: "calendar views, month and week" },
  { n: "5", t: "steps from message to action" },
  { n: "1", t: "clear next step, every day" },
];

const SOURCES = ["WhatsApp", "Email", "LMS", "University Portal", "Manual Input"];
const WORDS = ["Reading", "Understanding", "Extracting", "Organizing"];
const CARDS = [
  { tag: "Assignment", title: "DBMS assignment 3", detail: "Friday · 5:00 PM" },
  { tag: "Event", title: "Viva and oral exam", detail: "Monday" },
  { tag: "Reminder", title: "Submission approaching", detail: "Due within 24 hours" },
  { tag: "Priority", title: "Suggested next action", detail: "Start with what is due first" },
];
const CHIP_START = [{ x: -320, y: -120 }, { x: 300, y: -90 }, { x: -260, y: 130 }, { x: 280, y: 150 }, { x: 0, y: -200 }];
const CARD_SETTLE = [{ x: -170, y: -90 }, { x: 170, y: -90 }, { x: -170, y: 90 }, { x: 170, y: 90 }];

function ModuleCard({ f, i }) {
  return (
    <li className="ld-card">
      <div className="ld-card-top">
        <span className="ld-card-icon"><Icon name={f.icon} size={22} /></span>
        <span className="ld-card-num" aria-hidden="true">{String(i + 1).padStart(2, "0")}</span>
      </div>
      <h3>{f.title}</h3>
      <p>{f.text}</p>
    </li>
  );
}

export default function LandingPage() {
  const { user } = useAuth();
  const root = useRef(null);

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const el = root.current;
    if (!el) return undefined;

    let lenis = null;
    let tick = null;
    if (!reduced) {
      lenis = new Lenis({ lerp: 0.1, smoothWheel: true });
      setLenis(lenis);
      lenis.on("scroll", ScrollTrigger.update);
      tick = (time) => lenis.raf(time * 1000);
      gsap.ticker.add(tick);
      gsap.ticker.lagSmoothing(0);
    }

    const q = (s) => Array.from(el.querySelectorAll(s));
    const one = (s) => el.querySelector(s);
    const mm = gsap.matchMedia();

    const ctx = gsap.context(() => {
      if (reduced) {
        el.classList.add("ld-reduced");
        return;
      }

      // hero copy entrance (the product demo animates itself)
      gsap.from(".hx-copy > *", { y: 24, opacity: 0, duration: 1, stagger: 0.1, ease: "reveal", delay: 0.1 });

      // hero scroll story (desktop): headline blurs away, the demo shrinks to a thumbnail,
      // the label pills grow into cards, then the statement and stats appear
      mm.add("(min-width: 900px) and (min-height: 620px)", () => {
        const pin = one(".hx-pin");
        if (!pin) return undefined;
        const geo = { s: 0.34, y: 0 };
        const measure = () => {
          const fr = one(".hx-frame");
          if (!fr) return;
          const H = pin.clientHeight;
          const w = fr.offsetWidth;
          const h = fr.offsetHeight;
          geo.s = Math.min(0.34, (H * 0.24) / h);
          const top = H * 0.47;
          geo.y = top - fr.offsetTop;
          pin.style.setProperty("--vw", `${w * geo.s}px`);
          pin.style.setProperty("--vh", `${h * geo.s}px`);
          pin.style.setProperty("--vt", `${top}px`);
        };
        measure();
        ScrollTrigger.addEventListener("refreshInit", measure);
        gsap.set(".hx-card", { opacity: 0, y: 36, scale: 0.92 });
        gsap.set(".hx-mid", { opacity: 0, y: 24 });
        gsap.set(".hx-stat", { opacity: 0, y: 24 });
        const tl = gsap.timeline({
          scrollTrigger: { trigger: pin, start: "top 72px", end: "+=230%", scrub: 1, pin: true, anticipatePin: 1, invalidateOnRefresh: true },
        });
        tl.to(".hx-copy", { opacity: 0, y: -40, filter: "blur(14px)", duration: 0.9, ease: "none" }, 0)
          .to(".hx-frame", { scale: () => geo.s, y: () => geo.y, duration: 1.4, ease: "power2.inOut" }, 0.1)
          .to(".hd-steps", { opacity: 0, duration: 0.4, ease: "none" }, 0.1)
          .to(".hx-pill", { opacity: 0, scale: 0.8, y: -30, duration: 0.7, stagger: 0.04, ease: "none" }, 0.3)
          .to(".hx-card", { opacity: 1, y: 0, scale: 1, duration: 0.9, stagger: 0.1, ease: "none" }, 0.7)
          .to(".hx-mid", { opacity: 1, y: 0, duration: 0.8, ease: "none" }, 1.3)
          .to(".hx-stat", { opacity: 1, y: 0, duration: 0.7, stagger: 0.12, ease: "none" }, 1.9)
          .to({}, { duration: 0.8 });
        return () => { ScrollTrigger.removeEventListener("refreshInit", measure); tl.scrollTrigger?.kill(); };
      });

      // problem: headline reveal, channel chips drift in and keep floating
      gsap.from(".ld-problem-head > *", {
        filter: "blur(14px)", opacity: 0, y: 24, duration: 1.3, stagger: 0.14, ease: "reveal",
        scrollTrigger: { trigger: ".ld-problem", start: "top 70%", toggleActions: "play none none reverse" },
      });
      gsap.from(".ld-ch", {
        opacity: 0, scale: 0.7, x: () => gsap.utils.random(-140, 140), y: () => gsap.utils.random(40, 120),
        rotate: () => gsap.utils.random(-14, 14), duration: 1.2, stagger: 0.09, ease: "reveal",
        scrollTrigger: { trigger: ".ld-chips-wrap", start: "top 85%", toggleActions: "play none none reverse" },
      });

      // solution: heading + pulsing core
      gsap.from(".ld-sol-head > *", {
        filter: "blur(16px)", opacity: 0, y: 24, duration: 1.4, stagger: 0.15, ease: "reveal",
        scrollTrigger: { trigger: ".ld-sol", start: "top 70%", toggleActions: "play none none reverse" },
      });
      gsap.to(".ld-sol .ld-orb", { scale: 1.07, duration: 2, repeat: -1, yoyo: true, ease: "sine.inOut" });

      // solution: pinned horizontal showcase (desktop)
      mm.add("(min-width: 768px)", () => {
        const pin = one(".ld-hpin");
        const track = one(".ld-hpin .ld-hs-track");
        const bar = one(".ld-hpin .ld-hs-bar");
        if (!pin || !track) return undefined;
        const dist = () => Math.max(0, track.scrollWidth - window.innerWidth + 160);
        const tween = gsap.to(track, {
          x: () => -dist(), ease: "none",
          scrollTrigger: {
            trigger: pin, start: "top 72px", end: () => `+=${dist()}`, scrub: 1, pin: true,
            invalidateOnRefresh: true,
            onUpdate: (self) => { if (bar) gsap.set(bar, { scaleX: Math.max(self.progress, 0.02) }); },
          },
        });
        return () => { tween.scrollTrigger?.kill(); tween.kill(); };
      });

      // how it works: one pinned, scrubbed timeline of five phases
      const k = gsap.utils.clamp(0.5, 1, window.innerWidth / 760);
      const chips = q(".ld-src");
      const cards = q(".ld-act");
      const words = q(".ld-word");
      gsap.set(".ld-p2, .ld-p3, .ld-p4, .ld-p5", { opacity: 0 });
      gsap.set(chips, { opacity: 0, x: (i) => CHIP_START[i].x * k, y: (i) => CHIP_START[i].y * k });
      gsap.set(cards, { opacity: 0, scale: 0.3, filter: "blur(14px)", x: 0, y: 0 });
      gsap.set(words, { opacity: 0 });

      const tl = gsap.timeline({
        scrollTrigger: { trigger: ".ld-hpin2", start: "top 72px", end: "+=450%", scrub: 1, pin: true },
      });
      tl.to(".ld-p1", { opacity: 1, duration: 1.2, ease: "none" }, 0)
        .to(".ld-p1", { opacity: 0, y: -20, duration: 0.6, ease: "none" }, 2.8);

      tl.to(".ld-p2", { opacity: 1, duration: 1, ease: "none" }, 3.2)
        .to(chips, { opacity: 1, stagger: 0.1, duration: 0.8, ease: "none" }, 3.4)
        .to(chips, { x: 0, y: 0, scale: 0.6, duration: 2, stagger: 0.05, ease: "none" }, 4.2)
        .to(".ld-p2", { opacity: 0, duration: 0.6, ease: "none" }, 6.2);

      tl.to(".ld-p3", { opacity: 1, duration: 1, ease: "none" }, 6.6);
      words.forEach((w, i) => {
        const s = 7.8 + i * 0.7;
        tl.to(w, { opacity: 1, duration: 0.3, ease: "none" }, s).to(w, { opacity: 0, duration: 0.3, ease: "none" }, s + 0.55);
      });
      tl.to(".ld-p3", { opacity: 0, duration: 0.6, ease: "none" }, 10.5);

      tl.to(".ld-p4", { opacity: 1, duration: 0.8, ease: "none" }, 10.9)
        .to(cards, {
          opacity: 1, scale: 1, filter: "blur(0px)",
          x: (i) => CARD_SETTLE[i].x * k, y: (i) => CARD_SETTLE[i].y,
          duration: 1.8, stagger: 0.15, ease: "none",
        }, 11.1);
      tl.to(cards, {
        x: (i) => CARD_SETTLE[i].x * k * 0.5, y: (i) => CARD_SETTLE[i].y * 0.5,
        scale: 0.85, duration: 1, stagger: 0.05, ease: "none",
      }, 13.6)
        .to(cards, { opacity: 0, duration: 0.6, ease: "none" }, 14.6)
        .to(".ld-p4", { opacity: 0, duration: 0.3, ease: "none" }, 15)
        .to(".ld-p5", { opacity: 1, duration: 1, ease: "none" }, 14.9);

      // final call to action + footer
      gsap.from(".ld-final .ld-rise", {
        y: 60, opacity: 0, duration: 1, stagger: 0.14, ease: "reveal",
        scrollTrigger: { trigger: ".ld-final", start: "top 70%", toggleActions: "play none none reverse" },
      });
      gsap.from(".ld-foot .ld-rise", {
        y: 50, opacity: 0, duration: 0.9, stagger: 0.1, ease: "reveal",
        scrollTrigger: { trigger: ".ld-foot", start: "top 90%", toggleActions: "play none none none" },
      });
    }, el);

    const refresh = () => ScrollTrigger.refresh();
    if (document.fonts?.ready) document.fonts.ready.then(refresh);
    window.addEventListener("load", refresh);

    return () => {
      window.removeEventListener("load", refresh);
      mm.revert();
      ctx.revert();
      if (lenis) {
        gsap.ticker.remove(tick);
        lenis.destroy();
        setLenis(null);
      }
    };
  }, []);

  const year = new Date().getFullYear();
  const cta = user ? (
    <Link className="ld-btn ld-btn-grad" to="/dashboard">Go to dashboard <span aria-hidden="true">→</span></Link>
  ) : (
    <Link className="ld-btn ld-btn-grad" to="/signup">Get Started <span aria-hidden="true">→</span></Link>
  );

  return (
    <div className="ld" ref={root}>
      {/* HERO */}
      <section id="top" className="ld-hero">
        <div className="hx-pin">
          <div className="hx-copy">
            <p className="ld-badge"><span className="ld-ping" aria-hidden="true" />NUDGE · AI student companion</p>
            <h1 className="ld-h1">
              <span className="ld-line">Turn scattered messages</span>
              <span className="ld-line"><span className="ld-grad">into meaningful actions.</span></span>
            </h1>
            <p className="ld-lead">
              NUDGE reads the messages and notices you get every day, pulls out the deadline, and ranks what to do first.
            </p>
            <div className="ld-cta-row ld-cta-center">
              {cta}
              <button type="button" className="ld-btn ld-btn-ghost" onClick={() => smoothScrollTo("#how-it-works")}>
                See how it works
              </button>
            </div>
          </div>

          <div className="hx-frame"><HeroMontage><HeroDemo /></HeroMontage></div>

          <div className="hx-pills" aria-hidden="true">
            {HX.map((h, i) => (
              <span key={h.label} className={`hx-pill hx-${h.c} hx-p${i}`}><i />{h.label}</span>
            ))}
          </div>

          <div className="hx-mid">
            <h2>We turn the noise of student life<br />into clear next steps.</h2>
          </div>

          <ul className="hx-cards">
            {HX.map((h, i) => (
              <li key={h.label} className={`hx-card hx-${h.c} hx-c${i}`}>
                <img className="hx-img" src={`/media/${h.img}.png`} alt="" width="104" height="104" loading="lazy" decoding="async"
                  onError={(e) => { e.currentTarget.style.display = "none"; }} />
                <span className="hx-card-text">{h.text}</span>
              </li>
            ))}
            <li className="hx-card hx-teal hx-c6">
              <span className="hx-card-text">Turn everyday reminders into timely action</span>
            </li>
          </ul>

          <ul className="hx-stats">
            {HX_STATS.map((x) => (
              <li key={x.t} className="hx-stat"><b>{x.n}</b><span>{x.t}</span></li>
            ))}
          </ul>
        </div>
      </section>

      {/* PROBLEM */}
      <section id="problem" className="ld-problem ld-light">
        <Curve from="dark" />
        <div className="ld-wrap ld-center">
          <div className="ld-problem-head">
            <p className="ld-eyebrow">The problem</p>
            <h2 className="ld-h2">
              Academic information <br />
              <span className="ld-grad">is fragmented everywhere.</span>
            </h2>
            <p className="ld-lead">
              Students follow many uncoordinated channels every day. Urgent deadlines get buried in WhatsApp. Exam dates hide inside portals. Notices arrive by email. Everything is scattered, and nothing is organised.
            </p>
          </div>
          <div className="ld-chips-wrap">
            {CHANNELS.map((c) => (
              <span key={c.label} className="ld-ch">
                <i style={{ background: c.color }} aria-hidden="true" />
                {c.label}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* SOLUTION */}
      <section id="solution" className="ld-sol">
        <Curve from="light" />
        <div className="ld-wrap ld-center">
          <div className="ld-sol-head">
            <p className="ld-eyebrow">Our solution</p>
            <h2 className="ld-h2">
              One platform. <br />
              <span className="ld-grad">Intelligent decisions.</span>
            </h2>
            <p className="ld-lead">
              NUDGE combines language processing, smart prioritisation and academic planning into one calm place for student life.
            </p>
          </div>
          <div className="ld-orb" aria-hidden="true">
            <img src={logoImg} alt="" width="64" height="64" />
          </div>
        </div>

        <div className="ld-hpin">
          <ul className="ld-hs-track">
            {FEATURES.map((f, i) => <ModuleCard key={f.title} f={f} i={i} />)}
          </ul>
          <div className="ld-hs-progress" aria-hidden="true"><span className="ld-hs-bar" /></div>
        </div>
        <ul className="ld-hswipe">
          {FEATURES.map((f, i) => <ModuleCard key={f.title} f={f} i={i} />)}
        </ul>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="ld-how ld-light">
        <Curve from="dark" />
        <div className="ld-hpin2">
          {Array.from({ length: 10 }, (_, i) => (
            <span
              key={i}
              className="ld-dot"
              aria-hidden="true"
              style={{ left: `${15 + ((i * 37) % 70)}%`, top: `${20 + ((i * 53) % 60)}%`, animationDuration: `${7 + (i % 5)}s`, animationDelay: `${i * 0.6}s` }}
            />
          ))}

          <div className="ld-ph ld-p1">
            <p className="ld-eyebrow ld-eyebrow-accent">How NUDGE works</p>
            <h2 className="ld-h2">
              From raw information<br /><span className="ld-grad">to intelligent actions.</span>
            </h2>
            <p className="ld-lead">
              NUDGE turns scattered academic notices into structured, actionable items, so you stay organised, prepared and confident.
            </p>
          </div>

          <div className="ld-ph ld-p2">
            <p className="ld-label ld-label-top">Information enters</p>
            <div className="ld-src-area">
              {SOURCES.map((s) => <div key={s} className="ld-src">{s}</div>)}
            </div>
          </div>

          <div className="ld-ph ld-p3">
            <p className="ld-core-title">NUDGE Intelligence</p>
            <p className="ld-label">Analyze <b>→</b> Understand <b>→</b> Prioritise</p>
            <div className="ld-words">
              {WORDS.map((w) => <span key={w} className="ld-word ld-grad">{w}</span>)}
            </div>
          </div>

          <div className="ld-ph ld-p4">
            <div className="ld-act-area">
              {CARDS.map((c) => (
                <div key={c.tag} className="ld-act">
                  <span className="ld-act-tag">{c.tag}</span>
                  <strong>{c.title}</strong>
                  <span>{c.detail}</span>
                </div>
              ))}
            </div>
            <p className="ld-note">Example only</p>
          </div>

          <div className="ld-ph ld-p5">
            <h2 className="ld-h2">
              From scattered information<br /><span className="ld-grad">to confident action.</span>
            </h2>
            <p className="ld-lead">One intelligent platform for the student journey.</p>
          </div>
        </div>
      </section>

      {/* CALL TO ACTION */}
      <section className="ld-final">
        <Curve from="light" />
        <div className="ld-final-inner">
          <div className="ld-final-copy">
            <h2 className="ld-rise">Let's make student life simpler.</h2>
            <p className="ld-rise">
              Deadlines in one place, clear priorities and early warnings, so you always know what to do next.
            </p>
            <Link className="ld-outline ld-rise" to={user ? "/dashboard" : "/signup"}>
              {user ? "Go to dashboard" : "Get started"}
            </Link>
          </div>
          <Stickers />
        </div>
      </section>

      {/* FOOTER */}
      <footer id="contact" className="ld-foot ld-light">
        <Curve from="dark" />
        <div className="ld-foot-grid">
          <div className="ld-foot-brand">
            <a className="ld-foot-logo" href="#top" onClick={(e) => { e.preventDefault(); smoothScrollTo("#top", 0); }}>
              <img src={logoImg} alt="" width="52" height="52" />
              <span>NUDGE</span>
            </a>
            <p className="ld-foot-tag">From Messages to Actions: the intelligent student life management platform.</p>
            <Link className="ld-outline" to={user ? "/dashboard" : "/signup"}>
              {user ? "Go to dashboard" : "Get started"}
            </Link>
          </div>

          <div className="ld-foot-col">
            <ul>
              <li><a href="#top" onClick={(e) => { e.preventDefault(); smoothScrollTo("#top", 0); }}>Home</a></li>
              <li><Link to="/#solution">Solution</Link></li>
              <li><Link to="/#how-it-works">How it works</Link></li>
              <li><Link to="/#contact">Contact</Link></li>
            </ul>
          </div>

          <div className="ld-foot-col">
            <ul>
              <li><Link to="/signup">Sign up</Link></li>
              <li><Link to="/login">Log in</Link></li>
            </ul>
          </div>
        </div>

        <div className="ld-foot-bottom ld-rise">
          <span>© {year} NUDGE. All rights reserved.</span>
          <span className="ld-foot-legal">
            <Link to="/privacy">Privacy</Link>
            <Link to="/terms">Terms</Link>
            {CONTACT_EMAIL && <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>}
          </span>
        </div>
      </footer>
    </div>
  );
}