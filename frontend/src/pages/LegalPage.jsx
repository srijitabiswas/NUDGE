import { Link } from "react-router-dom";
import { CONTACT_EMAIL, LEGAL_UPDATED } from "../config";

const PRIVACY = [
  ["Information we collect", [
    "Account details you give us: your name, email address and, if you set one up, your academic profile (course, semester and subjects).",
    "Content you add to NUDGE: messages, notices, screenshots and the tasks, deadlines and subjects created from them.",
    "Basic usage settings, such as your notification preferences.",
  ]],
  ["How we use it", [
    "To create your account and keep you signed in.",
    "To read the messages and screenshots you add, turn them into tasks and deadlines, and work out priorities and reminders for you.",
    "To keep the service working, secure and improving.",
  ]],
  ["Sharing", [
    "We do not sell your personal information.",
    "We only share data with service providers that help us run NUDGE (for example hosting), or when the law requires it.",
  ]],
  ["Storage and security", [
    "We take reasonable steps to protect your data. No online service can promise perfect security.",
    "We keep your information while your account is active and for as long as needed to provide the service.",
  ]],
  ["Your choices", [
    "You can view and update your profile and settings in the app.",
    "You can ask us to delete your account and data, or to give you a copy of it, by contacting us.",
  ]],
  ["Changes to this policy", [
    "If we change this policy we will update the date above and, for significant changes, tell you in the app.",
  ]],
];

const TERMS = [
  ["Using NUDGE", [
    "NUDGE helps students organise messages, deadlines and tasks. By creating an account or using the service you agree to these terms.",
  ]],
  ["Your account", [
    "Give accurate information and keep your sign-in details private. You are responsible for activity on your account.",
  ]],
  ["Your content", [
    "You keep ownership of the messages, screenshots and other content you add. You give us permission to process it only to provide NUDGE to you.",
    "Only add content you are allowed to use.",
  ]],
  ["Reminders are an aid, not a guarantee", [
    "NUDGE reads text and images automatically, so it can make mistakes with dates, times or priorities. Always check important deadlines against the original notice from your institution.",
    "We are not responsible for missed deadlines or other losses that result from relying on NUDGE alone.",
  ]],
  ["Acceptable use", [
    "Do not misuse the service, try to break or probe its security, or use it to break the law or the rights of others.",
  ]],
  ["Availability and changes", [
    "We aim to keep NUDGE available but cannot promise it will always be uninterrupted or error free. We may change or stop features, and we may update these terms. Continued use after an update means you accept it.",
  ]],
  ["Ending your use", [
    "You can stop using NUDGE at any time. We may suspend accounts that break these terms.",
  ]],
];

const PAGES = {
  privacy: { title: "Privacy Policy", intro: "This policy explains what NUDGE collects, why, and the choices you have.", sections: PRIVACY },
  terms: { title: "Terms of Use", intro: "These terms apply when you use NUDGE.", sections: TERMS },
};

export default function LegalPage({ kind }) {
  const page = PAGES[kind];
  return (
    <div className="legal">
      <h1>{page.title}</h1>
      <p className="legal-meta">Last updated {LEGAL_UPDATED}</p>
      <p>{page.intro}</p>
      {page.sections.map(([heading, items]) => (
        <section key={heading}>
          <h2>{heading}</h2>
          {items.length === 1 ? (
            <p>{items[0]}</p>
          ) : (
            <ul>{items.map((t) => <li key={t}>{t}</li>)}</ul>
          )}
        </section>
      ))}
      {CONTACT_EMAIL && (
        <section>
          <h2>Contact</h2>
          <p>Questions? Email <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.</p>
        </section>
      )}
      <p className="legal-back"><Link to="/">Back to home</Link></p>
    </div>
  );
}