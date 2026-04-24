const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000";

async function parseResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    throw new Error(typeof payload === "string" ? payload : payload?.error || "API request failed.");
  }

  return payload;
}

export async function fetchDashboardBundle() {
  const [tasks, volunteers, dashboard] = await Promise.all([
    fetch(`${API_BASE}/api/tasks`).then(parseResponse),
    fetch(`${API_BASE}/api/volunteers`).then(parseResponse),
    fetch(`${API_BASE}/api/dashboard`).then(parseResponse),
  ]);

  return {
    tasks: tasks.tasks || [],
    volunteers: volunteers.volunteers || [],
    dashboard,
  };
}

export async function uploadReport({ text, file }) {
  const formData = new FormData();
  if (text?.trim()) {
    formData.append("text", text.trim());
  }
  if (file) {
    formData.append("file", file);
  }

  return fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  }).then(parseResponse);
}

export async function syncExternalSources() {
  return fetch(`${API_BASE}/api/monitor/sync`, {
    method: "POST",
  }).then(parseResponse);
}

export async function assignVolunteer(taskId, volunteerId) {
  return fetch(`${API_BASE}/api/assign`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task_id: taskId, volunteer_id: volunteerId }),
  }).then(parseResponse);
}

export async function updateTaskStatus(taskId, status) {
  return fetch(`${API_BASE}/api/tasks/${taskId}/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  }).then(parseResponse);
}

export { API_BASE };
