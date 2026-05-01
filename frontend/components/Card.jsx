import React from "react";

export default function Card({ title, value, hint, tone = "default" }) {
  return (
    <article className={`stat-card ${tone}`}>
      <p>{title}</p>
      <h3>{value}</h3>
      <span>{hint}</span>
    </article>
  );
}
