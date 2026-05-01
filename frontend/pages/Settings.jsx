import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import { getStoredSession, settingsOverviewRequest } from "../api/client";

export default function Settings() {
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    settingsOverviewRequest(session.token)
      .then((data) => {
        setOverview(data);
        setError("");
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to load settings.");
      });
  }, []);

  return (
    <div className="page-grid">
      <section className="hero-panel moss">
        <div>
          <p className="eyebrow">System Settings</p>
          <h2>{overview?.hero?.headline ?? "Loading settings overview..."}</h2>
          <span>{overview?.hero?.subtext ?? "Fetching environment and security data."}</span>
        </div>
        <div className="hero-visual knobs">
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

      {error ? <section className="panel api-error">{error}</section> : null}

      <section className="panel config-list">
        {(overview?.items ?? []).map((item) => (
          <div key={item.title} className="config-row">
            <strong>{item.title}</strong>
            <span>{item.detail}</span>
          </div>
        ))}
      </section>
    </div>
  );
}
