"use client";

import React, { useMemo, useState } from "react";
import {
  Bot,
  Download,
  Gauge,
  Menu,
  Pause,
  Play,
  Plus,
  RefreshCcw,
  Scissors,
  SlidersHorizontal,
  Sparkles,
  Upload,
  Volume2,
  Wand2,
} from "lucide-react";

type Track = {
  id: string;
  name: string;
  type: string;
  lufs: string;
  peak: string;
  level: number;
  issue: string;
  color: string;
};

type Suggestion = {
  icon: React.ComponentType<{ size?: number; className?: string }>;
  title: string;
  detail: string;
  risk: string;
};

const tracks: Track[] = [
  { id: "t1", name: "Vocal_Main.wav", type: "Vocal", lufs: "-14.2", peak: "-1.2", level: -6.1, issue: "보컬 앞부분 무음", color: "bg-purple-500" },
  { id: "t2", name: "Vocal_Double.wav", type: "Vocal", lufs: "-17.0", peak: "-3.8", level: -8.3, issue: "게인 낮음", color: "bg-fuchsia-500" },
  { id: "t3", name: "Drum_Bus.wav", type: "Drums", lufs: "-12.8", peak: "-0.6", level: -5.6, issue: "피크 주의", color: "bg-amber-400" },
  { id: "t4", name: "Kick.wav", type: "Drums", lufs: "-13.4", peak: "-0.9", level: -4.2, issue: "저역 과다", color: "bg-orange-500" },
  { id: "t5", name: "Snare.wav", type: "Drums", lufs: "-15.6", peak: "-2.1", level: -6.8, issue: "정상", color: "bg-rose-400" },
  { id: "t6", name: "Bass.wav", type: "Bass", lufs: "-11.8", peak: "-1.3", level: -5.1, issue: "Low-mid muddy", color: "bg-emerald-400" },
  { id: "t7", name: "Guitar_L.wav", type: "Guitar", lufs: "-18.1", peak: "-4.8", level: -7.3, issue: "하이컷 후보", color: "bg-sky-400" },
  { id: "t8", name: "Guitar_R.wav", type: "Guitar", lufs: "-18.3", peak: "-5.0", level: -7.6, issue: "하이컷 후보", color: "bg-cyan-400" },
  { id: "t9", name: "Piano.wav", type: "Keys", lufs: "-20.4", peak: "-3.2", level: -12.0, issue: "게인 낮음", color: "bg-indigo-400" },
  { id: "t10", name: "FX_Riser.wav", type: "FX", lufs: "-22.0", peak: "-6.0", level: -16.0, issue: "앞뒤 무음", color: "bg-lime-400" },
];

const suggestions: Suggestion[] = [
  { icon: Scissors, title: "Trim Silence", detail: "Vocal_Main과 FX_Riser의 앞/뒤 무음 후보를 정리합니다.", risk: "낮음" },
  { icon: SlidersHorizontal, title: "Low Cut 80Hz", detail: "보컬/기타 트랙의 불필요한 저역을 정리합니다.", risk: "낮음" },
  { icon: Gauge, title: "Gain Normalize", detail: "트랙별 loudness 차이를 줄여 첫 믹스 밸런스를 잡습니다.", risk: "중간" },
];

const eqPoints = [
  { x: 10, y: 82, label: "Low Cut" },
  { x: 22, y: 55, label: "100Hz" },
  { x: 39, y: 50, label: "250Hz" },
  { x: 57, y: 62, label: "2.5k" },
  { x: 74, y: 47, label: "7.5k" },
  { x: 90, y: 45, label: "High" },
];

