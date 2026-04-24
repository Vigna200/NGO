function SourceOpsPanel({ handleSyncSources, syncingSources, latestSyncSummary }) {
  return (
    <div className="app-panel">
      <h2 className="app-title">Optional External Alerts</h2>
      <p className="app-copy">
        This is optional. The core workflow is still direct NGO and field-team reporting.
      </p>

      <div className="mt-5 grid gap-3">
        <div className="app-subpanel">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-500 dark:text-cyan-300">When to use it</p>
          <ul className="mt-3 space-y-2 text-sm text-slate-700 dark:text-slate-300">
            <li>Pull extra public alerts when your team wants a broader view</li>
            <li>Convert them into the same case format as direct reports</li>
            <li>Use them as supporting evidence, not as the main workflow</li>
          </ul>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        <button
          className="rounded-2xl bg-slate-950 px-4 py-3 text-sm font-bold text-white transition hover:bg-slate-800 disabled:opacity-60 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-200"
          type="button"
          disabled={syncingSources}
          onClick={handleSyncSources}
        >
          {syncingSources ? "Checking external alerts..." : "Fetch External Alerts"}
        </button>
      </div>

      {latestSyncSummary ? (
        <div className="mt-5 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-700 dark:text-emerald-100">
          Checked {latestSyncSummary.sources_processed} external entries and added{" "}
          {latestSyncSummary.results?.length || 0} new cases to the dashboard.
        </div>
      ) : null}
    </div>
  );
}

export default SourceOpsPanel;
