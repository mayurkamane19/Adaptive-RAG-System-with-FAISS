import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import Chart from "../components/Chart";
import { analyticsOverviewRequest, getStoredSession } from "../api/client";

export default function Analytics() {
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    analyticsOverviewRequest(session.token)
      .then((data) => {
        setOverview(data);
        setError("");
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to load analytics.");
      });
  }, []);

  return (
    <div className="page-grid">
      <section className="hero-panel sunrise">
        <div>
          <p className="eyebrow">Analytics Studio</p>
          <h2>{overview?.hero?.headline ?? "Loading analytics overview..."}</h2>
          <span>{overview?.hero?.subtext ?? "Fetching live analytics from the backend."}</span>
        </div>
        <div className="hero-visual grid-visual">
          <span />
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

      <Chart
        title="Funnel Trend"
        subtitle="Acquisition to paid conversion"
        variant="line"
        points={overview?.points ?? []}
      />
    </div>
  );
}
