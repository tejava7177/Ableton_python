"use client";

import type { PointerEvent as ReactPointerEvent, ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";

import type { ActionSession, AnalysisSession, EqBand } from "@/types/session";

type AnalysisPanelProps = {
  analysis: AnalysisSession | null;
  action: ActionSession | null;
  selectedTrackId: string | null;
  onApply: (params: { low_cut_hz: number; high_cut_hz: number; bands: EqBand[] }) => void;
  isBusy: boolean;
};

type DragTarget = "lowCut" | "highCut" | "band0" | "band1" | null;

const MIN_FREQ = 20;
const MAX_FREQ = 20000;
const MIN_DB = -18;
const MAX_DB = 18;
const VIEWBOX_WIDTH = 920;
const VIEWBOX_HEIGHT = 360;
const CURVE_BASELINE_DB = -18;
const FREQ_LABELS = [20, 30, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000];

const DEFAULT_BANDS: EqBand[] = [
  { frequency_hz: 180, gain_db: -3, q: 0.9, enabled: true },
  { frequency_hz: 2600, gain_db: 2.5, q: 1.2, enabled: true },
];

export function AnalysisPanel({
  analysis,
  action,
  selectedTrackId,
  onApply,
  isBusy,
}: AnalysisPanelProps) {
  const [lowCutHz, setLowCutHz] = useState(80);
  const [highCutHz, setHighCutHz] = useState(18000);
  const [bands, setBands] = useState<EqBand[]>(DEFAULT_BANDS);
  const [dragTarget, setDragTarget] = useState<DragTarget>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!action?.params) return;
    if (typeof action.params.low_cut_hz === "number") {
      setLowCutHz(action.params.low_cut_hz);
    }
    if (typeof action.params.high_cut_hz === "number") {
      setHighCutHz(action.params.high_cut_hz);
    }
    if (Array.isArray(action.params.bands) && action.params.bands.length > 0) {
      setBands(
        action.params.bands.slice(0, 2).map((band, index) => ({
          ...DEFAULT_BANDS[index],
          ...band,
        })),
      );
    }
  }, [action]);

  const graph = useMemo(() => {
    const curvePoints: string[] = [];
    const fillPoints: string[] = [];
    const spectrumPoints: string[] = [];

    for (let x = 0; x <= VIEWBOX_WIDTH; x += 5) {
      const freq = xToFreq(x);
      const responseDb = buildTotalResponseDb(freq, lowCutHz, highCutHz, bands);
      const y = dbToY(responseDb);
      curvePoints.push(`${x},${y}`);
      fillPoints.push(`${x},${y}`);

      const energy = mockSpectrumDb(freq, analysis?.result.rms_dbfs ?? -18, analysis?.result.peak_dbfs ?? -6);
      spectrumPoints.push(`${x},${dbToY(energy)}`);
    }

    fillPoints.push(`${VIEWBOX_WIDTH},${dbToY(CURVE_BASELINE_DB)}`);
    fillPoints.push(`0,${dbToY(CURVE_BASELINE_DB)}`);

    return {
      curvePath: curvePoints.join(" "),
      fillPolygon: fillPoints.join(" "),
      spectrumPath: spectrumPoints.join(" "),
      lowCutX: freqToX(lowCutHz),
      highCutX: freqToX(highCutHz),
      bandPoints: bands.map((band) => ({
        x: freqToX(band.frequency_hz),
        y: dbToY(band.gain_db),
      })),
    };
  }, [analysis, bands, highCutHz, lowCutHz]);

  function updateBand(index: number, patch: Partial<EqBand>) {
    setBands((prev) => prev.map((band, i) => (i === index ? { ...band, ...patch } : band)));
  }

  function handlePointerDown(target: DragTarget) {
    setDragTarget(target);
  }

  function handlePointerMove(event: ReactPointerEvent<SVGSVGElement>) {
    if (!dragTarget || !svgRef.current) return;

    const point = svgPointFromEvent(svgRef.current, event);
    const x = clamp(point.x, 0, VIEWBOX_WIDTH);
    const y = clamp(point.y, 0, VIEWBOX_HEIGHT);

    if (dragTarget === "lowCut") {
      const nextFreq = clamp(freqFromX(x), 20, Math.min(1000, highCutHz - 100));
      setLowCutHz(Math.round(nextFreq));
      return;
    }

    if (dragTarget === "highCut") {
      const nextFreq = clamp(freqFromX(x), Math.max(1000, lowCutHz + 100), 22000);
      setHighCutHz(Math.round(nextFreq));
      return;
    }

    if (dragTarget === "band0" || dragTarget === "band1") {
      const index = dragTarget === "band0" ? 0 : 1;
      const nextFreq = clamp(freqFromX(x), lowCutHz + 20, highCutHz - 20);
      const nextGain = clamp(dbFromY(y), MIN_DB, MAX_DB);
      updateBand(index, {
        frequency_hz: Math.round(nextFreq),
        gain_db: roundTo(nextGain, 0.1),
      });
    }
  }

  function handlePointerUp() {
    setDragTarget(null);
  }

  return (
    <section className="rounded-[28px] bg-panel p-6 shadow-[0_30px_80px_rgba(0,0,0,0.35)]">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-cyan-300/80">Channel EQ MVP</p>
          <h2 className="mt-2 text-2xl font-semibold">EQ Plugin-Style Preview</h2>
        </div>
        <div className="rounded-full border border-cyan-400/30 bg-cyan-400/10 px-4 py-2 text-sm text-cyan-200">
          {selectedTrackId ? "Track Selected" : "Select a Track"}
        </div>
      </div>

      <div className="mt-6 overflow-hidden rounded-[24px] border border-slate-700 bg-[#121a24]">
        <div className="border-b border-slate-700 bg-gradient-to-b from-[#1c2533] to-[#131a23] px-5 py-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-medium text-slate-100">Channel EQ Curve</h3>
              <p className="mt-1 text-sm text-slate-400">
                HPF + Bell 2 Band + LPF 조합으로 실제 플러그인 형태에 가깝게 preview 한다.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="rounded-full bg-cyan-400/15 px-3 py-1 text-cyan-200">HPF</span>
              <span className="rounded-full bg-amber-400/15 px-3 py-1 text-amber-200">Bell 1</span>
              <span className="rounded-full bg-violet-400/15 px-3 py-1 text-violet-200">Bell 2</span>
              <span className="rounded-full bg-fuchsia-400/15 px-3 py-1 text-fuchsia-200">LPF</span>
            </div>
          </div>
        </div>

        <div className="p-4">
          <div className="rounded-[20px] border border-slate-800 bg-gradient-to-b from-[#191f2c] to-[#0f1620] p-3">
            <svg
              ref={svgRef}
              viewBox={`0 0 ${VIEWBOX_WIDTH} ${VIEWBOX_HEIGHT}`}
              className="h-[360px] w-full touch-none"
              onPointerMove={handlePointerMove}
              onPointerUp={handlePointerUp}
              onPointerLeave={handlePointerUp}
            >
              <defs>
                <linearGradient id="eq-fill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="rgba(90, 225, 214, 0.34)" />
                  <stop offset="100%" stopColor="rgba(90, 225, 214, 0.02)" />
                </linearGradient>
              </defs>

              {FREQ_LABELS.map((freq) => {
                const x = freqToX(freq);
                return (
                  <g key={freq}>
                    <line x1={x} y1="0" x2={x} y2={VIEWBOX_HEIGHT} stroke="rgba(120,140,170,0.15)" strokeWidth="1" />
                    <text x={x} y={VIEWBOX_HEIGHT - 12} textAnchor="middle" fill="rgba(190,205,230,0.7)" fontSize="12">
                      {formatFreqLabel(freq)}
                    </text>
                  </g>
                );
              })}

              {[-18, -12, -6, 0, 6, 12, 18].map((db) => {
                const y = dbToY(db);
                return (
                  <g key={db}>
                    <line
                      x1="0"
                      y1={y}
                      x2={VIEWBOX_WIDTH}
                      y2={y}
                      stroke={db === 0 ? "rgba(93, 200, 255, 0.55)" : "rgba(120,140,170,0.14)"}
                      strokeWidth={db === 0 ? "2" : "1"}
                    />
                    <text x={VIEWBOX_WIDTH - 8} y={y - 6} textAnchor="end" fill="rgba(190,205,230,0.58)" fontSize="12">
                      {db > 0 ? `+${db}` : db} dB
                    </text>
                  </g>
                );
              })}

              <polyline
                points={graph.spectrumPath}
                fill="none"
                stroke="rgba(210, 210, 220, 0.22)"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <polygon points={graph.fillPolygon} fill="url(#eq-fill)" />
              <polyline
                points={graph.curvePath}
                fill="none"
                stroke="#4fd1c5"
                strokeWidth="4"
                strokeLinecap="round"
                strokeLinejoin="round"
              />

              <NodeHandle
                x={graph.lowCutX}
                y={dbToY(buildHighPassDb(lowCutHz, lowCutHz))}
                color="#4fd1c5"
                onPointerDown={() => handlePointerDown("lowCut")}
              />
              <NodeHandle
                x={graph.highCutX}
                y={dbToY(buildLowPassDb(highCutHz, highCutHz))}
                color="#e879f9"
                onPointerDown={() => handlePointerDown("highCut")}
              />

              {bands.map((band, index) => (
                <NodeHandle
                  key={`${band.frequency_hz}-${index}`}
                  x={graph.bandPoints[index]?.x ?? 0}
                  y={graph.bandPoints[index]?.y ?? 0}
                  color={index === 0 ? "#fbbf24" : "#a78bfa"}
                  onPointerDown={() => handlePointerDown(index === 0 ? "band0" : "band1")}
                />
              ))}
            </svg>
          </div>

          <div className="mt-5 grid gap-5 xl:grid-cols-[1.25fr_0.75fr]">
            <div className="grid gap-4 md:grid-cols-2">
              <PluginBandCard title="High-Pass" accent="text-cyan-200" valueLabel={`${lowCutHz} Hz`} footnote="12 dB/oct">
                <input
                  className="w-full accent-cyan-400"
                  type="range"
                  min={20}
                  max={1000}
                  value={lowCutHz}
                  onChange={(event) => setLowCutHz(Number(event.target.value))}
                />
                <input
                  className="mt-3 w-full rounded-xl border border-slate-600 bg-slate-900/60 px-4 py-3 text-slate-100"
                  type="number"
                  min={20}
                  max={1000}
                  value={lowCutHz}
                  onChange={(event) => setLowCutHz(Number(event.target.value))}
                />
              </PluginBandCard>

              <PluginBandCard title="Low-Pass" accent="text-fuchsia-200" valueLabel={`${highCutHz} Hz`} footnote="12 dB/oct">
                <input
                  className="w-full accent-fuchsia-400"
                  type="range"
                  min={1000}
                  max={22000}
                  value={highCutHz}
                  onChange={(event) => setHighCutHz(Number(event.target.value))}
                />
                <input
                  className="mt-3 w-full rounded-xl border border-slate-600 bg-slate-900/60 px-4 py-3 text-slate-100"
                  type="number"
                  min={1000}
                  max={22000}
                  value={highCutHz}
                  onChange={(event) => setHighCutHz(Number(event.target.value))}
                />
              </PluginBandCard>

              {bands.map((band, index) => (
                <PluginBandCard
                  key={`band-card-${index}`}
                  title={`Bell ${index + 1}`}
                  accent={index === 0 ? "text-amber-200" : "text-violet-200"}
                  valueLabel={`${band.frequency_hz} Hz / ${band.gain_db.toFixed(1)} dB`}
                  footnote={`Q ${band.q.toFixed(2)}`}
                >
                  <label className="block text-sm text-slate-300">
                    Frequency
                    <input
                      className={`mt-2 w-full ${index === 0 ? "accent-amber-400" : "accent-violet-400"}`}
                      type="range"
                      min={20}
                      max={20000}
                      value={band.frequency_hz}
                      onChange={(event) => updateBand(index, { frequency_hz: Number(event.target.value) })}
                    />
                  </label>
                  <label className="mt-3 block text-sm text-slate-300">
                    Gain
                    <input
                      className={`mt-2 w-full ${index === 0 ? "accent-amber-400" : "accent-violet-400"}`}
                      type="range"
                      min={-18}
                      max={18}
                      step={0.1}
                      value={band.gain_db}
                      onChange={(event) => updateBand(index, { gain_db: Number(event.target.value) })}
                    />
                  </label>
                  <label className="mt-3 block text-sm text-slate-300">
                    Q
                    <input
                      className={`mt-2 w-full ${index === 0 ? "accent-amber-400" : "accent-violet-400"}`}
                      type="range"
                      min={0.1}
                      max={10}
                      step={0.05}
                      value={band.q}
                      onChange={(event) => updateBand(index, { q: Number(event.target.value) })}
                    />
                  </label>
                  <div className="mt-3 grid grid-cols-3 gap-2">
                    <NumericField
                      label="Hz"
                      value={band.frequency_hz}
                      step={1}
                      min={20}
                      max={20000}
                      onChange={(value) => updateBand(index, { frequency_hz: value })}
                    />
                    <NumericField
                      label="dB"
                      value={band.gain_db}
                      step={0.1}
                      min={-18}
                      max={18}
                      onChange={(value) => updateBand(index, { gain_db: value })}
                    />
                    <NumericField
                      label="Q"
                      value={band.q}
                      step={0.05}
                      min={0.1}
                      max={10}
                      onChange={(value) => updateBand(index, { q: value })}
                    />
                  </div>
                </PluginBandCard>
              ))}
            </div>

            <div className="rounded-[20px] border border-slate-700 bg-[#161f2b] p-5">
              <h3 className="text-lg font-medium text-slate-100">Analysis Result</h3>
              {analysis ? (
                <div className="mt-4 space-y-3 text-sm text-slate-200">
                  <MetricRow label="Duration" value={`${analysis.result.duration_sec} sec`} />
                  <MetricRow label="Sample Rate" value={`${analysis.result.sample_rate} Hz`} />
                  <MetricRow label="Channels" value={`${analysis.result.channels}`} />
                  <MetricRow label="Peak" value={`${analysis.result.peak_dbfs} dBFS`} />
                  <MetricRow label="RMS" value={`${analysis.result.rms_dbfs} dBFS`} />
                </div>
              ) : (
                <p className="mt-4 text-sm text-slate-400">분석 결과가 아직 없습니다.</p>
              )}

              <button
                className="mt-6 w-full rounded-xl bg-accent px-4 py-3 text-base font-semibold text-slate-900 disabled:opacity-40"
                disabled={!selectedTrackId || isBusy}
                onClick={() => onApply({ low_cut_hz: lowCutHz, high_cut_hz: highCutHz, bands })}
              >
                Apply Channel EQ Preview
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function PluginBandCard({
  title,
  accent,
  valueLabel,
  footnote,
  children,
}: {
  title: string;
  accent: string;
  valueLabel: string;
  footnote: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-[20px] border border-slate-700 bg-[#161f2b] p-5">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className={`text-sm uppercase tracking-[0.24em] ${accent}`}>{title}</p>
          <p className="mt-3 text-lg font-semibold text-slate-100">{valueLabel}</p>
        </div>
        <span className="rounded-full border border-slate-600 px-3 py-1 text-xs text-slate-300">
          {footnote}
        </span>
      </div>
      <div className="mt-5">{children}</div>
    </div>
  );
}

function NumericField({
  label,
  value,
  step,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  step: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
}) {
  return (
    <label className="block text-xs text-slate-400">
      {label}
      <input
        className="mt-1 w-full rounded-lg border border-slate-600 bg-slate-900/60 px-3 py-2 text-sm text-slate-100"
        type="number"
        value={value}
        step={step}
        min={min}
        max={max}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

function MetricRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-700/70 pb-2">
      <span className="text-slate-400">{label}</span>
      <span>{value}</span>
    </div>
  );
}

function NodeHandle({
  x,
  y,
  color,
  onPointerDown,
}: {
  x: number;
  y: number;
  color: string;
  onPointerDown: () => void;
}) {
  return (
    <g onPointerDown={onPointerDown} style={{ cursor: "grab" }}>
      <circle cx={x} cy={y} r="14" fill={`${color}22`} />
      <circle cx={x} cy={y} r="9" fill={color} stroke="white" strokeWidth="2.5" />
    </g>
  );
}

function svgPointFromEvent(svg: SVGSVGElement, event: ReactPointerEvent<SVGSVGElement>) {
  const rect = svg.getBoundingClientRect();
  const scaleX = VIEWBOX_WIDTH / rect.width;
  const scaleY = VIEWBOX_HEIGHT / rect.height;
  return {
    x: (event.clientX - rect.left) * scaleX,
    y: (event.clientY - rect.top) * scaleY,
  };
}

function buildTotalResponseDb(freq: number, lowCutHz: number, highCutHz: number, bands: EqBand[]): number {
  let db = buildHighPassDb(freq, lowCutHz) + buildLowPassDb(freq, highCutHz);
  for (const band of bands) {
    if (!band.enabled) continue;
    db += buildBellDb(freq, band);
  }
  return clamp(db, MIN_DB, MAX_DB);
}

function buildHighPassDb(freq: number, lowCutHz: number): number {
  if (freq >= lowCutHz) return 0;
  const ratio = Math.max(freq / lowCutHz, 1e-4);
  return Math.max(MIN_DB, 12 * Math.log2(ratio));
}

function buildLowPassDb(freq: number, highCutHz: number): number {
  if (freq <= highCutHz) return 0;
  const ratio = Math.max(highCutHz / freq, 1e-4);
  return Math.max(MIN_DB, 12 * Math.log2(ratio));
}

function buildBellDb(freq: number, band: EqBand): number {
  const spread = Math.max(0.08, 0.9 / band.q);
  const distance = Math.log2(Math.max(freq, MIN_FREQ) / Math.max(band.frequency_hz, MIN_FREQ));
  return band.gain_db * Math.exp(-(distance * distance) / (2 * spread * spread));
}

function freqToX(freq: number): number {
  const clamped = Math.min(MAX_FREQ, Math.max(MIN_FREQ, freq));
  const minLog = Math.log10(MIN_FREQ);
  const maxLog = Math.log10(MAX_FREQ);
  const pos = (Math.log10(clamped) - minLog) / (maxLog - minLog);
  return pos * VIEWBOX_WIDTH;
}

function freqFromX(x: number): number {
  const minLog = Math.log10(MIN_FREQ);
  const maxLog = Math.log10(MAX_FREQ);
  const pos = x / VIEWBOX_WIDTH;
  return 10 ** (minLog + pos * (maxLog - minLog));
}

function xToFreq(x: number): number {
  return freqFromX(x);
}

function dbToY(db: number): number {
  const clamped = clamp(db, MIN_DB, MAX_DB);
  const normalized = (MAX_DB - clamped) / (MAX_DB - MIN_DB);
  return normalized * (VIEWBOX_HEIGHT - 44) + 12;
}

function dbFromY(y: number): number {
  const normalized = clamp((y - 12) / (VIEWBOX_HEIGHT - 44), 0, 1);
  return MAX_DB - normalized * (MAX_DB - MIN_DB);
}

function mockSpectrumDb(freq: number, rmsDbfs: number, peakDbfs: number): number {
  const lowHill = 280 * Math.exp(-Math.abs(Math.log(freq / 180)) * 0.75);
  const midHill = 180 * Math.exp(-Math.abs(Math.log(freq / 1400)) * 0.95);
  const topHill = 220 * Math.exp(-Math.abs(Math.log(freq / 6000)) * 1.2);
  const base = -14 + lowHill * 0.012 + midHill * 0.01 + topHill * 0.006;
  const crestBoost = Math.min(5, Math.max(0, (peakDbfs - rmsDbfs) * 0.35));
  return clamp(base + crestBoost, -18, -1);
}

function formatFreqLabel(freq: number): string {
  if (freq >= 1000) {
    const value = freq / 1000;
    return value >= 10 ? `${Math.round(value)}k` : `${value.toFixed(value % 1 === 0 ? 0 : 1)}k`;
  }
  return `${freq}`;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function roundTo(value: number, precision: number): number {
  return Math.round(value / precision) * precision;
}