function Card({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <div className={`rounded-2xl border shadow-xl shadow-black/10 ${className}`}>{children}</div>;
}

function CardContent({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <div className={className}>{children}</div>;
}

function Button({
  children,
  className = "",
  variant = "default",
  size = "default",
  onClick,
}: {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm";
  onClick?: () => void;
}) {
  const sizeClass = size === "sm" ? "h-9 px-3 text-sm" : "h-10 px-4 text-sm";
  const variantClass =
    variant === "outline"
      ? "border border-zinc-700 bg-zinc-900 text-zinc-100 hover:bg-zinc-800"
      : variant === "ghost"
        ? "bg-transparent text-zinc-100 hover:bg-zinc-800"
        : "bg-zinc-100 text-zinc-950 hover:bg-white";

  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center justify-center rounded-xl font-medium transition ${sizeClass} ${variantClass} ${className}`}
    >
      {children}
    </button>
  );
}

function WaveformRow({
  active,
  color = "bg-purple-500",
  index = 0,
}: {
  active?: boolean;
  color?: string;
  index?: number;
}) {
  const bars = useMemo(
    () =>
      Array.from(
        { length: 120 },
        (_, i) =>
          Math.round(
            18 + Math.abs(Math.sin(i * 0.25 + index)) * 38 + Math.abs(Math.cos(i * 0.09)) * 18,
          ),
      ),
    [index],
  );

  return (
    <div className={`relative h-12 border-b border-zinc-800/80 ${active ? "bg-purple-500/5" : "bg-zinc-950/20"}`}>
      <div className="absolute inset-x-0 top-1/2 flex -translate-y-1/2 items-center gap-[2px] px-3">
        {bars.map((h, i) => (
          <div
            key={i}
            className={`w-1 rounded-full ${active ? color : "bg-zinc-600/70"}`}
            style={{ height: `${h}%`, opacity: active ? 0.95 : 0.5 }}
          />
        ))}
      </div>
      {index === 1 ? (
        <div className="absolute left-[44%] top-1/2 h-7 -translate-y-1/2 rounded-md border border-pink-400/40 bg-pink-500/20 px-8 text-xs leading-7 text-pink-200">
          Silence
        </div>
      ) : null}
    </div>
  );
}

function LevelMeter({ level }: { level: number }) {
  const width = Math.min(92, Math.max(8, 100 + level * 6));
  return (
    <div className="h-3 w-20 overflow-hidden rounded-full bg-zinc-800">
      <div
        className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-lime-300 to-amber-300"
        style={{ width: `${width}%` }}
      />
    </div>
  );
}

export default function AIMixingDAWWorkspaceMockup() {
  const [selectedTrack, setSelectedTrack] = useState<Track>(tracks[0]);
  const [tab, setTab] = useState("Inspector");
  const [playing, setPlaying] = useState(false);

  return (
    <div className="min-h-screen bg-[#090b10] text-zinc-100">
      <div className="flex min-h-screen flex-col overflow-hidden">
        <header className="flex h-14 items-center border-b border-zinc-800 bg-zinc-950/95 px-4">
          <div className="flex w-64 items-center gap-3 border-r border-zinc-800 pr-4">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-purple-500/20 text-purple-300">
              <Sparkles size={18} />
            </div>
            <div>
              <div className="text-sm font-bold">AI Mixing Assistant</div>
              <div className="text-[11px] text-zinc-500">DAW-inspired workspace</div>
            </div>
          </div>

          <div className="flex flex-1 items-center justify-between px-4">
            <div className="flex items-center gap-3">
              <Menu size={18} className="text-zinc-500" />
              <div className="text-sm">Project_2025_05_12</div>
              <div className="flex items-center gap-1 text-xs text-emerald-300">
                <span className="h-2 w-2 rounded-full bg-emerald-400" />
                Saved
              </div>
            </div>

            <div className="flex items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-1.5">
              <Button
                size="sm"
                variant="ghost"
                className="h-7 w-7 p-0 text-zinc-300 hover:bg-zinc-800"
                onClick={() => setPlaying(!playing)}
              >
                {playing ? <Pause size={16} /> : <Play size={16} />}
              </Button>
              <div className="font-mono text-sm text-zinc-300">01:23.456 / 03:45.000</div>
            </div>

            <div className="flex items-center gap-4 text-sm text-zinc-400">
              <span>BPM 120</span>
              <span>4/4</span>
              <span>C Maj</span>
              <Volume2 size={17} />
            </div>
          </div>
        </header>

        <div className="flex min-h-0 flex-1 flex-col xl:flex-row">
          <aside className="w-full shrink-0 border-r border-zinc-800 bg-zinc-950 p-3 xl:w-72">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Tracks ({tracks.length})</h2>
                <p className="text-xs text-zinc-500">50~100 tracks batch-ready</p>
              </div>
              <Button size="sm" variant="outline" className="h-8 w-8 border-zinc-700 bg-zinc-900 p-0">
                <Plus size={15} />
              </Button>
            </div>

            <div className="space-y-1 overflow-y-auto pr-1 xl:max-h-[calc(100vh-240px)]">
              {tracks.map((track) => (
                <button
                  key={track.id}
                  onClick={() => setSelectedTrack(track)}
                  className={`grid w-full grid-cols-[44px_1fr_82px] items-center gap-2 rounded-lg border px-2 py-2 text-left text-xs transition ${
                    selectedTrack.id === track.id
                      ? "border-purple-500/70 bg-purple-500/10"
                      : "border-zinc-800 bg-zinc-900/70 hover:bg-zinc-800/70"
                  }`}
                >
                  <div className="flex gap-1">
                    <span className="rounded bg-zinc-800 px-1.5 py-1 text-[10px] text-zinc-400">M</span>
                    <span className="rounded bg-zinc-800 px-1.5 py-1 text-[10px] text-zinc-400">S</span>
                  </div>
                  <div className="truncate">
                    <div className="truncate font-medium text-zinc-200">{track.name.replace(".wav", "")}</div>
                    <div className="text-[10px] text-zinc-500">{track.type}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <LevelMeter level={track.level} />
                    <span className="w-10 text-right text-[10px] text-zinc-400">{track.level} dB</span>
                  </div>
                </button>
              ))}
            </div>

            <Card className="mt-4 border-zinc-800 bg-zinc-900/80">
              <CardContent className="p-3">
                <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-zinc-300">
                  <Upload size={14} />
                  Upload Session
                </div>
                <div className="rounded-lg border border-dashed border-zinc-700 p-4 text-center text-xs text-zinc-500">
                  WAV / STEM ZIP 업로드
                </div>
              </CardContent>
            </Card>
          </aside>

          <main className="flex min-w-0 flex-1 flex-col bg-[#0d1118]">
            <section className="border-b border-zinc-800 p-3 xl:h-[52%]">
              <div className="mb-2 flex items-center justify-between text-xs text-zinc-500">
                <div className="flex flex-wrap gap-10 pl-2 xl:gap-20">
                  {["0:00", "0:30", "1:00", "1:30", "2:00", "2:30", "3:00", "3:30"].map((label) => (
                    <span key={label}>{label}</span>
                  ))}
                </div>
                <span>Timeline</span>
              </div>
              <div className="relative overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950/80">
                <div className="absolute left-[42%] top-0 z-10 h-full w-px bg-purple-300 shadow-[0_0_14px_rgba(168,85,247,0.8)]" />
                {tracks.slice(0, 7).map((track, index) => (
                  <WaveformRow key={track.id} active={selectedTrack.id === track.id} color={track.color} index={index} />
                ))}
              </div>
            </section>

            <section className="grid min-h-0 flex-1 grid-cols-1 gap-3 p-3 xl:grid-cols-[1fr_260px]">
              <Card className="border-zinc-800 bg-zinc-950/80">
                <CardContent className="p-0">
                  <div className="flex flex-col gap-3 border-b border-zinc-800 px-4 py-3 lg:flex-row lg:items-center lg:justify-between">
                    <div className="flex flex-wrap gap-6 text-sm">
                      {["EQ", "Trim", "Gain", "Reference", "Spectrum"].map((item) => (
                        <span key={item} className={item === "EQ" ? "text-purple-300" : "text-zinc-500"}>
                          {item}
                        </span>
                      ))}
                    </div>
                    <div className="flex flex-wrap items-center gap-5 text-xs text-zinc-400">
                      <span>
                        Low Cut <b className="text-zinc-100">80 Hz</b>
                      </span>
                      <span>
                        High Cut <b className="text-zinc-100">18.0 kHz</b>
                      </span>
                    </div>
                  </div>

                  <div className="relative h-56 p-5">
                    <div className="absolute inset-5 rounded-lg bg-[linear-gradient(to_right,rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:48px_32px]" />
                    <svg className="absolute inset-5 h-[calc(100%-40px)] w-[calc(100%-40px)] overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
                      <path
                        d="M 0 88 C 10 70, 13 58, 22 55 C 32 51, 39 51, 47 52 C 56 54, 58 66, 63 62 C 68 58, 72 45, 80 47 C 90 49, 93 46, 100 45"
                        fill="none"
                        stroke="rgb(216 180 254)"
                        strokeWidth="1.2"
                        vectorEffect="non-scaling-stroke"
                      />
                      {eqPoints.map((p, idx) => (
                        <g key={idx}>
                          <circle cx={p.x} cy={p.y} r="2" fill="rgb(168 85 247)" stroke="white" strokeWidth="0.5" vectorEffect="non-scaling-stroke" />
                        </g>
                      ))}
                    </svg>
                    <div className="absolute bottom-4 left-5 right-5 flex justify-between text-[11px] text-zinc-500">
                      <span>20</span>
                      <span>100</span>
                      <span>250</span>
                      <span>1k</span>
                      <span>5k</span>
                      <span>20k</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-zinc-800 bg-zinc-950/80">
                <CardContent className="p-4">
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="text-sm font-semibold">Level Meter</h3>
                    <span className="text-xs text-zinc-500">Master</span>
                  </div>
                  <div className="flex h-44 items-end justify-center gap-5 rounded-xl bg-zinc-900/80 p-4">
                    {[80, 68, 74, 62].map((h, i) => (
                      <div key={i} className="flex h-full w-7 items-end rounded bg-zinc-800">
                        <div className="w-full rounded bg-gradient-to-t from-emerald-500 via-lime-300 to-red-400" style={{ height: `${h}%` }} />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </section>
          </main>

          <aside className="w-full shrink-0 border-l border-zinc-800 bg-zinc-950 p-3 xl:w-80">
            <div className="mb-3 grid grid-cols-3 rounded-xl bg-zinc-900 p-1 text-xs">
              {["Inspector", "AI", "Reference"].map((item) => (
                <button
                  key={item}
                  onClick={() => setTab(item)}
                  className={`rounded-lg px-2 py-2 ${tab === item ? "bg-purple-500 text-white" : "text-zinc-500"}`}
                >
                  {item}
                </button>
              ))}
            </div>

            <Card className="border-zinc-800 bg-zinc-900/80">
              <CardContent className="p-4">
                <div className="mb-4">
                  <h2 className="font-semibold">{selectedTrack.name}</h2>
                  <p className="text-xs text-zinc-500">WAV · 44.1kHz · 24bit · Project Session 연결</p>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="rounded-lg bg-zinc-950 p-3">
                    <p className="text-zinc-500">LUFS</p>
                    <p className="mt-1 text-lg text-zinc-100">{selectedTrack.lufs}</p>
                  </div>
                  <div className="rounded-lg bg-zinc-950 p-3">
                    <p className="text-zinc-500">True Peak</p>
                    <p className="mt-1 text-lg text-zinc-100">{selectedTrack.peak}</p>
                  </div>
                  <div className="rounded-lg bg-zinc-950 p-3">
                    <p className="text-zinc-500">Issue</p>
                    <p className="mt-1 text-sm text-amber-300">{selectedTrack.issue}</p>
                  </div>
                  <div className="rounded-lg bg-zinc-950 p-3">
                    <p className="text-zinc-500">Type</p>
                    <p className="mt-1 text-sm text-zinc-100">{selectedTrack.type}</p>
                  </div>
                </div>

                <Button className="mt-4 w-full rounded-xl bg-purple-500 text-white hover:bg-purple-400">
                  <RefreshCcw size={15} className="mr-2" />
                  Re-analyze Track
                </Button>
              </CardContent>
            </Card>

            <Card className="mt-3 border-zinc-800 bg-zinc-900/80">
              <CardContent className="p-4">
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold">AI Suggested Actions</h3>
                  <span className="rounded-full bg-purple-500/20 px-2 py-0.5 text-xs text-purple-200">3</span>
                </div>
                <div className="space-y-2">
                  {suggestions.map((s) => {
                    const Icon = s.icon;
                    return (
                      <div key={s.title} className="rounded-xl border border-zinc-800 bg-zinc-950 p-3 transition hover:scale-[1.01]">
                        <div className="flex gap-3">
                          <div className="rounded-lg bg-purple-500/15 p-2 text-purple-300">
                            <Icon size={16} />
                          </div>
                          <div>
                            <div className="text-sm font-medium">{s.title}</div>
                            <p className="mt-1 text-xs text-zinc-500">{s.detail}</p>
                            <p className="mt-2 text-[11px] text-emerald-300">위험도 {s.risk}</p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <Button className="mt-4 w-full rounded-xl bg-zinc-100 text-zinc-950 hover:bg-white">
                  <Wand2 size={15} className="mr-2" />
                  Apply Suggestions
                </Button>
              </CardContent>
            </Card>

            <Card className="mt-3 border-zinc-800 bg-zinc-900/80">
              <CardContent className="p-4">
                <div className="mb-2 flex items-center gap-2 text-sm font-semibold">
                  <Bot size={16} />
                  Assistant
                </div>
                <p className="rounded-xl bg-zinc-950 p-3 text-xs leading-relaxed text-zinc-400">
                  현재 보컬은 reference보다 약간 뒤에 있습니다. Low Cut과 2.5kHz presence 보정을 먼저 적용해보는 것을 추천합니다.
                </p>
                <Button
                  variant="outline"
                  className="mt-3 w-full rounded-xl border-purple-500/50 bg-transparent text-purple-200 hover:bg-purple-500/10"
                >
                  <Download size={15} className="mr-2" />
                  Export Preview
                </Button>
              </CardContent>
            </Card>
          </aside>
        </div>
      </div>
    </div>
  );
}
