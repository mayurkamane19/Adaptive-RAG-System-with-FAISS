import React from "react";

export default function Chart({
  title,
  subtitle,
  bars = [],
  points = [],
  variant = "bars",
}) {
  const hasLinePoints = points.length > 0;
  const hasBars = bars.length > 0;

  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">{title}</p>
          <h3>{subtitle}</h3>
        </div>
      </div>

      {variant === "line" ? (
        <div className="line-chart">
          {hasLinePoints ? (
            <svg viewBox="0 0 320 160" role="img" aria-label={subtitle}>
              <defs>
                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#f97316" />
                  <stop offset="100%" stopColor="#facc15" />
                </linearGradient>
              </defs>
              <path
                d={points
                  .map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`)
                  .join(" ")}
                fill="none"
                stroke="url(#lineGradient)"
                strokeWidth="5"
                strokeLinecap="round"
              />
              {points.map((point) => (
                <circle
                  key={`${point.x}-${point.y}`}
                  cx={point.x}
                  cy={point.y}
                  r="5"
                  fill="#fff7ed"
                  stroke="#fb923c"
                  strokeWidth="3"
                />
              ))}
            </svg>
          ) : (
            <div className="empty-state">No chart data available yet.</div>
          )}
        </div>
      ) : (
        <div className="bar-chart">
          {hasBars ? bars.map((bar) => (
            <div key={bar.label} className="bar-column">
              <div className="bar-track">
                <div className="bar-fill" style={{ height: `${bar.value}%` }} />
              </div>
              <span>{bar.label}</span>
            </div>
          )) : <div className="empty-state">No bar data available yet.</div>}
        </div>
      )}
    </section>
  );
}
