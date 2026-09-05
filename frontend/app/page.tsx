export default function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <p className="muted">
        AI-powered competitive pricing intelligence. Track products, detect
        anomalies, forecast movements, and get plain-language insights.
      </p>

      <div className="grid" style={{ marginTop: "1.5rem" }}>
        <div className="card">
          <div className="muted">Tracked Products</div>
          <div className="stat">—</div>
        </div>
        <div className="card">
          <div className="muted">Price Changes</div>
          <div className="stat">—</div>
        </div>
        <div className="card">
          <div className="muted">Active Alerts</div>
          <div className="stat">—</div>
        </div>
        <div className="card">
          <div className="muted">Anomalies</div>
          <div className="stat">—</div>
        </div>
      </div>

      <div className="card" style={{ marginTop: "1rem" }}>
        <h2>Quick start</h2>
        <ol className="muted">
          <li>Register / Login via the API docs or Login page</li>
          <li>Create a product and attach a <code>demo</code> listing</li>
          <li>Trigger a scrape → view analytics, anomalies, forecast & insights</li>
        </ol>
        <p>
          Backend API docs:{" "}
          <a href="http://localhost:8000/docs" style={{ color: "var(--accent)" }}>
            http://localhost:8000/docs
          </a>
        </p>
      </div>
    </div>
  );
}
