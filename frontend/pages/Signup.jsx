import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Signup({ onSignup }) {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const password = String(formData.get("password") ?? "");
    const confirmPassword = String(formData.get("confirmPassword") ?? "");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    onSignup({
      full_name: String(formData.get("fullName") ?? "").trim(),
      email: String(formData.get("email") ?? "").trim(),
      password,
    }).then((result) => {
      if (!result.success) {
        setError(result.message);
        return;
      }

      setError("");
      navigate("/dashboard");
    });
  }

  return (
    <div className="auth-shell">
      <section className="auth-showcase signup-showcase">
        <div className="brand-mark">PS</div>
        <p className="eyebrow">Create Workspace</p>
        <h1>Launch your team inside a cleaner, faster SaaS control layer.</h1>
        <span>
          Set up reporting, user roles, billing visibility, and notification workflows in a few clicks.
        </span>

        <div className="auth-checks">
          <div>Team onboarding in one dashboard</div>
          <div>Real-time analytics and billing insights</div>
          <div>Ready for reports, automations, and scaling</div>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-panel-head">
          <p className="eyebrow">Sign Up</p>
          <h2>Create your account</h2>
          <span>Start your workspace with a few account details.</span>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            <span>Full name</span>
            <input type="text" name="fullName" placeholder="Mayur Patel" required />
          </label>

          <label>
            <span>Work email</span>
            <input type="email" name="email" placeholder="you@company.com" required />
          </label>

          <label>
            <span>Password</span>
            <input type="password" name="password" placeholder="Create a password" required />
          </label>

          <label>
            <span>Confirm password</span>
            <input
              type="password"
              name="confirmPassword"
              placeholder="Re-enter your password"
              required
            />
          </label>

          {error ? <div className="auth-error">{error}</div> : null}

          <button type="submit" className="primary-action auth-submit">
            Create Account
          </button>
        </form>

        <div className="auth-footer">
          <span>Already have an account?</span>
          <Link to="/login">Sign in</Link>
        </div>
      </section>
    </div>
  );
}
