"use client";

import type { ActionSession, TrackSession } from "@/types/session";

type PreviewPanelProps = {
  track: TrackSession | null;
  action: ActionSession | null;
  onApprove: () => void;
  onCancel: () => void;
  isBusy: boolean;
};

export function PreviewPanel({ track, action, onApprove, onCancel, isBusy }: PreviewPanelProps) {
  return (
    <section className="rounded-2xl bg-panel p-6 shadow-lg">
      <h2 className="text-xl font-semibold">Before / After Preview</h2>
      <div className="mt-4 grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl bg-card p-4">
          <h3 className="font-medium">Original</h3>
          {track ? (
            <audio className="mt-3 w-full" controls src={track.file_url}>
              Your browser does not support audio playback.
            </audio>
          ) : (
            <p className="mt-3 text-sm text-slate-400">선택된 원본 트랙이 없습니다.</p>
          )}
        </div>

        <div className="rounded-xl bg-card p-4">
          <h3 className="font-medium">Processed</h3>
          {action?.processed_file_url ? (
            <>
              <audio className="mt-3 w-full" controls src={action.processed_file_url}>
                Your browser does not support audio playback.
              </audio>
              <p className="mt-2 text-sm text-slate-300">action status: {action.status}</p>
              <p className="mt-2 text-xs text-slate-400">{action.processed_file_url}</p>
              <div className="mt-4 flex gap-3">
                <button
                  className="rounded-lg bg-accent px-4 py-2 font-medium text-slate-900 disabled:opacity-40"
                  onClick={onApprove}
                  disabled={isBusy}
                >
                  Approve
                </button>
                <button
                  className="rounded-lg border border-slate-500 px-4 py-2 font-medium disabled:opacity-40"
                  onClick={onCancel}
                  disabled={isBusy}
                >
                  Cancel
                </button>
              </div>
            </>
          ) : (
            <p className="mt-3 text-sm text-slate-400">처리된 파일이 아직 없습니다.</p>
          )}
        </div>
      </div>
    </section>
  );
}
