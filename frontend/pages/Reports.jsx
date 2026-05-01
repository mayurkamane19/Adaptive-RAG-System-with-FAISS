import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import Chart from "../components/Chart";
import Table from "../components/Table";
import {
  createReportRunRequest,
  deleteReportRunRequest,
  getStoredSession,
  reportsOverviewRequest,
} from "../api/client";

export default function Reports() {
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: "",
    status: "Scheduled",
    day_label: "Mon",
  });

  function loadOverview() {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    reportsOverviewRequest(session.token)
      .then((data) => {
        setOverview(data);
        setError("");
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to load reports.");
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

    createReportRunRequest(session.token, form)
      .then(() => {
        setForm({ name: "", status: "Scheduled", day_label: "Mon" });
        loadOverview();
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to create report run.");
      });
  }

  function handleDelete(row) {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    deleteReportRunRequest(session.token, row.id)
      .then(() => loadOverview())
      .catch((requestError) => {
        setError(requestError.message || "Unable to delete report run.");
      });
  }

  return (
    <div className="page-grid">
      <section className="hero-panel sand">
        <div>
          <p className="eyebrow">Report Builder</p>
          <h2>{overview?.hero?.headline ?? "Loading reports overview..."}</h2>
          <span>{overview?.hero?.subtext ?? "Fetching reporting data from the backend."}</span>
        </div>
        <div className="hero-visual sheets">
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
            <p className="eyebrow">Create Report Run</p>
            <h3>Schedule or draft a report workflow</h3>
          </div>
        </div>

        <form className="inline-form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Report name"
            value={form.name}
            onChange={(event) => setForm({ ...form, name: event.target.value })}
            required
          />
          <select
            value={form.status}
            onChange={(event) => setForm({ ...form, status: event.target.value })}
          >
            <option>Scheduled</option>
            <option>Completed</option>
            <option>Draft</option>
          </select>
          <select
            value={form.day_label}
            onChange={(event) => setForm({ ...form, day_label: event.target.value })}
          >
            <option>Mon</option>
            <option>Tue</option>
            <option>Wed</option>
            <option>Thu</option>
            <option>Fri</option>
            <option>Sat</option>
          </select>
          <div className="form-spacer" />
          <button type="submit" className="primary-action">
            Add Run
          </button>
        </form>
      </section>

      {error ? <section className="panel api-error">{error}</section> : null}

      <Chart
        title="Report Volume"
        subtitle="Weekly report generation"
        bars={overview?.bars ?? []}
      />

      <Table
        columns={["Report", "Status", "Day"]}
        rows={overview?.rows ?? []}
        actionLabel="Delete"
        onAction={handleDelete}
      />
    </div>
  );
}
