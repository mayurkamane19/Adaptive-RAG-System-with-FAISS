import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export default function Login({ onLogin }) {
  const navigate = useNavigate();
  const [error, setError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    onLogin({
      email: String(formData.get("email") ?? "").trim(),
      password: String(formData.get("password") ?? ""),
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
      <section className="auth-showcase">
        <div className="brand-mark">PS</div>
        <p className="eyebrow">PulseStack Access</p>
        <h1>Welcome back to your revenue command center.</h1>
        <span>
          Monitor metrics, team activity, billing health, and reports from one unified SaaS workspace.
        </span>

        <div className="auth-metrics">
          <article>
            <strong>4.8M</strong>
            <span>Tracked annual revenue</span>
          </article>
          <article>
            <strong>1,284</strong>
            <span>Workspace users</span>
          </article>
          <article>
            <strong>91%</strong>
            <span>Weekly focus score</span>
          </article>
        </div>
      </section>

      <section className="auth-panel">
        <div className="auth-panel-head">
          <p className="eyebrow">Sign In</p>
          <h2>Access your workspace</h2>
          <span>Use your work email to continue into PulseStack.</span>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            <span>Email address</span>
            <input
              type="email"
              name="email"
              placeholder="demo@pulsestack.com"
              defaultValue="demo@pulsestack.com"
              required
            />
          </label>

          <label>
            <span>Password</span>
            <input
              type="password"
              name="password"
              placeholder="Enter your password"
              defaultValue="123456"
              required
            />
          </label>

          <div className="auth-hint">
            Demo login: <strong>demo@pulsestack.com</strong> / <strong>123456</strong>
          </div>

          {error ? <div className="auth-error">{error}</div> : null}

          <button type="submit" className="primary-action auth-submit">
            Sign In
          </button>
        </form>

        <div className="auth-footer">
          <span>New to PulseStack?</span>
          <Link to="/signup">Create an account</Link>
        </div>
      </section>
    </div>
  );
}
