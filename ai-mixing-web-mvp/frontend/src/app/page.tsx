"use client";

import { useMemo, useState } from "react";

import { AnalysisPanel } from "@/components/AnalysisPanel";
import { PreviewPanel } from "@/components/PreviewPanel";
import { TrackList } from "@/components/TrackList";
import { UploadPanel } from "@/components/UploadPanel";
import {
  analyzeTrack,
  applyLowHighCut,
  createProject,
  getProject,
  updateActionStatus,
  uploadTrack,
} from "@/lib/api";
import type {
  ActionSession,
  AnalysisSession,
  ProjectDetail,
  TrackSession,
} from "@/types/session";

export default function HomePage() {
  const [projectName, setProjectName] = useState("Hiphop Demo Mix");
  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [selectedTrackId, setSelectedTrackId] = useState<string | null>(null);
  const [analysisMap, setAnalysisMap] = useState<Record<string, AnalysisSession>>({});
  const [actionMap, setActionMap] = useState<Record<string, ActionSession>>({});
  const [message, setMessage] = useState("프로젝트를 생성한 뒤 WAV를 업로드하세요.");
  const [isBusy, setIsBusy] = useState(false);

  const selectedTrack = useMemo<TrackSession | null>(() => {
    if (!project || !selectedTrackId) return null;
    return project.tracks.find((track) => track.track_id === selectedTrackId) ?? null;
  }, [project, selectedTrackId]);

  const selectedAnalysis = selectedTrackId ? analysisMap[selectedTrackId] ?? null : null;
  const selectedAction = selectedTrackId ? actionMap[selectedTrackId] ?? null : null;

  async function refreshProject(projectId: string) {
    const detail = await getProject(projectId);
    setProject(detail);
  }

  async function handleCreateProject() {
    try {
      setIsBusy(true);
      const created = await createProject(projectName);
      await refreshProject(created.project_id);
      setMessage(`프로젝트 생성 완료: ${created.project_id}`);
    } catch (error) {
      setMessage(`프로젝트 생성 실패: ${String(error)}`);
    } finally {
      setIsBusy(false);
    }
  }

  async function handleUploadTrack() {
    if (!project || !pendingFile) {
      setMessage("프로젝트와 WAV 파일을 먼저 준비하세요.");
      return;
    }

    try {
      setIsBusy(true);
      const track = await uploadTrack(project.project_id, pendingFile);
      await refreshProject(project.project_id);
      setSelectedTrackId(track.track_id);
      setMessage(`업로드 완료: ${track.filename}`);
    } catch (error) {
      setMessage(`업로드 실패: ${String(error)}`);
    } finally {
      setIsBusy(false);
    }
  }

  async function handleAnalyzeTrack(trackId: string) {
    try {
      setIsBusy(true);
      const analysis = await analyzeTrack(trackId);
      setSelectedTrackId(trackId);
      setAnalysisMap((prev) => ({ ...prev, [trackId]: analysis }));
      await refreshProject(project!.project_id);
      setMessage(`분석 완료: ${trackId}`);
    } catch (error) {
      setMessage(`분석 실패: ${String(error)}`);
    } finally {
      setIsBusy(false);
    }
  }

  async function handleApplyLowHighCut(params: { low_cut_hz: number; high_cut_hz: number }) {
    if (!selectedTrackId) {
      setMessage("처리할 트랙을 먼저 선택하세요.");
      return;
    }

    try {
      setIsBusy(true);
      const action = await applyLowHighCut(selectedTrackId, params);
      setActionMap((prev) => ({ ...prev, [selectedTrackId]: action }));
      await refreshProject(project!.project_id);
      setMessage(`처리 완료: ${action.action_id}`);
    } catch (error) {
      setMessage(`처리 실패: ${String(error)}`);
    } finally {
      setIsBusy(false);
    }
  }

  async function handleUpdateActionStatus(status: "approved" | "cancelled") {
    if (!selectedAction) {
      setMessage("업데이트할 액션이 없습니다.");
      return;
    }

    try {
      setIsBusy(true);
      const updated = await updateActionStatus(selectedAction.action_id, status);
      setActionMap((prev) => ({ ...prev, [selectedAction.track_id]: updated }));
      await refreshProject(project!.project_id);
      setMessage(`액션 상태 변경 완료: ${updated.status}`);
    } catch (error) {
      setMessage(`액션 상태 변경 실패: ${String(error)}`);
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <main className="min-h-screen bg-ink px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl space-y-6">
        <header className="space-y-2">
          <p className="text-sm uppercase tracking-[0.24em] text-accent">AI Mixing Assistant Web MVP</p>
          <h1 className="text-4xl font-bold">Upload, Analyze, Process, Preview</h1>
          <p className="max-w-3xl text-slate-300">
            `mixing-extension`의 세션 구조를 참고한 테스트 프로젝트다. 완전한 웹 DAW가 아니라,
            WAV 업로드부터 분석과 Low / High Cut preview까지의 작은 검증 루프를 빠르게 확인한다.
          </p>
        </header>

        <div className="rounded-2xl border border-slate-700 bg-slate-900/50 px-5 py-4 text-sm text-slate-200">
          {message}
        </div>

        <UploadPanel
          projectName={projectName}
          onProjectNameChange={setProjectName}
          onCreateProject={handleCreateProject}
          onFileChange={setPendingFile}
          onUploadTrack={handleUploadTrack}
          hasProject={Boolean(project)}
          isBusy={isBusy}
        />

        <div className="grid gap-6 xl:grid-cols-[1.1fr_1fr]">
          <TrackList
            tracks={project?.tracks ?? []}
            selectedTrackId={selectedTrackId}
            onSelectTrack={setSelectedTrackId}
            onAnalyzeTrack={handleAnalyzeTrack}
            isBusy={isBusy}
          />
          <AnalysisPanel
            analysis={selectedAnalysis}
            selectedTrackId={selectedTrackId}
            onApply={handleApplyLowHighCut}
            isBusy={isBusy}
          />
        </div>

        <PreviewPanel
          track={selectedTrack}
          action={selectedAction}
          onApprove={() => handleUpdateActionStatus("approved")}
          onCancel={() => handleUpdateActionStatus("cancelled")}
          isBusy={isBusy}
        />

        {project && (
          <section className="rounded-2xl bg-panel p-6 shadow-lg">
            <h2 className="text-xl font-semibold">Project Snapshot</h2>
            <pre className="mt-4 overflow-x-auto rounded-xl bg-card p-4 text-xs text-slate-200">
              {JSON.stringify(project, null, 2)}
            </pre>
          </section>
        )}
      </div>
    </main>
  );
}
