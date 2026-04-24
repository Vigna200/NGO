import { useEffect, useState } from "react";

import AnalyticsPanel from "./components/AnalyticsPanel";
import RecentCases from "./components/RecentCases";
import ResultCard from "./components/ResultCard";
import SourceOpsPanel from "./components/SourceOpsPanel";
import TaskList from "./components/TaskList";
import UploadForm from "./components/UploadForm";
import VolunteerPanel from "./components/VolunteerPanel";
import {
  API_BASE,
  assignVolunteer,
  fetchDashboardBundle,
  syncExternalSources,
  updateTaskStatus,
  uploadReport,
} from "./api";

function App() {
  const [theme, setTheme] = useState(() => {
    if (typeof window === "undefined") {
      return "dark";
    }
    return window.localStorage.getItem("ngo-theme") || "dark";
  });
  const [rawText, setRawText] = useState(
    "Critical food shortage in Village A affecting 150 people. Immediate support required."
  );
  const [selectedFile, setSelectedFile] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [volunteers, setVolunteers] = useState([]);
  const [dashboard, setDashboard] = useState({
    summary: {},
    priority_breakdown: {},
    location_needs: [],
    recent_cases: [],
  });
  const [result, setResult] = useState(null);
  const [assignmentState, setAssignmentState] = useState({});
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncingSources, setSyncingSources] = useState(false);
  const [latestSyncSummary, setLatestSyncSummary] = useState(null);

  async function refreshDashboard({ silent = false } = {}) {
    if (!silent) {
      setSyncing(true);
    }

    try {
      const bundle = await fetchDashboardBundle();
      setTasks(bundle.tasks);
      setVolunteers(bundle.volunteers);
      setDashboard(bundle.dashboard);
      setError("");
    } catch (refreshError) {
      setError(refreshError.message);
    } finally {
      if (!silent) {
        setSyncing(false);
      }
    }
  }

  useEffect(() => {
    refreshDashboard();
  }, []);

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.toggle("dark", theme === "dark");
    window.localStorage.setItem("ngo-theme", theme);
  }, [theme]);

  useEffect(() => {
    const nextState = {};
    tasks.forEach((task) => {
      nextState[task.id] = task.assigned_volunteer_id || "";
    });
    setAssignmentState(nextState);
  }, [tasks]);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      if (!document.hidden) {
        refreshDashboard({ silent: true });
      }
    }, 5000);

    return () => window.clearInterval(intervalId);
  }, []);

  async function handleUpload(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");

    try {
      const data = await uploadReport({ text: rawText, file: selectedFile });
      setResult(data.result || data);
      setRawText("");
      setSelectedFile(null);
      await refreshDashboard();
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAssign(taskId) {
    const volunteerId = assignmentState[taskId];
    if (!volunteerId) {
      setError("Select a volunteer before assigning.");
      return;
    }

    try {
      await assignVolunteer(taskId, volunteerId);
      await refreshDashboard();
    } catch (assignError) {
      setError(assignError.message);
    }
  }

  async function handleStatus(taskId, status) {
    try {
      await updateTaskStatus(taskId, status);
      await refreshDashboard();
    } catch (statusError) {
      setError(statusError.message);
    }
  }

  async function handleSyncSources() {
    setSyncingSources(true);
    setError("");

    try {
      const summary = await syncExternalSources();
      setLatestSyncSummary(summary);
      const newest = summary.results?.[0];
      if (newest) {
        setResult(newest);
      }
      await refreshDashboard();
    } catch (syncError) {
      setError(syncError.message);
    } finally {
      setSyncingSources(false);
    }
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.10),_transparent_26%),linear-gradient(180deg,_#f8fafc_0%,_#e2e8f0_100%)] text-slate-900 transition-colors dark:bg-[radial-gradient(circle_at_top_left,_rgba(34,211,238,0.14),_transparent_25%),linear-gradient(180deg,_#020617_0%,_#0f172a_100%)] dark:text-slate-50">
      <div className="mx-auto flex max-w-7xl flex-col gap-8 px-4 py-6 md:px-8">
        <Navbar theme={theme} onToggleTheme={() => setTheme((current) => (current === "dark" ? "light" : "dark"))} />

        <header
          id="overview"
          className="app-panel border-cyan-500/20 shadow-2xl shadow-cyan-200/30 dark:shadow-cyan-950/30"
        >
          <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
            <div className="max-w-3xl">
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">Community Response OS</p>
              <h1 className="mt-3 text-4xl font-black tracking-tight text-slate-950 md:text-6xl dark:text-white">
                Turn scattered field reports into urgent local action.
              </h1>
              <p className="mt-4 max-w-2xl text-base text-slate-600 md:text-lg dark:text-slate-300">
                Local groups and NGOs often collect paper surveys, field notes, and informal reports in
                many places. This dashboard brings that information together, highlights the most urgent
                needs, and helps teams assign the right volunteer faster.
              </p>
            </div>
            <div className="grid gap-3 text-sm text-slate-600 dark:text-slate-300">
              <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-4 py-2">
                {syncing ? "Syncing live data..." : "Live polling every 5 seconds"}
              </div>
              <div>API: {API_BASE}</div>
              <div>Mode: {dashboard.database_mode || "loading"}</div>
              <div>
                Last update:
                {" "}
                {dashboard.last_updated ? new Date(dashboard.last_updated).toLocaleString() : "Waiting for data"}
              </div>
            </div>
          </div>
        </header>

        {error ? (
          <div className="rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {error}
          </div>
        ) : null}

        <section className="grid gap-4 lg:grid-cols-3">
          <ProblemCard
            title="Scattered Reports"
            body="Community needs are often buried in paper surveys, PDFs, messages, and field updates, so the biggest problems are easy to miss."
          />
          <ProblemCard
            title="Clear Priority"
            body="The system extracts the issue, location, people affected, and urgency so coordinators can quickly see what needs action first."
          />
          <ProblemCard
            title="Volunteer Matching"
            body="Each case is turned into an action task and matched to a volunteer based on skills, availability, and local fit."
          />
        </section>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-6">
          <StatCard label="Total Tasks" value={dashboard.summary.total_tasks || 0} accent="cyan" />
          <StatCard label="Open Tasks" value={dashboard.summary.open_tasks || 0} accent="amber" />
          <StatCard label="Very High" value={dashboard.summary.very_high_priority_tasks || 0} accent="rose" />
          <StatCard label="Completed" value={dashboard.summary.completed_tasks || 0} accent="emerald" />
          <StatCard label="People Impacted" value={dashboard.summary.people_impacted || 0} accent="amber" />
          <StatCard label="Volunteers Ready" value={dashboard.summary.volunteers_available || 0} accent="emerald" />
          <StatCard label="Volunteer Coverage" value={`${dashboard.summary.volunteer_coverage || 0}%`} accent="violet" />
        </section>

        <section id="ingestion" className="grid gap-3">
          <SectionHeading
            eyebrow="Ingestion + Extraction"
            title="Submit a report and get a clear case summary"
            body="Upload text, PDFs, or images from the field. The AI engine will extract the main issue, count the people affected, estimate urgency, and prepare the next action."
          />
        </section>

        <section className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <UploadForm
            rawText={rawText}
            setRawText={setRawText}
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            handleUpload={handleUpload}
            submitting={submitting}
          />
          <ResultCard result={result} />
        </section>

        <section id="dashboard" className="grid gap-3">
          <SectionHeading
            eyebrow="Response Dashboard"
            title="See the biggest local needs clearly"
            body="Review open cases, assign volunteers, and move work from action required to completed without digging through scattered records."
          />
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.86fr_1.14fr]">
          <VolunteerPanel volunteers={volunteers} tasks={tasks} />
          <TaskList
            tasks={tasks}
            volunteers={volunteers}
            assignmentState={assignmentState}
            setAssignmentState={setAssignmentState}
            handleAssign={handleAssign}
            handleStatus={handleStatus}
          />
        </section>

        <section id="analytics" className="grid gap-3">
          <SectionHeading
            eyebrow="Highlights"
            title="Short, visual view of the response picture"
            body="A quick summary of where pressure is building, which priorities are dominating, and what the response team should focus on next."
          />
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
          <AnalyticsPanel dashboard={dashboard} />
          <RecentCases cases={dashboard.recent_cases || []} />
        </section>

        <section className="grid gap-3">
          <SectionHeading
            eyebrow="Optional"
            title="External monitoring support"
            body="The app works fully with direct NGO reports. If you want, you can also pull extra public alerts into the same dashboard."
          />
        </section>

        <section className="grid gap-6 xl:grid-cols-1">
          <SourceOpsPanel
            handleSyncSources={handleSyncSources}
            syncingSources={syncingSources}
            latestSyncSummary={latestSyncSummary}
          />
        </section>
      </div>
    </div>
  );
}

