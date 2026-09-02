import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [paymentId, setPaymentId] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analyzePayment = async () => {
    if (!paymentId.trim()) {
      setError("Enter a payment ID.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const response = await fetch(
        `${API_URL}/payments/${paymentId.trim()}/analysis`
      );

      if (!response.ok) {
        throw new Error("Payment not found.");
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Resolve</h1>
          <p>Payment Event Investigation Engine</p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Operational
        </div>
      </header>

      <main className="container">

        <section className="hero">
          <div>
            <h2>Investigate Payment Events</h2>
            <p>
              Reconstruct payment state, detect conflicts, and investigate
              anomalies with bounded AI.
            </p>
          </div>

          <div className="search-box">
            <input
              type="text"
              placeholder="Enter payment ID..."
              value={paymentId}
              onChange={(e) => setPaymentId(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") analyzePayment();
              }}
            />

            <button onClick={analyzePayment} disabled={loading}>
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>

          {error && <div className="error">{error}</div>}
        </section>

        {analysis && (
          <>
            <section className="stats">
              <div className="stat-card">
                <span>Payment State</span>
                <strong>{analysis.current_state}</strong>
              </div>

              <div className="stat-card">
                <span>Events</span>
                <strong>{analysis.event_count}</strong>
              </div>

              <div className="stat-card">
                <span>Conflicts</span>
                <strong className={analysis.conflict_count > 0 ? "danger" : "success"}>
                  {analysis.conflict_count}
                </strong>
              </div>
            </section>

            <section className="panel">
              <div className="panel-header">
                <h3>Event Timeline</h3>
                <span>{analysis.payment_id}</span>
              </div>

              <div className="timeline">
                {analysis.investigation?.evidence?.map((event) => (
                  <div className="event" key={event.event_id}>
                    <div className="event-marker"></div>

                    <div>
                      <strong>{event.event_type}</strong>
                      <p>{event.event_id}</p>
                      <small>{event.event_timestamp}</small>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {analysis.conflicts?.length > 0 && (
              <section className="panel conflict-panel">
                <div className="panel-header">
                  <h3>⚠ Conflicts Detected</h3>
                  <span className="danger">
                    {analysis.conflict_count}
                  </span>
                </div>

                {analysis.conflicts.map((conflict, index) => (
                  <div className="conflict" key={index}>
                    <div>
                      <strong>{conflict.conflict_type}</strong>
                      <p>{conflict.message}</p>
                    </div>

                    <span className="severity">
                      {conflict.severity}
                    </span>
                  </div>
                ))}
              </section>
            )}

            {analysis.investigation && (
              <section className="panel ai-panel">
                <div className="panel-header">
                  <h3>🤖 AI Investigation</h3>
                  <span>Gemini</span>
                </div>

                <div className="ai-content">
                  <pre>
                    {analysis.investigation.summary}
                  </pre>

                  {analysis.investigation.recommendation && (
                    <div className="recommendation">
                      <strong>Recommendation</strong>
                      <p>
                        {analysis.investigation.recommendation}
                      </p>
                    </div>
                  )}
                </div>
              </section>
            )}
          </>
        )}

        {!analysis && !loading && (
          <section className="empty-state">
            <div className="empty-icon">⌕</div>
            <h3>Ready to investigate</h3>
            <p>
              Enter a payment ID above to reconstruct its event history
              and identify inconsistencies.
            </p>
          </section>
        )}

      </main>

      <footer>
        Resolve • Deterministic-first payment investigation
      </footer>
    </div>
  );
}

export default App;