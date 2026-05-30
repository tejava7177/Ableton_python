import type {
  ActionSession,
  AnalysisSession,
  EqBand,
  ProjectDetail,
  ProjectSession,
  TrackSession,
} from "@/types/session";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function createProject(name: string): Promise<ProjectSession> {
  const response = await fetch(`${API_BASE}/api/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  return parseJson<ProjectSession>(response);
}

export async function getProject(projectId: string): Promise<ProjectDetail> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}`, { cache: "no-store" });
  return parseJson<ProjectDetail>(response);
}

export async function uploadTrack(projectId: string, file: File): Promise<TrackSession> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/projects/${projectId}/tracks`, {
    method: "POST",
    body: formData,
  });
  return parseJson<TrackSession>(response);
}

export async function listTracks(projectId: string): Promise<TrackSession[]> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/tracks`, { cache: "no-store" });
  return parseJson<TrackSession[]>(response);
}

export async function analyzeTrack(trackId: string): Promise<AnalysisSession> {
  const response = await fetch(`${API_BASE}/api/tracks/${trackId}/analysis`, {
    method: "POST",
  });
  return parseJson<AnalysisSession>(response);
}

export async function applyLowHighCut(
  trackId: string,
  params: { low_cut_hz: number; high_cut_hz: number },
): Promise<ActionSession> {
  const response = await fetch(`${API_BASE}/api/tracks/${trackId}/actions/low-high-cut`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return parseJson<ActionSession>(response);
}

export async function applyChannelEq(
  trackId: string,
  params: { low_cut_hz: number; high_cut_hz: number; bands: EqBand[] },
): Promise<ActionSession> {
  const response = await fetch(`${API_BASE}/api/tracks/${trackId}/actions/channel-eq`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  return parseJson<ActionSession>(response);
}

export async function updateActionStatus(
  actionId: string,
  status: "pending" | "completed" | "approved" | "cancelled",
): Promise<ActionSession> {
  const response = await fetch(`${API_BASE}/api/actions/${actionId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  return parseJson<ActionSession>(response);
}

export { API_BASE };
