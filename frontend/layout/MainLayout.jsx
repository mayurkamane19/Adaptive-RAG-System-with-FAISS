import React from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";

export default function MainLayout({
  pages,
  activePageId,
  pageTitle,
  authUser,
  onLogout,
  routeKey,
  children,
}) {
  return (
    <div className="app-shell">
      <Sidebar pages={pages} activePageId={activePageId} />
      <main className="app-main">
        <Navbar pageTitle={pageTitle} authUser={authUser} onLogout={onLogout} />
        <div key={routeKey} className="page-content route-transition page-route-transition">
          {children}
        </div>
      </main>
    </div>
  );
}
