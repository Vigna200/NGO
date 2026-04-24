function AnalyticsPanel({ dashboard }) {
  const items = Object.entries(dashboard.priority_breakdown || {});
  const total = items.reduce((sum, [, count]) => sum + count, 0);
  const topLocations = (dashboard.location_needs || []).slice(0, 3);
  const openTasks = dashboard.summary.open_tasks || 0;
  const coverage = dashboard.summary.volunteer_coverage || 0;
  const criticalFocus = (dashboard.summary.very_high_priority_tasks || 0) + (dashboard.summary.high_priority_tasks || 0);

  return (
    <div className="app-panel">
      <h2 className="app-title">Response Highlights</h2>
      <p className="app-copy">A short operational snapshot for coordinators and field leads.</p>

      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <HighlightCard label="Open work" value={openTasks} note="Cases still needing follow-through" />
        <HighlightCard label="Critical focus" value={criticalFocus} note="Very high + high priority cases" />
        <HighlightCard label="Volunteer coverage" value={`${coverage}%`} note="Tasks already assigned to someone" />
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="app-subpanel">
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Priority split</h3>
          <div className="mt-4 flex items-center gap-5">
            <div className="relative flex h-32 w-32 items-center justify-center rounded-full bg-[conic-gradient(#ef4444_0deg_110deg,#f59e0b_110deg_220deg,#06b6d4_220deg_300deg,#22c55e_300deg_360deg)]">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-white text-center text-xs font-semibold text-slate-700 dark:bg-slate-900 dark:text-slate-200">
                {total}
                <br />
                tasks
              </div>
            </div>
            <div className="grid flex-1 gap-3">
              {items.map(([priority, count]) => (
                <PriorityRow key={priority} priority={priority} count={count} total={total} />
              ))}
            </div>
          </div>
        </div>

        <div className="app-subpanel">
          <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate-400">Where help is needed most</h3>
          <div className="mt-4 grid gap-3">
            {topLocations.length ? (
              topLocations.map((item, index) => (
                <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900" key={item.location}>
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm font-semibold text-slate-900 dark:text-white">
                      {index + 1}. {item.location}
                    </span>
                    <span className="text-xs font-bold uppercase tracking-[0.18em] text-cyan-600 dark:text-cyan-300">
                      {item.needs_count} needs
                    </span>
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-slate-200 dark:bg-slate-800">
                    <div
                      className="h-2 rounded-full bg-cyan-500"
                      style={{ width: `${Math.max(18, Math.min(100, item.needs_count * 18))}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500 dark:text-slate-500">Location highlights will appear after the first report is processed.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function HighlightCard({ label, value, note }) {
  return (
    <div className="app-subpanel">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">{label}</p>
      <p className="mt-3 text-3xl font-black text-slate-950 dark:text-white">{value}</p>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{note}</p>
    </div>
  );
}

function PriorityRow({ priority, count, total }) {
  const percentage = total ? Math.round((count / total) * 100) : 0;
  const tone =
    priority === "Very High"
      ? "bg-rose-500"
      : priority === "High"
        ? "bg-amber-500"
        : priority === "Medium"
          ? "bg-cyan-500"
          : "bg-emerald-500";

  return (
    <div>
      <div className="flex items-center justify-between text-sm text-slate-700 dark:text-slate-300">
        <span>{priority}</span>
        <span>{count} cases</span>
      </div>
      <div className="mt-2 h-2 rounded-full bg-slate-200 dark:bg-slate-800">
        <div className={`h-2 rounded-full ${tone}`} style={{ width: `${Math.max(10, percentage)}%` }} />
      </div>
    </div>
  );
}

export default AnalyticsPanel;
