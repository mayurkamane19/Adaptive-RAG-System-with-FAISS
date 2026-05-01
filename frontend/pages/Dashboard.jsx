import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import Chart from "../components/Chart";
import Table from "../components/Table";
import {
  dashboardOverviewRequest,
  getStoredSession,
} from "../api/client";

export default function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    dashboardOverviewRequest(session.token)
      .then((data) => {
        setOverview(data);
        setError("");
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to load dashboard.");
      });
  }, []);

  const hero = overview?.hero;
  const stats = overview?.stats ?? [];
  const growthBars = overview?.growth_bars ?? [];
  const rows = overview?.accounts ?? [];

  return (
    <div className="page-grid">
      <section className="hero-panel saffron">
        <div>
          <p className="eyebrow">Command Center</p>
          <h2>{hero?.headline ?? "Loading live revenue and workspace activity..."}</h2>
          <span>
            {hero?.subtext ?? "PulseStack is fetching live backend data for this workspace."}
          </span>
        </div>
        <div className="hero-visual">
          <div className="orbital-card">
            <strong>ARR</strong>
            <h3>{hero?.arr_value ?? "..."}</h3>
            <p>{hero?.arr_hint ?? "Waiting for backend..."}</p>
          </div>
        </div>
      </section>

      <div className="stats-grid">
        {stats.map((stat) => (
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
        title="Growth Curve"
        subtitle="Revenue momentum by month"
        bars={growthBars}
      />

      <Table
        columns={["Account", "Plan", "Revenue", "Status"]}
        rows={rows}
      />
    </div>
  );
}
