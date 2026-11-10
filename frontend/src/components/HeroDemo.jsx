import { useEffect, useRef, useState } from "react";
import logoImg from "../assets/nudge-logo.png";

// Hero demo: one message becomes a task, gets a priority, then lands in the dashboard.
// Pure React state + CSS transitions. Step N turns on class "atN" (and all earlier ones).
const DURATIONS = [2800, 3400, 3800, 2800, 5000];
const STEPS = ["Message", "Detect", "Task", "Prioritise", "Dashboard"];

const ROWS = [
  { t: "DBMS assignment 3", d: "Tomorrow", p: "High", c: "hi", mine: true },
  { t: "OS lab record", d: "Friday", p: "Medium", c: "md" },
  { t: "Maths quiz prep", d: "Monday", p: "Low", c: "lo" },
];

export default function HeroDemo() {
  const reduced = typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const [step, setStep] = useState(reduced ? 4 : 0);
  const [out, setOut] = useState(false);
  const [snap, setSnap] = useState(false);
  const wrap = useRef(null);

  useEffect(() => {
    if (reduced) return undefined;
    let timer = 0;
    let visible = true;
    const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; });
    if (wrap.current) io.observe(wrap.current);

    const run = (s) => {
      timer = setTimeout(() => {
        if (!visible || document.hidden) { run(s); return; }
        if (s < 4) {
          setStep(s + 1);
          run(s + 1);
        } else {
          setOut(true);
          timer = setTimeout(() => {
            setSnap(true);
            setStep(0);
            timer = setTimeout(() => { setSnap(false); setOut(false); run(0); }, 80);
          }, 900);
        }
      }, DURATIONS[s]);
    };
    run(0);
    return () => { clearTimeout(timer); io.disconnect(); };
  }, [reduced]);

  const at = Array.from({ length: step + 1 }, (_, i) => `at${i}`).join(" ");

  return (
    <div className={`hd-wrap${out ? " out" : ""}${snap ? " snap" : ""}`} ref={wrap}>
      <p className="sr-only">
        Demo: a class message about a DBMS assignment due tomorrow at 11:59 PM is read by NUDGE, turned into a
        task with subject, deadline and type, marked high priority, and shown as the next focus on the dashboard.
        Sample data.
      </p>
      <div className={`hd ${at}`} aria-hidden="true">
        <div className="hd-grid" />

        {/* 1-2. the message */}
        <div className="hd-msg">
          <div className="hd-card hd-msg-card">
            <div className="hd-msg-head">
              <span className="hd-avatar">RS</span>
              <div>
                <strong>Prof. R. Sen</strong>
                <span>CSE 3A class group · 9:41 PM</span>
              </div>
            </div>
            <p className="hd-msg-body">
              Reminder: <span className="hl" data-l="Task" style={{ "--i": 0 }}>DBMS assignment 3</span> is due{" "}
              <span className="hl hl2" data-l="Deadline" style={{ "--i": 1 }}>tomorrow at 11:59 PM</span>. Submit the PDF
              on the <span className="hl hl3" data-l="Where" style={{ "--i": 2 }}>LMS</span>. No extensions.
            </p>
            <span className="hd-scan" />
          </div>
          <div className="hd-chip">
            <span className="hd-chip-a"><i className="hd-spin" />NUDGE is reading the message</span>
            <span className="hd-chip-b">✓ Found a task, a subject and a deadline</span>
          </div>
        </div>

        <span className="hd-link"><i /></span>

        {/* 3-4. the task */}
        <div className="hd-task">
          <div className="hd-card hd-task-card">
            <div className="hd-task-top">
              <span className="hd-ai"><i />Detected by NUDGE</span>
              <span className="hd-prio">High priority</span>
            </div>
            <h3>DBMS assignment 3</h3>
            <dl>
              <div className="hd-fld" style={{ "--i": 0 }}><dt>Subject</dt><dd>Database Management Systems</dd></div>
              <div className="hd-fld" style={{ "--i": 1 }}><dt>Deadline</dt><dd>Tomorrow · 11:59 PM</dd></div>
              <div className="hd-fld" style={{ "--i": 2 }}><dt>Type</dt><dd>Assignment</dd></div>
              <div className="hd-fld" style={{ "--i": 3 }}><dt>Status</dt><dd>To do</dd></div>
            </dl>
            <div className="hd-risk">Due in under 24 hours · at risk</div>
            <div className="hd-task-foot">
              <span>Review, then save</span>
              <span className="hd-confirm">
                <b className="a">Confirm task</b>
                <b className="b">✓ Added to tasks</b>
              </span>
            </div>
          </div>
        </div>

        {/* 5. the dashboard */}
        <div className="hd-dash">
          <div className="hd-card hd-dash-card">
            <div className="hd-dash-bar">
              <img src={logoImg} alt="" width="22" height="22" />
              <strong>NUDGE</strong>
              <span>Dashboard</span>
              <em>Sample data</em>
            </div>
            <div className="hd-dash-body">
              <div className="hd-focus">
                <p className="hd-kicker">Focus next</p>
                <h4>DBMS assignment 3</h4>
                <p className="hd-due">Due tomorrow · 11:59 PM</p>
                <p className="hd-why">Why: due soonest, so it comes first.</p>
                <span className="hd-prio">High priority</span>
              </div>
              <div className="hd-right">
                <div className="hd-tiles">
                  <div><b>1</b><span>Due in 24h</span></div>
                  <div><b>4</b><span>This week</span></div>
                  <div><b>0</b><span>Overdue</span></div>
                </div>
                <ul className="hd-list">
                  {ROWS.map((r, i) => (
                    <li key={r.t} className={r.mine ? "mine" : ""} style={{ "--i": i }}>
                      <span>{r.t}</span>
                      <em>{r.d}</em>
                      <b className={r.c}>{r.p}</b>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        <ol className="hd-steps" aria-hidden="true">
          {STEPS.map((s, i) => (
            <li key={s} className={i === step ? "on" : i < step ? "done" : ""}>
              <i>{i + 1}</i><span>{s}</span>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
