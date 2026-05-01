import React from "react";

export default function Navbar({ pageTitle, authUser, onLogout }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Unified SaaS Workspace</p>
        <h1>{pageTitle}</h1>
      </div>

      <div className="topbar-actions">
        <div className="user-chip">
          <strong>{authUser?.fullName ?? "Workspace User"}</strong>
          <span>
            {authUser?.role ? `${authUser.role.toUpperCase()} · ` : ""}
            {authUser?.email ?? "user@pulsestack.com"}
          </span>
        </div>
        <label className="search-box">
          <span>Search</span>
          <input type="text" placeholder="customers, reports, invoices" />
        </label>
        <button type="button" className="secondary-action" onClick={onLogout}>
          Logout
        </button>
        <button type="button" className="primary-action">
          New Workflow
        </button>
      </div>
    </header>
  );
}
