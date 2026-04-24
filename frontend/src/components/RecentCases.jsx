function RecentCases({ cases }) {
  return (
    <div className="app-panel">
      <h2 className="app-title">Recent Reports</h2>
      <p className="app-copy">The latest processed reports in plain language for fast review.</p>
      <div className="mt-5 grid gap-3">
        {cases.length ? (
          cases.map((item) => (
            <article className="app-subpanel" key={item.case_id}>
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-cyan-500 dark:text-cyan-300">{item.issue || item.category}</h3>
                <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-bold text-white">{item.priority}</span>
              </div>
              <p className="mt-3 text-base font-semibold text-slate-900 dark:text-white">{item.headline || item.task}</p>
              <p className="mt-2 text-sm text-slate-700 dark:text-slate-300">{item.clean_extracted_text}</p>
              <p className="mt-3 text-sm text-slate-500 dark:text-slate-500">
                {item.location} | {item.people_affected} affected | {item.assigned_volunteer} | {item.source_count || 1} source
                {(item.source_count || 1) > 1 ? "s" : ""}
              </p>
            </article>
          ))
        ) : (
          <p className="rounded-2xl border border-dashed border-slate-300 p-6 text-sm text-slate-500 dark:border-slate-700">
            Processed cases will appear here after the first upload.
          </p>
        )}
      </div>
    </div>
  );
}

export default RecentCases;
