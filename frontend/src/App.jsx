import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [paymentId, setPaymentId] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [aiInvestigated, setAiInvestigated] = useState(false);

  // --------------------------------------------------
  // FAST DETERMINISTIC ANALYSIS
  // --------------------------------------------------

  const analyzePayment = async () => {
    if (!paymentId.trim()) {
      setError("Enter a payment ID.");
      return;
    }

    setLoading(true);
    setError("");
    setAnalysis(null);

    // IMPORTANT:
    // Initial analysis does NOT call Gemini.
    setAiInvestigated(false);

    try {
      const response = await fetch(
        `${API_URL}/payments/${paymentId.trim()}/analysis?include_ai=false`
      );

      if (!response.ok) {
        throw new Error("Payment not found.");
      }

      const data = await response.json();

      setAnalysis(data);

      // DO NOT set aiInvestigated(true) here.
      // AI has not been called yet.
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Unable to connect to Resolve backend."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // GEMINI INVESTIGATION
  // --------------------------------------------------

  const investigateWithAI = async () => {
    if (!analysis) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/payments/${analysis.payment_id}/analysis?include_ai=true`
      );

      if (!response.ok) {
        throw new Error("AI investigation failed.");
      }

      const data = await response.json();

      setAnalysis(data);

      // AI has now actually been called.
      setAiInvestigated(true);
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Unable to connect to Resolve backend."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // AI RESPONSE PARSER
  // --------------------------------------------------

  const parseAI = (text = "") => {
    const summaryMatch = text.match(
      /SUMMARY:\s*([\s\S]*?)(?=\n\s*ROOT CAUSE:|$)/i
    );

    const rootCauseMatch = text.match(
      /ROOT CAUSE:\s*([\s\S]*?)(?=\n\s*RECOMMENDATION:|$)/i
    );

    const recommendationMatch = text.match(
      /RECOMMENDATION:\s*([\s\S]*)/i
    );

    return {
      summary: summaryMatch?.[1]?.trim() || text,
      rootCause: rootCauseMatch?.[1]?.trim() || "",
      recommendation:
        recommendationMatch?.[1]?.trim() || "",
    };
  };

  const ai = parseAI(
    analysis?.investigation?.summary || ""
  );

  const hasConflict = analysis?.conflict_count > 0;

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <div className="app">

      {/* HEADER */}
      <header className="topbar">
        <div className="brand">
          <div className="logo">R</div>

          <div>
            <h1>Resolve</h1>
            <p>Payment Event Investigation Engine</p>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          System Operational
        </div>
      </header>

      <main className="container">

        {/* HERO */}
        <section className="hero">
          <div>
            <div className="eyebrow">
              PAYMENT INTELLIGENCE
            </div>

            <h2>
              Investigate payment events.
              <br />
              <span>Resolve inconsistencies.</span>
            </h2>

            <p>
              Reconstruct payment state, detect event conflicts,
              collect evidence, and generate bounded AI-assisted
              investigations.
            </p>
          </div>

          {/* SEARCH */}
          <div className="search-card">
            <label>PAYMENT ID</label>

            <div className="search-box">
              <input
                type="text"
                placeholder="pay_578704b8"
                value={paymentId}
                onChange={(e) => setPaymentId(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    analyzePayment();
                  }
                }}
              />

              <button
                onClick={analyzePayment}
                disabled={loading}
              >
                {loading
                  ? "Analyzing..."
                  : "Analyze Payment"}
              </button>
            </div>

            {error && (
              <div className="error">
                <span>⚠</span>
                {error}
              </div>
            )}
          </div>
        </section>

        {/* EMPTY STATE */}
        {!analysis && !loading && (
          <section className="empty-state">
            <div className="empty-icon">⌕</div>

            <h3>Ready to investigate</h3>

            <p>
              Enter a payment ID above to reconstruct its
              event history and identify inconsistencies.
            </p>

            <div className="capabilities">
              <span>State Reconstruction</span>
              <span>Conflict Detection</span>
              <span>AI Investigation</span>
            </div>
          </section>
        )}

        {/* LOADING */}
        {loading && (
          <section className="loading-state">
            <div className="loader"></div>

            <h3>
              {aiInvestigated
                ? "Investigating with Gemini..."
                : "Analyzing payment..."}
            </h3>

            <p>
              {aiInvestigated
                ? "Gemini is investigating the detected payment inconsistency."
                : "Reconstructing event history and analyzing payment state."}
            </p>
          </section>
        )}

        {/* RESULTS */}
        {analysis && !loading && (
          <div className="results">

            {/* SUMMARY CARDS */}
            <section className="stats">

              <div className="stat-card">
                <div className="stat-label">
                  CURRENT STATE
                </div>

                <div className="stat-value state">
                  {analysis.current_state}
                </div>

                <div className="stat-description">
                  Reconstructed payment state
                </div>
              </div>

              <div className="stat-card">
                <div className="stat-label">
                  EVENTS
                </div>

                <div className="stat-value">
                  {analysis.event_count}
                </div>

                <div className="stat-description">
                  Events observed
                </div>
              </div>

              <div
                className={`stat-card ${
                  hasConflict ? "conflict-stat" : ""
                }`}
              >
                <div className="stat-label">
                  CONFLICTS
                </div>

                <div
                  className={`stat-value ${
                    hasConflict ? "danger" : "success"
                  }`}
                >
                  {analysis.conflict_count}
                </div>

                <div className="stat-description">
                  {hasConflict
                    ? "Investigation required"
                    : "No inconsistencies detected"}
                </div>
              </div>

            </section>

            {/* PAYMENT IDENTIFIER */}
            <div className="payment-heading">
              <div>
                <div className="section-eyebrow">
                  PAYMENT INVESTIGATION
                </div>

                <h3>{analysis.payment_id}</h3>
              </div>

              <div
                className={`result-badge ${
                  hasConflict
                    ? "badge-danger"
                    : "badge-success"
                }`}
              >
                {hasConflict
                  ? "CONFLICT DETECTED"
                  : "NO CONFLICT"}
              </div>
            </div>

            {/* EVENT TIMELINE */}
            <section className="panel">
              <div className="panel-header">
                <div>
                  <div className="section-eyebrow">
                    EVENT HISTORY
                  </div>

                  <h3>Payment Timeline</h3>
                </div>

                <span className="event-count">
                  {analysis.event_count} events
                </span>
              </div>

              <div className="timeline">
                {analysis.investigation?.evidence?.map(
                  (event, index) => (
                    <div
                      className="timeline-item"
                      key={event.event_id}
                    >
                      <div className="timeline-line">
                        <div className="timeline-dot">
                          {index + 1}
                        </div>
                      </div>

                      <div className="event-card">
                        <div className="event-top">
                          <strong>
                            {event.event_type}
                          </strong>

                          <span>
                            {event.event_timestamp}
                          </span>
                        </div>

                        <div className="event-id">
                          {event.event_id}
                        </div>
                      </div>
                    </div>
                  )
                )}
              </div>
            </section>

            {/* CONFLICTS */}
            {hasConflict && (
              <section className="panel conflict-panel">

                <div className="panel-header">
                  <div>
                    <div className="section-eyebrow danger-text">
                      ATTENTION REQUIRED
                    </div>

                    <h3>Conflicts Detected</h3>
                  </div>

                  <span className="conflict-count">
                    {analysis.conflict_count}
                  </span>
                </div>

                {analysis.conflicts.map(
                  (conflict, index) => (
                    <div
                      className="conflict-card"
                      key={index}
                    >
                      <div className="conflict-icon">
                        !
                      </div>

                      <div className="conflict-info">
                        <div className="conflict-title">
                          {conflict.conflict_type}
                        </div>

                        <p>
                          {conflict.message}
                        </p>
                      </div>

                      <div className="severity">
                        {conflict.severity}
                      </div>
                    </div>
                  )
                )}

              </section>
            )}

            {/* AI INVESTIGATION */}
            <section className="panel ai-panel">

              {!aiInvestigated ? (
                <>
                  <div className="ai-header">

                    <div className="ai-title">
                      <div className="ai-icon">
                        ✦
                      </div>

                      <div>
                        <div className="section-eyebrow">
                          AI-ASSISTED ANALYSIS
                        </div>

                        <h3>Investigation</h3>
                      </div>
                    </div>

                    <div className="ai-provider">
                      Gemini
                    </div>

                  </div>

                  <div className="ai-card">
                    <div className="ai-card-label">
                      READY FOR AI INVESTIGATION
                    </div>

                    <p>
                      Resolve detected a payment inconsistency.
                      Run Gemini to investigate the evidence and
                      identify a likely root cause.
                    </p>

                    <button
                      className="ai-investigate-button"
                      onClick={investigateWithAI}
                      disabled={loading}
                    >
                      ✦ Investigate with AI
                    </button>
                  </div>

                  <div className="ai-disclaimer">
                    <span>ⓘ</span>
                    AI output is advisory. Resolve does not
                    automatically execute payment actions.
                  </div>
                </>
              ) : (
                <>
                  <div className="ai-header">

                    <div className="ai-title">
                      <div className="ai-icon">
                        ✦
                      </div>

                      <div>
                        <div className="section-eyebrow">
                          AI-ASSISTED ANALYSIS
                        </div>

                        <h3>Investigation</h3>
                      </div>
                    </div>

                    <div className="ai-provider">
                      Gemini
                    </div>

                  </div>

                  <div className="ai-grid">

                    <div className="ai-card">
                      <div className="ai-card-label">
                        SUMMARY
                      </div>

                      <p>{ai.summary}</p>
                    </div>

                    <div className="ai-card">
                      <div className="ai-card-label">
                        ROOT CAUSE
                      </div>

                      <p>
                        {ai.rootCause ||
                          analysis.investigation.root_cause}
                      </p>
                    </div>

                    <div className="ai-card recommendation-card">
                      <div className="ai-card-label">
                        RECOMMENDATION
                      </div>

                      <p>
                        {ai.recommendation ||
                          analysis.investigation.recommendation}
                      </p>
                    </div>

                  </div>

                  <div className="ai-disclaimer">
                    <span>ⓘ</span>
                    AI output is advisory. Resolve does not
                    automatically execute payment actions.
                  </div>
                </>
              )}

            </section>

          </div>
        )}

      </main>

      <footer>
        <span>RESOLVE</span>
        <span>Deterministic-first payment intelligence</span>
      </footer>

    </div>
  );
}

export default App;