import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import {
  createNotificationItemRequest,
  deleteNotificationItemRequest,
  getStoredSession,
  notificationsOverviewRequest,
} from "../api/client";

export default function Notifications() {
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    title: "",
    detail: "",
  });

  function loadOverview() {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    notificationsOverviewRequest(session.token)
      .then((data) => {
        setOverview(data);
        setError("");
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to load notifications.");
      });
  }

  useEffect(() => {
    loadOverview();
  }, []);

  function handleSubmit(event) {
    event.preventDefault();
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    createNotificationItemRequest(session.token, form)
      .then(() => {
        setForm({ title: "", detail: "" });
        loadOverview();
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to create notification.");
      });
  }

  function handleDelete(item) {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    deleteNotificationItemRequest(session.token, item.id)
      .then(() => loadOverview())
      .catch((requestError) => {
        setError(requestError.message || "Unable to delete notification.");
      });
  }

  return (
    <div className="page-grid">
      <section className="hero-panel sky">
        <div>
          <p className="eyebrow">Alerts Center</p>
          <h2>{overview?.hero?.headline ?? "Loading notification center..."}</h2>
          <span>{overview?.hero?.subtext ?? "Fetching alert data from the backend."}</span>
        </div>
        <div className="hero-visual rings">
          <span />
          <span />
          <span />
        </div>
      </section>

      <div className="stats-grid">
        {(overview?.stats ?? []).map((stat) => (
          <Card
            key={stat.title}
            title={stat.title}
            value={stat.value}
            hint={stat.hint}
            tone={stat.tone}
          />
        ))}
      </div>

      <section className="panel form-panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Create Notification</p>
            <h3>Push a new alert into the live operations queue</h3>
          </div>
        </div>

        <form className="stack-form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Alert title"
            value={form.title}
            onChange={(event) => setForm({ ...form, title: event.target.value })}
            required
          />
          <input
            type="text"
            placeholder="15 minutes ago - Infrastructure"
            value={form.detail}
            onChange={(event) => setForm({ ...form, detail: event.target.value })}
            required
          />
          <button type="submit" className="primary-action">
            Add Alert
          </button>
        </form>
      </section>

      {error ? <section className="panel api-error">{error}</section> : null}

      <section className="panel timeline">
        {(overview?.items ?? []).length > 0 ? (
          overview.items.map((item) => (
            <div key={item.id ?? item.title} className="timeline-item timeline-action">
              <div>
                <strong>{item.title}</strong>
                <span>{item.detail}</span>
              </div>
              <button
                type="button"
                className="table-action danger-action"
                onClick={() => handleDelete(item)}
              >
                Delete
              </button>
            </div>
          ))
        ) : (
          <div className="empty-state">No notifications available yet.</div>
        )}
      </section>
    </div>
  );
}
