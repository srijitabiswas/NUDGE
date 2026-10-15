import logoImg from "../assets/nudge-logo.png";

const POINTS = {
  login: [
    "Your tasks, deadlines and priorities in one place",
    "Alerts when a date changes or two tasks clash",
    "A calendar built from your own timetable",
  ],
  signup: [
    "Paste a message and get a task you can review",
    "Priorities with a plain-language reason",
    "Set up your subjects once, see everything by subject",
  ],
};

export default function AuthAside({ mode = "login" }) {
  return (
    <aside className="auth-aside" aria-label="About NUDGE">
      <img src={logoImg} alt="" className="auth-aside-logo" width="56" height="56" />
      <p className="eyebrow">From messages to actions</p>
      <h2>{mode === "login" ? "Pick up where you left off." : "Start organising your semester."}</h2>
      <ul>
        {POINTS[mode].map((p) => (
          <li key={p}>{p}</li>
        ))}
      </ul>
    </aside>
  );
}