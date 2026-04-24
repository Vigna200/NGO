function VolunteerPanel({ volunteers, tasks }) {
  return (
    <div className="app-panel">
      <h2 className="app-title">Volunteer Team</h2>
      <p className="app-copy">Available responders and the cases currently under them.</p>
      <div className="mt-5 grid gap-3">
        {volunteers.map((volunteer) => (
          <article className="app-subpanel" key={volunteer.id}>
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-lg font-semibold text-slate-950 dark:text-white">{volunteer.name}</h3>
              <span
                className={
                  volunteer.availability
                    ? "rounded-full bg-emerald-400/20 px-3 py-1 text-xs font-bold text-emerald-300"
                    : "rounded-full bg-rose-400/20 px-3 py-1 text-xs font-bold text-rose-300"
                }
              >
                {volunteer.availability ? "Available" : "Busy"}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">{volunteer.location}</p>
            <p className="mt-2 text-sm text-slate-700 dark:text-slate-300">{volunteer.skills.join(", ")}</p>
            <div className="mt-4 border-t border-slate-200 pt-3 dark:border-slate-800">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
                Assigned Tasks
              </p>
              <div className="mt-2 grid gap-2">
                {tasksForVolunteer(tasks, volunteer.id).length ? (
                  tasksForVolunteer(tasks, volunteer.id).map((task) => (
                    <div className="rounded-xl bg-white px-3 py-2 text-sm text-slate-700 dark:bg-slate-900 dark:text-slate-300" key={task.id}>
                      <div className="font-medium text-slate-900 dark:text-white">{task.headline || task.task}</div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        {task.priority} | {task.status} | {task.location}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-slate-500 dark:text-slate-400">No tasks assigned yet.</p>
                )}
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}

function tasksForVolunteer(tasks, volunteerId) {
  return (tasks || []).filter((task) => task.assigned_volunteer_id === volunteerId);
}

export default VolunteerPanel;
