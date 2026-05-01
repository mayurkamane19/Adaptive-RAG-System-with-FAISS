import React, { useEffect, useState } from "react";
import Card from "../components/Card";
import { getStoredSession, profileOverviewRequest } from "../api/client";

export default function Profile() {
  const [overview, setOverview] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const session = getStoredSession();
    if (!session?.token) {
      return;
    }

    profileOverviewRequest(session.token)
      .then((data) => {
        setOverview(data);
        setError("");
      })
      .catch((requestError) => {
        setError(requestError.message || "Unable to load profile.");
      });
  }, []);

  return (
    <div className="page-grid">
      <section className="hero-panel blush">
        <div>
          <p className="eyebrow">Profile Studio</p>
          <h2>{overview?.hero?.headline ?? "Loading profile overview..."}</h2>
          <span>{overview?.hero?.subtext ?? "Fetching profile data from the backend."}</span>
        </div>
        <div className="hero-visual profile-badge">
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

      <section className="panel profile-panel">
        <div className="profile-avatar">{overview?.profile?.initials ?? "PS"}</div>
        <div>
          <h3>{overview?.profile?.name ?? "Workspace User"}</h3>
          <p>{overview?.profile?.role ?? "Loading role..."}</p>
          <span>{overview?.profile?.summary ?? "Loading preferences..."}</span>
        </div>
      </section>
    </div>
  );
}