function StatCard({ label, value, accent }) {
  const palette = {
    cyan: "border-cyan-300 bg-cyan-100/80 text-cyan-700 dark:border-cyan-400/20 dark:bg-cyan-400/10 dark:text-cyan-200",
    rose: "border-rose-300 bg-rose-100/80 text-rose-700 dark:border-rose-400/20 dark:bg-rose-400/10 dark:text-rose-200",
    amber: "border-amber-300 bg-amber-100/80 text-amber-700 dark:border-amber-400/20 dark:bg-amber-400/10 dark:text-amber-200",
    emerald: "border-emerald-300 bg-emerald-100/80 text-emerald-700 dark:border-emerald-400/20 dark:bg-emerald-400/10 dark:text-emerald-200",
    violet: "border-violet-300 bg-violet-100/80 text-violet-700 dark:border-violet-400/20 dark:bg-violet-400/10 dark:text-violet-200",
  };

  return (
    <div className={`rounded-3xl border p-5 shadow-lg shadow-slate-200/60 dark:shadow-none ${palette[accent]}`}>
      <p className="text-sm uppercase tracking-[0.2em]">{label}</p>
      <p className="mt-4 text-4xl font-black text-slate-950 dark:text-white">{value}</p>
    </div>
  );
}

function Navbar({ theme, onToggleTheme }) {
  const links = [
    { label: "Overview", href: "#overview" },
    { label: "Ingestion", href: "#ingestion" },
    { label: "Dashboard", href: "#dashboard" },
    { label: "Analytics", href: "#analytics" },
  ];

  return (
    <nav className="sticky top-4 z-20 rounded-3xl border border-slate-200/80 bg-white/92 px-4 py-3 shadow-lg shadow-slate-300/25 backdrop-blur dark:border-slate-800 dark:bg-slate-900/85 dark:shadow-slate-950/40">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-cyan-500">NGO Navigator</p>
          <p className="text-sm text-slate-600 dark:text-slate-300">Scattered reports into focused local action</p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {links.map((link) => (
            <a
              key={link.href}
              className="rounded-full px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800"
              href={link.href}
            >
              {link.label}
            </a>
          ))}
          <button
            className="rounded-full border border-slate-200 bg-slate-100 px-4 py-2 text-sm font-semibold text-slate-800 transition hover:bg-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700"
            type="button"
            onClick={onToggleTheme}
          >
            {theme === "dark" ? "Bright Mode" : "Dark Mode"}
          </button>
        </div>
      </div>
    </nav>
  );
}

function ProblemCard({ title, body }) {
  return (
    <article className="app-panel p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-500">Why It Matters</p>
      <h2 className="mt-3 text-xl font-bold text-slate-950 dark:text-white">{title}</h2>
      <p className="mt-3 text-sm leading-6 text-slate-600 dark:text-slate-300">{body}</p>
    </article>
  );
}

function SectionHeading({ eyebrow, title, body }) {
  return (
    <div className="px-1">
      <p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-500">{eyebrow}</p>
      <h2 className="mt-2 text-2xl font-bold text-slate-950 dark:text-white">{title}</h2>
      <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-400">{body}</p>
    </div>
  );
}

export default App;
