function ResultCard({ result }) {
  return (
    <div className="app-panel">
      <h2 className="app-title">Latest Case Summary</h2>
      <p className="app-copy">A coordinator-friendly summary of the latest AI decision.</p>

      {result ? (
        <div className="mt-5 grid gap-4">
          <div className="app-subpanel">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-500 dark:text-cyan-300">Issue Summary</p>
            <h3 className="mt-2 text-xl font-bold text-slate-950 dark:text-white">{result.headline}</h3>
            <p className="mt-2 text-sm text-slate-700 dark:text-slate-300">{result.issue} affecting {result.affected_summary}.</p>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <InfoCard label="Location" value={result.location} />
            <InfoCard label="Urgency" value={capitalize(result.urgency)} />
            <InfoCard label="Priority" value={result.priority} />
            <InfoCard label="Assigned Volunteer" value={result.assigned_volunteer} />
            <InfoCard label="Recommended Action" value={result.recommended_action} />
            <InfoCard label="Status" value={result.status} />
          </div>

          <div className="app-subpanel">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-500 dark:text-cyan-300">Report Details</p>
            <p className="mt-2 text-sm text-slate-700 dark:text-slate-300">
              Confidence: {result.confidence} | Volunteer match: {result.volunteer_confidence}
            </p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
              Source: {(result.source_labels || []).join(", ") || "Direct report"} | Score: {result.priority_score}
            </p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
              AI service: {result.ai_service_used || "Rule-based NLP fallback"}
            </p>
          </div>
        </div>
      ) : (
        <div className="mt-5 app-subpanel">
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Submit a report to see a clear result with issue, location, urgency, priority, volunteer assignment, and source summary.
          </p>
        </div>
      )}
    </div>
  );
}

function InfoCard({ label, value }) {
  return (
    <div className="app-subpanel">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-2 text-sm font-medium text-slate-900 dark:text-white">{value || "Pending"}</p>
    </div>
  );
}

function capitalize(value) {
  if (!value) {
    return "Pending";
  }
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export default ResultCard;
