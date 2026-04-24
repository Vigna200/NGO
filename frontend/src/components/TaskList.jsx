const TASK_STATUSES = ["Action Required", "Assigned", "In Progress", "Completed"];

function TaskList({ tasks, volunteers, assignmentState, setAssignmentState, handleAssign, handleStatus }) {
  return (
    <div className="app-panel">
      <h2 className="app-title">Dashboard: Priority Tasks</h2>
      <p className="app-copy">Manage needs, volunteers, and task progress in real time.</p>
      <div className="mt-5 grid gap-4">
        {tasks.length ? (
          tasks
            .slice()
            .reverse()
            .map((task) => (
              <article className="app-subpanel" key={task.id}>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-sm uppercase tracking-[0.25em] text-slate-500 dark:text-slate-500">{task.issue || task.category}</p>
                    <h3 className="mt-1 text-lg font-semibold text-slate-950 dark:text-white">{task.headline || task.task}</h3>
                  </div>
                  <span className={priorityBadge(task.priority)}>{task.priority}</span>
                </div>
                <div className="mt-4 grid gap-2 text-sm text-slate-700 dark:text-slate-300 md:grid-cols-2">
                  <p>Location: {task.location}</p>
                  <p>People affected: {task.people_affected}</p>
                  <p>Assigned volunteer: {task.assigned_to}</p>
                  <p>Status: {task.status}</p>
                  <p>Action: {task.task}</p>
                  <p>Confidence: {task.confidence || "Medium"}</p>
                </div>
                <div className="mt-4 flex flex-col gap-3 lg:flex-row">
                  <select
                    className="flex-1 rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none focus:border-cyan-400 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                    value={assignmentState[task.id] || ""}
                    onChange={(event) =>
                      setAssignmentState((current) => ({
                        ...current,
                        [task.id]: event.target.value,
                      }))
                    }
                  >
                    <option value="">Select volunteer</option>
                    {volunteers.map((volunteer) => (
                      <option key={volunteer.id} value={volunteer.id}>
                        {volunteer.name} - {volunteer.location}
                      </option>
                    ))}
                  </select>
                  <button
                    className="rounded-xl bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-white"
                    type="button"
                    onClick={() => handleAssign(task.id)}
                  >
                    Assign Volunteer
                  </button>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {TASK_STATUSES.map((status) => (
                    <button
                      className={
                        task.status === status
                          ? "rounded-full bg-emerald-400 px-3 py-1 text-xs font-bold text-slate-950"
                          : "rounded-full border border-slate-300 px-3 py-1 text-xs font-semibold text-slate-700 dark:border-slate-700 dark:text-slate-300"
                      }
                      key={status}
                      type="button"
                      onClick={() => handleStatus(task.id, status)}
                    >
                      {status}
                    </button>
                  ))}
                </div>
              </article>
            ))
        ) : (
          <p className="rounded-2xl border border-dashed border-slate-300 p-6 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
            No tasks yet. Upload a report to create the first actionable item.
          </p>
        )}
      </div>
    </div>
  );
}

function priorityBadge(priority) {
  if (priority === "Very High") {
    return "rounded-full bg-fuchsia-400/20 px-3 py-1 text-xs font-bold text-fuchsia-300";
  }
  if (priority === "High") {
    return "rounded-full bg-rose-400/20 px-3 py-1 text-xs font-bold text-rose-300";
  }
  if (priority === "Medium") {
    return "rounded-full bg-amber-400/20 px-3 py-1 text-xs font-bold text-amber-300";
  }
  return "rounded-full bg-emerald-400/20 px-3 py-1 text-xs font-bold text-emerald-300";
}

export default TaskList;
