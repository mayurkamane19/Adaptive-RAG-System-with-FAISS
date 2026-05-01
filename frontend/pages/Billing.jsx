import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import Table from "../components/Table";
import {
  billingOverviewRequest,
  createBillingItemRequest,
  deleteBillingItemRequest,
  getStoredSession,
} from "../api/client";

export default function Billing() {
  const session = getStoredSession();
  const isAdmin = session?.user?.role === "admin";
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    item: "",
    amount: "",
    status: "Paid",
    invoice_date: "",
  });

  function loadOverview() {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    billingOverviewRequest(session.token)
      .then((data) => {
        setOverview(data);
        setError("");
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to load billing.");
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

    createBillingItemRequest(session.token, form)
      .then(() => {
        setForm({ item: "", amount: "", status: "Paid", invoice_date: "" });
        loadOverview();
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to create billing item.");
      });
  }

  function handleDelete(row) {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    deleteBillingItemRequest(session.token, row.id)
      .then(() => loadOverview())
      .catch((requestError) => {
        setError(requestError.message || "Unable to delete billing item.");
      });
  }

  return (
    <div className="page-grid">
      <section className="hero-panel plum">
        <div>
          <p className="eyebrow">Billing Desk</p>
          <h2>{overview?.hero?.headline ?? "Loading billing overview..."}</h2>
          <span>{overview?.hero?.subtext ?? "Fetching invoice and plan data from the backend."}</span>
        </div>
        <div className="hero-visual wallet">
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

      {isAdmin ? (
        <section className="panel form-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Create Billing Item</p>
              <h3>Add invoice, credit, or subscription line</h3>
            </div>
          </div>

          <form className="inline-form" onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Item name"
              value={form.item}
              onChange={(event) => setForm({ ...form, item: event.target.value })}
              required
            />
            <input
              type="text"
              placeholder="$2,400"
              value={form.amount}
              onChange={(event) => setForm({ ...form, amount: event.target.value })}
              required
            />
            <select
              value={form.status}
              onChange={(event) => setForm({ ...form, status: event.target.value })}
            >
              <option>Paid</option>
              <option>Pending</option>
              <option>Overdue</option>
            </select>
            <input
              type="text"
              placeholder="30 Apr 2026"
              value={form.invoice_date}
              onChange={(event) => setForm({ ...form, invoice_date: event.target.value })}
              required
            />
            <button type="submit" className="primary-action">
              Add Item
            </button>
          </form>
        </section>
      ) : (
        <section className="panel access-note">
          <p className="eyebrow">Admin Only</p>
          <h3>Billing management is available only to admin accounts.</h3>
        </section>
      )}

      {error ? <section className="panel api-error">{error}</section> : null}

      <Table
        columns={["Item", "Amount", "Status", "Date"]}
        rows={overview?.rows ?? []}
        actionLabel="Delete"
        onAction={isAdmin ? handleDelete : undefined}
      />
    </div>
  );
}
