"use client";

import { useState } from "react";

import type { AnalysisSession } from "@/types/session";

type AnalysisPanelProps = {
  analysis: AnalysisSession | null;
  selectedTrackId: string | null;
  onApply: (params: { low_cut_hz: number; high_cut_hz: number }) => void;
  isBusy: boolean;
};

export function AnalysisPanel({
  analysis,
  selectedTrackId,
  onApply,
  isBusy,
}: AnalysisPanelProps) {
  const [lowCutHz, setLowCutHz] = useState(80);
  const [highCutHz, setHighCutHz] = useState(18000);

  return (
    <section className="rounded-2xl bg-panel p-6 shadow-lg">
      <h2 className="text-xl font-semibold">Analysis + Low/High Cut</h2>

      <div className="mt-4 grid gap-6 lg:grid-cols-2">
        <div className="space-y-3 rounded-xl bg-card p-4">
          <h3 className="font-medium">Analysis Result</h3>
          {analysis ? (
            <ul className="space-y-2 text-sm text-slate-200">
              <li>duration_sec: {analysis.result.duration_sec}</li>
              <li>sample_rate: {analysis.result.sample_rate}</li>
              <li>channels: {analysis.result.channels}</li>
              <li>peak_dbfs: {analysis.result.peak_dbfs}</li>
              <li>rms_dbfs: {analysis.result.rms_dbfs}</li>
            </ul>
          ) : (
            <p className="text-sm text-slate-400">분석 결과가 아직 없습니다.</p>
          )}
        </div>

        <div className="space-y-4 rounded-xl bg-card p-4">
          <h3 className="font-medium">Low / High Cut</h3>
          <label className="block text-sm text-slate-300">
            Low Cut Hz
            <input
              className="mt-2 w-full rounded-lg border border-slate-600 bg-slate-900/40 px-4 py-3"
              type="number"
              value={lowCutHz}
              min={20}
              max={1000}
              onChange={(event) => setLowCutHz(Number(event.target.value))}
            />
          </label>
          <label className="block text-sm text-slate-300">
            High Cut Hz
            <input
              className="mt-2 w-full rounded-lg border border-slate-600 bg-slate-900/40 px-4 py-3"
              type="number"
              value={highCutHz}
              min={1000}
              max={22000}
              onChange={(event) => setHighCutHz(Number(event.target.value))}
            />
          </label>
          <button
            className="rounded-lg bg-accent px-4 py-2 font-medium text-slate-900 disabled:opacity-40"
            disabled={!selectedTrackId || isBusy}
            onClick={() => onApply({ low_cut_hz: lowCutHz, high_cut_hz: highCutHz })}
          >
            Apply Low / High Cut
          </button>
        </div>
      </div>
    </section>
  );
}

