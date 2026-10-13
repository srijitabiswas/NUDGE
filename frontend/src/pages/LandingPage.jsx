import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const FEATURES = [
  { title: "Messages to tasks", text: "Paste a message or notice. NUDGE detects the title, type, date and time, and you confirm before anything is saved." },
  { title: "Priority with reasons", text: "Each task gets a priority and a plain-language reason, so you know what to do first and why." },
  { title: "Change and clash alerts", text: "See when a deadline, date or time changes, and when two tasks overlap." },
  { title: "Calendar and timetable", text: "Deadlines and your weekly classes in monthly and weekly views." },
  { title: "Workload analytics", text: "Open work, completion rate and early risks at a glance." },
  { title: "Your academic profile", text: "Keep your course, semester and subjects in one place, and see tasks grouped by subject." },
];

const STEPS = [
  { title: "Add", text: "Paste a message, notice or announcement you received." },
  { title: "Review", text: "Check the detected task, fix anything, and confirm." },
  { title: "Act", text: "Track deadlines, see priorities and get alerts before things slip." },
];

export default function LandingPage() {
  const { user } = useAuth();

  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div className="stack">
            <p className="eyebrow">Student life management</p>
            <h1>Turn scattered messages into a clear plan.</h1>
            <p className="hero-sub">
              NUDGE reads the messages, notices and deadlines you receive and turns them into tasks you can review,
              prioritise and track, all in one place.
            </p>
            <div className="row">
              {user ? (
                <Link className="btn btn-primary btn-lg" to="/dashboard">Go to dashboard</Link>
              ) : (
                <>
                  <Link className="btn btn-primary btn-lg" to="/signup">Create your account</Link>
                  <Link className="btn btn-secondary btn-lg" to="/login">Sign in</Link>
                </>
              )}
            </div>
          </div>

          <figure className="demo" aria-label="Example of a message becoming a task">
            <div className="demo-msg">
              <span className="demo-label">Message</span>
              <p>Reminder: DBMS assignment 3 is due tomorrow by 5 PM. Submit on the LMS.</p>
            </div>
            <div className="demo-arrow" aria-hidden="true">↓</div>
            <div className="demo-task">
              <span className="demo-label">Task</span>
              <strong>Submit DBMS assignment 3</strong>
              <div className="row demo-tags">
                <span className="tag tag-neutral">Assignment</span>
                <span className="tag tag-neutral">Tomorrow, 17:00</span>
                <span className="tag tag-danger">High priority</span>
              </div>
            </div>
            <figcaption className="muted">Example only</figcaption>
          </figure>
        </div>
      </section>

      <section id="features" className="section">
        <div className="container stack">
          <div>
            <h2>What NUDGE does</h2>
            <p className="muted">Everything you need to stay on top of coursework, in one workspace.</p>
          </div>
          <div className="feature-grid">
            {FEATURES.map((f) => (
              <article key={f.title} className="card">
                <h3>{f.title}</h3>
                <p>{f.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="how-it-works" className="section section-alt">
        <div className="container stack">
          <div>
            <h2>How it works</h2>
            <p className="muted">Three steps, and you stay in control.</p>
          </div>
          <ol className="steps">
            {STEPS.map((s, i) => (
              <li key={s.title} className="step">
                <span className="step-badge" aria-hidden="true">{i + 1}</span>
                <div>
                  <h3>{s.title}</h3>
                  <p>{s.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {!user && (
        <section className="section">
          <div className="container cta-band">
            <div>
              <h2>Ready to get organised?</h2>
              <p className="muted">Create an account and add your first message in a minute.</p>
            </div>
            <Link className="btn btn-primary btn-lg" to="/signup">Get started</Link>
          </div>
        </section>
      )}
    </>
  );
}