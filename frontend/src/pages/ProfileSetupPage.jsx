import { useNavigate } from "react-router-dom";
import Logo from "../components/Logo";
import ProfileForm from "../components/ProfileForm";
import { useAuth } from "../hooks/useAuth";

export default function ProfileSetupPage() {
  const { user, updateAccount } = useAuth();
  const navigate = useNavigate();

  async function save(profile) {
    await updateAccount({ profile: { ...profile, completed: true } });
    navigate("/dashboard", { replace: true });
  }

  return (
    <div className="setup-wrap">
      <header className="setup-head">
        <Logo />
      </header>
      <main id="main" className="container stack">
        <div className="page-header">
          <h1>Set up your profile{user?.name ? `, ${user.name.split(" ")[0]}` : ""}</h1>
          <p className="muted">This helps NUDGE organise your subjects and deadlines. You can edit it anytime.</p>
        </div>
        <ProfileForm
          initial={user?.profile}
          submitLabel="Save and continue"
          onSubmit={save}
          extraAction={
            <button type="button" className="btn btn-ghost" onClick={() => navigate("/dashboard", { replace: true })}>
              Skip for now
            </button>
          }
        />
      </main>
    </div>
  );
}