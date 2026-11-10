import { useId } from "react";

export function Button({ variant = "primary", size, className = "", type = "button", ...props }) {
  const cls = ["btn", `btn-${variant}`, size ? `btn-${size}` : "", className].filter(Boolean).join(" ");
  return <button type={type} className={cls} {...props} />;
}

export function Card({ title, actions, children, className = "", ...props }) {
  return (
    <section className={`card ${className}`} {...props}>
      {(title || actions) && (
        <div className="card-header">
          {title && <h2 className="card-title">{title}</h2>}
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}

// Labelled form control with hint and accessible error message.
// Use as="select" or as="textarea" for other controls.
export function Field({ label, hint, error, as: Control = "input", id, className = "", children, ...props }) {
  const autoId = useId();
  const fieldId = id || autoId;
  const hintId = hint ? `${fieldId}-hint` : undefined;
  const errorId = error ? `${fieldId}-error` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(" ") || undefined;

  return (
    <div className={`field ${className}`}>
      <label className="field-label" htmlFor={fieldId}>
        {label}
        {props.required && <span aria-hidden="true"> *</span>}
      </label>
      <Control
        id={fieldId}
        className="input"
        aria-invalid={error ? "true" : undefined}
        aria-describedby={describedBy}
        {...props}
      >
        {children}
      </Control>
      {hint && (
        <span id={hintId} className="field-hint">
          {hint}
        </span>
      )}
      {error && (
        <span id={errorId} className="field-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
}

// tone: neutral | primary | success | warning | danger | info
export function Tag({ tone = "neutral", children }) {
  return <span className={`tag tag-${tone}`}>{children}</span>;
}

export function Callout({ tone = "info", children }) {
  return (
    <div className={`callout callout-${tone}`} role={tone === "danger" ? "alert" : "status"}>
      {children}
    </div>
  );
}

export function PageHeader({ title, subtitle, actions }) {
  return (
    <header className="page-header">
      <div>
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
      </div>
      {actions && <div className="row">{actions}</div>}
    </header>
  );
}

export function EmptyState({ title, children }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      {children}
    </div>
  );
}