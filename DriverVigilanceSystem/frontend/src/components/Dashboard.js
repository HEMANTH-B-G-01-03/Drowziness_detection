import React from "react";

function riskColor(score) {
  if (score < 30) return "#22c55e";
  if (score < 60) return "#facc15";
  if (score < 85) return "#fb923c";
  return "#ef4444";
}

function riskClass(level) {
  switch ((level || "").toLowerCase()) {
    case "safe":
      return "status-safe";
    case "caution":
      return "status-caution";
    case "warning":
      return "status-warning";
    case "critical":
      return "status-critical";
    default:
      return "status-unknown";
  }
}

export default function Dashboard({ status }) {
  const risk = status?.risk;
  const score = risk?.risk_score ?? 0;
  const level = risk?.risk_level ?? "Unknown";
  const alerts = risk?.alerts ?? [];
  const cnn = status?.cnn_prediction;

  // Multi-label: zero, one, or several classes can be active at once.
  const activeClasses = cnn?.active_classes ?? (cnn?.class ? [cnn.class] : []);

  return (
    <div className="card">
      <h2>Driver Status &amp; Risk Score</h2>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div>
          <div style={{ fontSize: 13, color: "#94a3b8" }}>Active State(s)</div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 4 }}>
            {activeClasses.length > 0 ? (
              activeClasses.map((cls) => (
                <span
                  key={cls}
                  style={{
                    fontSize: 20,
                    fontWeight: 700,
                    textTransform: "capitalize",
                    padding: "2px 10px",
                    borderRadius: 8,
                    background: cls === "alert" ? "#064e3b" : "#3f1d1d",
                    color: cls === "alert" ? "#6ee7b7" : "#fca5a5",
                  }}
                >
                  {cls}
                </span>
              ))
            ) : (
              <span style={{ fontSize: 20, fontWeight: 700, color: "#94a3b8" }}>—</span>
            )}
          </div>
        </div>
        <span className={`status-badge ${riskClass(level)}`}>{level}</span>
      </div>

      {activeClasses.length > 1 && (
        <div
          style={{
            marginTop: 10,
            fontSize: 12,
            color: "#fca5a5",
            background: "#3f1d1d",
            padding: "6px 10px",
            borderRadius: 8,
          }}
        >
          ⚠ Multiple states detected simultaneously — risk score reflects the
          combined effect.
        </div>
      )}

      <div className="risk-meter">
        <div
          className="risk-meter-fill"
          style={{ width: `${score}%`, background: riskColor(score) }}
        ></div>
      </div>
      <div style={{ textAlign: "right", fontSize: 13, color: "#94a3b8" }}>
        Risk Score: <strong style={{ color: "#e5e7eb" }}>{score}</strong> / 100
      </div>

      {alerts.length > 0 && (
        <>
          <div style={{ marginTop: 16, fontSize: 13, color: "#94a3b8" }}>Active Alerts</div>
          <ul className="alert-list">
            {alerts.map((a) => (
              <li key={a}>⚠ {a.toUpperCase()} ALERT</li>
            ))}
          </ul>
        </>
      )}

      {cnn?.probs && (
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 8 }}>
            Independent Class Probabilities
            <span style={{ opacity: 0.7 }}> (each 0-100%, don&apos;t need to sum to 100)</span>
          </div>
          {Object.entries(cnn.probs).map(([cls, p]) => {
            const isActive = activeClasses.includes(cls);
            return (
              <div key={cls} className="stat-row">
                <span
                  className="stat-label"
                  style={{
                    textTransform: "capitalize",
                    color: isActive ? "#e5e7eb" : "#94a3b8",
                    fontWeight: isActive ? 700 : 400,
                  }}
                >
                  {isActive ? "● " : "○ "}
                  {cls}
                </span>
                <span className="stat-value">{(p * 100).toFixed(1)}%</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}