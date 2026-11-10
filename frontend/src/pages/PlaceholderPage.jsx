import { Link } from "react-router-dom";
import { PUBLIC_ROUTES, APP_ROUTES } from "../routeConfig";
import { Button, Card, Field, Tag, Callout, PageHeader } from "../components/ui";

export default function PlaceholderPage({ title }) {
  const all = [...PUBLIC_ROUTES, ...APP_ROUTES];
  return (
    <main className="container" style={{ padding: "var(--space-6) var(--space-5)" }}>
      <PageHeader title={title} subtitle="This page is coming in a later step." actions={<Button>Primary</Button>} />

      <div className="grid-2">
        <Card title="Buttons and tags">
          <div className="stack">
            <div className="row">
              <Button>Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="danger">Delete</Button>
              <Button disabled>Disabled</Button>
            </div>
            <div className="row">
              <Tag tone="primary">Assignment</Tag>
              <Tag tone="success">Completed</Tag>
              <Tag tone="warning">Due today</Tag>
              <Tag tone="danger">Overdue</Tag>
              <Tag tone="info">Changed</Tag>
              <Tag>Neutral</Tag>
            </div>
            <Callout tone="warning">Demo callout message.</Callout>
          </div>
        </Card>

        <Card title="Form fields">
          <div className="stack">
            <Field label="Email" type="email" placeholder="you@college.edu" hint="We never share this." required />
            <Field label="Password" type="password" error="Password must be at least 8 characters." />
            <Field label="Course" as="select" defaultValue="">
              <option value="" disabled>Select…</option>
              <option>B.Tech CSE</option>
            </Field>
          </div>
        </Card>
      </div>

      <Card title="All routes" className="stack" style={{ marginTop: "var(--space-4)" }}>
        <ul>
          {all.map((r) => (
            <li key={r.path}>
              <Link to={r.path}>{r.label}</Link> <code>{r.path}</code>
            </li>
          ))}
        </ul>
      </Card>
    </main>
  );
}