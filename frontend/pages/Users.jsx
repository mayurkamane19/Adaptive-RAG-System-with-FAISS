import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import Table from "../components/Table";
import {
  createWorkspaceUserRequest,
  deleteWorkspaceUserRequest,
  getStoredSession,
  usersOverviewRequest,
} from "../api/client";

export default function Users() {
  const session = getStoredSession();
  const isAdmin = session?.user?.role === "admin";
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    name: "",
    role: "",
    status: "Active",
    region: "",
  });

  function loadOverview() {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    usersOverviewRequest(session.token)
      .then((data) => {
        setOverview(data);
        setError("");
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to load users.");
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

    createWorkspaceUserRequest(session.token, form)
      .then(() => {
        setForm({ name: "", role: "", status: "Active", region: "" });
        loadOverview();
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to create user.");
      });
  }

  function handleDelete(row) {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    deleteWorkspaceUserRequest(session.token, row.id)
      .then(() => loadOverview())
      .catch((requestError) => {
        setError(requestError.message || "Unable to delete user.");
      });
  }

  return (
    <div className="page-grid">
      <section className="hero-panel coral">
        <div>
          <p className="eyebrow">People Hub</p>
          <h2>{overview?.hero?.headline ?? "Loading people workspace..."}</h2>
          <span>{overview?.hero?.subtext ?? "Fetching user and access data from the backend."}</span>
        </div>
        <div className="hero-visual avatars">
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

      {isAdmin ? (
        <section className="panel form-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Create User</p>
              <h3>Add a new workspace member</h3>
            </div>
          </div>

          <form className="inline-form" onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Full name"
              value={form.name}
              onChange={(event) => setForm({ ...form, name: event.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Role"
              value={form.role}
              onChange={(event) => setForm({ ...form, role: event.target.value })}
              required
            />
            <select
              value={form.status}
              onChange={(event) => setForm({ ...form, status: event.target.value })}
            >
              <option>Active</option>
              <option>Invited</option>
              <option>Paused</option>
            </select>
            <input
              type="text"
              placeholder="Region"
              value={form.region}
              onChange={(event) => setForm({ ...form, region: event.target.value })}
              required
            />
            <button type="submit" className="primary-action">
              Add User
            </button>
          </form>
        </section>
      ) : (
        <section className="panel access-note">
          <p className="eyebrow">Admin Only</p>
          <h3>User management is available only to admin accounts.</h3>
        </section>
      )}

      {error ? <section className="panel api-error">{error}</section> : null}

      <Table
        columns={["Name", "Role", "Status", "Region"]}
        rows={overview?.rows ?? []}
        actionLabel="Delete"
        onAction={isAdmin ? handleDelete : undefined}
      />
    </div>
  );
}
