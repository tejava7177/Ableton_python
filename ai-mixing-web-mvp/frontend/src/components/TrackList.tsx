"use client";

import type { TrackSession } from "@/types/session";

type TrackListProps = {
  tracks: TrackSession[];
  selectedTrackId: string | null;
  onSelectTrack: (trackId: string) => void;
  onAnalyzeTrack: (trackId: string) => void;
  isBusy: boolean;
};

export function TrackList({
  tracks,
  selectedTrackId,
  onSelectTrack,
  onAnalyzeTrack,
  isBusy,
}: TrackListProps) {
  return (
    <section className="rounded-2xl bg-panel p-6 shadow-lg">
      <h2 className="text-xl font-semibold">Track List</h2>
      <div className="mt-4 space-y-3">
        {tracks.length === 0 ? (
          <p className="text-sm text-slate-400">업로드된 트랙이 아직 없습니다.</p>
        ) : (
          tracks.map((track) => {
            const selected = track.track_id === selectedTrackId;
            return (
              <div
                key={track.track_id}
                className={`rounded-xl border p-4 ${
                  selected ? "border-accent bg-card" : "border-slate-700 bg-slate-900/40"
                }`}
              >
                <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <div>
                    <button
                      className="text-left text-base font-medium"
                      onClick={() => onSelectTrack(track.track_id)}
                    >
                      {track.filename}
                    </button>
                    <p className="text-sm text-slate-400">status: {track.status}</p>
                  </div>
                  <button
                    className="rounded-lg border border-slate-500 px-4 py-2 text-sm font-medium disabled:opacity-40"
                    onClick={() => onAnalyzeTrack(track.track_id)}
                    disabled={isBusy}
                  >
                    Analyze
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}

