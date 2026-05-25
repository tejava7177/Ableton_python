"use client";

import { ChangeEvent, useMemo, useState } from "react";
import {
  AlertCircle,
  AudioLines,
  Download,
  LoaderCircle,
  SlidersHorizontal,
  Upload,
  Waves,
} from "lucide-react";

type AnalyzeResponse = {
  file_id: string;
  filename: string;
  duration: number;
  sample_rate: number;
  channels: number;
  peak_dbfs: number;
  rms_dbfs: number;
  original_file_url: string;
};

type ProcessResponse = {
  processed_file_url: string;
  analysis_before: {
    peak_dbfs: number;
    rms_dbfs: number;
  };
  analysis_after: {
    peak_dbfs: number;
    rms_dbfs: number;
  };
  applied: {
    low_cut_hz: number;
    high_cut_hz: number;
  };
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const waveformBars = Array.from({ length: 48 }, (_, index) => ({
  id: index,
  height: 24 + Math.abs(Math.sin(index * 0.45)) * 76,
}));

function formatSeconds(seconds: number) {
  return `${seconds.toFixed(2)} sec`;
}

function formatDbfs(value: number) {
  return `${value.toFixed(2)} dBFS`;
}

async function parseError(response: Response) {
  try {
    const data = await response.json();
    return data.detail ?? "Unexpected server error.";
  } catch {
    return "Unexpected server error.";
  }
}

export default function LowHighCutPage() {
  const [file, setFile] = useState<File | null>(null);
  const [originalPreviewUrl, setOriginalPreviewUrl] = useState<string>("");
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [processed, setProcessed] = useState<ProcessResponse | null>(null);
  const [lowCutHz, setLowCutHz] = useState<number>(80);
  const [highCutHz, setHighCutHz] = useState<number>(18000);
  const [error, setError] = useState<string>("");
  const [analyzing, setAnalyzing] = useState(false);
  const [processing, setProcessing] = useState(false);

  const processedFileUrl = useMemo(() => {
    if (!processed?.processed_file_url) {
      return "";
    }
    return `${API_BASE_URL}${processed.processed_file_url}`;
  }, [processed]);

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] ?? null;
    setProcessed(null);
    setAnalysis(null);
    setError("");

    if (!selectedFile) {
      setFile(null);
      setOriginalPreviewUrl("");
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith(".wav")) {
      setFile(null);
      setOriginalPreviewUrl("");
      setError("WAV 파일만 업로드할 수 있습니다.");
      return;
    }

    if (selectedFile.size > 50 * 1024 * 1024) {
      setFile(null);
      setOriginalPreviewUrl("");
      setError("파일 크기는 50MB 이하여야 합니다.");
      return;
    }

    setFile(selectedFile);
    setOriginalPreviewUrl(URL.createObjectURL(selectedFile));

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setAnalyzing(true);
      const response = await fetch(`${API_BASE_URL}/api/audio/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await parseError(response));
      }

      const data = (await response.json()) as AnalyzeResponse;
      setAnalysis(data);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "분석에 실패했습니다.");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleApplyFilter = async () => {
    setError("");

    if (!file) {
      setError("먼저 WAV 파일을 업로드해 주세요.");
      return;
    }

    if (lowCutHz < 20 || lowCutHz > 1000) {
      setError("Low Cut은 20Hz에서 1000Hz 사이여야 합니다.");
      return;
    }

    if (highCutHz < 1000 || highCutHz > 22000) {
      setError("High Cut은 1000Hz에서 22000Hz 사이여야 합니다.");
      return;
    }

    if (lowCutHz >= highCutHz) {
      setError("Low Cut 값은 High Cut 값보다 작아야 합니다.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("low_cut_hz", String(lowCutHz));
    formData.append("high_cut_hz", String(highCutHz));

    try {
      setProcessing(true);
      const response = await fetch(`${API_BASE_URL}/api/audio/low-high-cut`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await parseError(response));
      }

      const data = (await response.json()) as ProcessResponse;
      setProcessed(data);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "필터 적용에 실패했습니다.");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <main className="min-h-screen px-4 py-8 md:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        <section className="rounded-[32px] border border-white/10 bg-slate-950/70 p-8 shadow-2xl shadow-cyan-950/20 backdrop-blur">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.32em] text-cyan-200/70">
                Audio Test Tool
              </p>
              <h1 className="mt-3 text-3xl font-semibold text-white md:text-5xl">
                Low / High Cut Tester
              </h1>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300 md:text-base">
                LLM 없이 WAV 파일을 업로드하고 현재 상태를 분석한 뒤, Low Cut / High Cut
                필터를 적용해 Before / After 결과를 비교하는 기술 검증용 페이지입니다.
              </p>
            </div>
            <div className="rounded-3xl border border-cyan-300/20 bg-cyan-300/10 px-4 py-3 text-sm text-cyan-100">
              FastAPI + Next.js + scipy.signal
            </div>
          </div>
        </section>

        {error ? (
          <div className="flex items-start gap-3 rounded-3xl border border-rose-400/30 bg-rose-500/10 p-4 text-rose-100">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
            <p className="text-sm leading-6">{error}</p>
          </div>
        ) : null}

        <div className="grid gap-6 xl:grid-cols-12">
          <section className="space-y-6 xl:col-span-3">
            <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="mb-4 flex items-center gap-2 text-cyan-100">
                <Upload className="h-5 w-5" />
                <h2 className="text-lg font-medium">Upload WAV</h2>
              </div>
              <label className="flex cursor-pointer flex-col items-center justify-center rounded-[24px] border border-dashed border-slate-600 bg-slate-950/70 px-4 py-10 text-center transition hover:border-cyan-300/40 hover:bg-slate-900">
                <input
                  type="file"
                  accept=".wav,audio/wav"
                  className="hidden"
                  onChange={handleFileChange}
                />
                <Upload className="h-8 w-8 text-slate-400" />
                <p className="mt-3 font-medium text-white">WAV 파일 선택</p>
                <p className="mt-1 text-sm text-slate-400">최대 50MB, mono / stereo 지원</p>
              </label>
              <div className="mt-4 rounded-2xl border border-white/8 bg-slate-900/80 p-4">
                <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Selected File</p>
                <p className="mt-2 break-all text-sm text-slate-100">
                  {file?.name ?? "아직 업로드된 파일이 없습니다."}
                </p>
              </div>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="mb-4 flex items-center gap-2 text-cyan-100">
                <AudioLines className="h-5 w-5" />
                <h2 className="text-lg font-medium">Original Analysis</h2>
              </div>
              {analyzing ? (
                <div className="flex items-center gap-3 rounded-2xl border border-white/8 bg-slate-950/70 p-4 text-sm text-slate-300">
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                  서버에서 오디오를 분석하는 중입니다.
                </div>
              ) : analysis ? (
                <div className="space-y-3">
                  {[
                    ["Duration", formatSeconds(analysis.duration)],
                    ["Sample Rate", `${analysis.sample_rate} Hz`],
                    ["Channels", `${analysis.channels}`],
                    ["Peak", formatDbfs(analysis.peak_dbfs)],
                    ["RMS", formatDbfs(analysis.rms_dbfs)],
                  ].map(([label, value]) => (
                    <div
                      key={label}
                      className="flex items-center justify-between rounded-2xl border border-white/8 bg-slate-950/70 px-4 py-3"
                    >
                      <span className="text-sm text-slate-400">{label}</span>
                      <span className="text-sm font-medium text-white">{value}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="rounded-2xl border border-white/8 bg-slate-950/70 p-4 text-sm leading-6 text-slate-400">
                  파일 업로드 후 duration, sample rate, channel, peak, RMS 정보를 표시합니다.
                </p>
              )}
            </div>
          </section>

          <section className="space-y-6 xl:col-span-6">
            <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="mb-4 flex items-center gap-2 text-cyan-100">
                <Waves className="h-5 w-5" />
                <h2 className="text-lg font-medium">Preview</h2>
              </div>
              <div className="rounded-[24px] border border-white/8 bg-slate-950/80 p-5">
                <div className="mb-5 flex h-36 items-end gap-2 overflow-hidden rounded-[20px] border border-white/6 bg-[linear-gradient(180deg,rgba(8,15,33,0.65),rgba(2,6,23,0.95))] px-4 py-4">
                  {waveformBars.map((bar) => (
                    <div
                      key={bar.id}
                      className="flex-1 rounded-full bg-gradient-to-t from-cyan-500/25 via-cyan-300/60 to-white/90"
                      style={{ height: `${bar.height}%` }}
                    />
                  ))}
                </div>
                <div className="grid gap-4 lg:grid-cols-2">
                  <div className="rounded-2xl border border-white/8 bg-slate-900/70 p-4">
                    <p className="mb-3 text-sm font-medium text-slate-200">Before</p>
                    <audio className="w-full" controls src={originalPreviewUrl || undefined} />
                  </div>
                  <div className="rounded-2xl border border-white/8 bg-slate-900/70 p-4">
                    <p className="mb-3 text-sm font-medium text-slate-200">After</p>
                    <audio className="w-full" controls src={processedFileUrl || undefined} />
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
              <h2 className="text-lg font-medium text-white">Before / After Metrics</h2>
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div className="rounded-[24px] border border-white/8 bg-slate-950/70 p-4">
                  <p className="text-sm text-slate-400">Before</p>
                  <div className="mt-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-400">Peak</span>
                      <span className="text-sm font-medium text-white">
                        {processed
                          ? formatDbfs(processed.analysis_before.peak_dbfs)
                          : analysis
                            ? formatDbfs(analysis.peak_dbfs)
                            : "-"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-400">RMS</span>
                      <span className="text-sm font-medium text-white">
                        {processed
                          ? formatDbfs(processed.analysis_before.rms_dbfs)
                          : analysis
                            ? formatDbfs(analysis.rms_dbfs)
                            : "-"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="rounded-[24px] border border-cyan-300/20 bg-cyan-300/8 p-4">
                  <p className="text-sm text-cyan-100">After</p>
                  <div className="mt-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-cyan-100/70">Peak</span>
                      <span className="text-sm font-medium text-white">
                        {processed ? formatDbfs(processed.analysis_after.peak_dbfs) : "-"}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-cyan-100/70">RMS</span>
                      <span className="text-sm font-medium text-white">
                        {processed ? formatDbfs(processed.analysis_after.rms_dbfs) : "-"}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 rounded-2xl border border-white/8 bg-slate-950/70 p-4 text-sm text-slate-300">
                {processed ? (
                  <p>
                    Applied: Low Cut {processed.applied.low_cut_hz}Hz / High Cut{" "}
                    {processed.applied.high_cut_hz}Hz
                  </p>
                ) : (
                  <p>필터 적용 후 Before / After 변화가 이 영역에 표시됩니다.</p>
                )}
              </div>
            </div>
          </section>

          <section className="space-y-6 xl:col-span-3">
            <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="mb-4 flex items-center gap-2 text-cyan-100">
                <SlidersHorizontal className="h-5 w-5" />
                <h2 className="text-lg font-medium">Filter Settings</h2>
              </div>

              <div className="space-y-4">
                <label className="block rounded-[24px] border border-white/8 bg-slate-950/70 p-4">
                  <span className="text-sm text-slate-300">Low Cut Frequency</span>
                  <input
                    type="number"
                    min={20}
                    max={1000}
                    value={lowCutHz}
                    onChange={(event) => setLowCutHz(Number(event.target.value))}
                    className="mt-3 w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                  />
                  <p className="mt-2 text-xs text-slate-500">20Hz to 1000Hz</p>
                </label>

                <label className="block rounded-[24px] border border-white/8 bg-slate-950/70 p-4">
                  <span className="text-sm text-slate-300">High Cut Frequency</span>
                  <input
                    type="number"
                    min={1000}
                    max={22000}
                    value={highCutHz}
                    onChange={(event) => setHighCutHz(Number(event.target.value))}
                    className="mt-3 w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                  />
                  <p className="mt-2 text-xs text-slate-500">1000Hz to 22000Hz</p>
                </label>
              </div>

              <button
                type="button"
                onClick={handleApplyFilter}
                disabled={!file || analyzing || processing}
                className="mt-5 inline-flex w-full items-center justify-center rounded-2xl bg-cyan-300 px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
              >
                {processing ? (
                  <>
                    <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                    Applying Filter...
                  </>
                ) : (
                  "Apply Filter"
                )}
              </button>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="mb-4 flex items-center gap-2 text-cyan-100">
                <Download className="h-5 w-5" />
                <h2 className="text-lg font-medium">Download</h2>
              </div>
              <a
                href={processedFileUrl || "#"}
                download
                className={`inline-flex w-full items-center justify-center rounded-2xl px-4 py-3 font-medium transition ${
                  processedFileUrl
                    ? "bg-white text-slate-950 hover:bg-slate-100"
                    : "pointer-events-none bg-slate-800 text-slate-500"
                }`}
              >
                Download Processed WAV
              </a>
              <p className="mt-3 text-sm leading-6 text-slate-400">
                필터 적용이 끝나면 처리된 WAV 파일을 바로 내려받을 수 있습니다.
              </p>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
