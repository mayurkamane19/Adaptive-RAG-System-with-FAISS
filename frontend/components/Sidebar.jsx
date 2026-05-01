import React from "react";
import { NavLink } from "react-router-dom";

const navGroups = [
  ["dashboard", "analytics", "users", "reports"],
  ["billing", "notifications", "profile", "settings"],
];

const iconMap = {
  dashboard: "01",
  analytics: "02",
  users: "03",
  reports: "04",
  billing: "05",
  notifications: "06",
  profile: "07",
  settings: "08",
};

export default function Sidebar({ pages, activePageId }) {
  return (
    <aside className="sidebar">
      <div>
        <div className="brand-mark">PS</div>
        <div className="brand-copy">
          <p>PulseStack</p>
          <span>Revenue OS</span>
        </div>
      </div>

      <div className="nav-groups">
        {navGroups.map((group, index) => (
          <nav key={group.join("-")} className="nav-group">
            {index === 1 ? <span className="nav-label">Workspace</span> : null}
            {group.map((pageId) => {
              const page = pages.find((entry) => entry.id === pageId);
              if (!page) {
                return null;
              }

              const isActive = activePageId === page.id;
              return (
                <NavLink
                  key={page.id}
                  to={page.path}
                  className={`nav-item ${isActive ? "active" : ""}`}
                >
                  <span>{iconMap[page.id]}</span>
                  {page.label}
                </NavLink>
              );
            })}
          </nav>
        ))}
      </div>

      <div className="sidebar-footer">
        <p>Team plan renewed</p>
        <span>128 seats active</span>
      </div>
    </aside>
  );
}
