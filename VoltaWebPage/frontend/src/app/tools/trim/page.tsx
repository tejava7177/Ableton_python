"use client";

import { ChangeEvent, useMemo, useState } from "react";
import {
  AlertCircle,
  AudioLines,
  Download,
  LoaderCircle,
  ScissorsLineDashed,
  Search,
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

type SilenceRegion = {
  start: number;
  end: number;
  duration: number;
  type: "start" | "internal" | "end";
};

type DetectSilenceResponse = {
  duration: number;
  silence_regions: SilenceRegion[];
};

type TrimResponse = {
  processed_file_url: string;
  original_duration: number;
  processed_duration: number;
  removed_duration: number;
  silence_regions: SilenceRegion[];
  applied: {
    threshold_db: number;
    min_silence_ms: number;
    padding_ms: number;
    mode: TrimMode;
  };
};

type TrimMode = "start_end_only" | "remove_internal" | "shorten_internal";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

const trimModes: Array<{
  value: TrimMode;
  title: string;
  detail: string;
}> = [
  {
    value: "start_end_only",
    title: "Trim Start/End Only",
    detail: "파일 앞/뒤 무음만 제거하고 내부 무음은 유지합니다.",
  },
  {
    value: "remove_internal",
    title: "Remove Internal Silence",
    detail: "중간 무음도 제거하고 구간 연결부에는 짧은 페이드를 적용합니다.",
  },
  {
    value: "shorten_internal",
    title: "Shorten Internal Silence",
    detail: "중간 무음을 완전히 없애지 않고 padding 길이 정도만 남깁니다.",
  },
];

const waveformBars = Array.from({ length: 48 }, (_, index) => ({
  id: index,
  height: Math.round(24 + Math.abs(Math.sin(index * 0.45)) * 76),
}));

function formatSeconds(seconds: number) {
  return `${seconds.toFixed(2)} sec`;
}

function formatDbfs(value: number) {
  return `${value.toFixed(2)} dBFS`;
}

function formatMilliseconds(seconds: number) {
  return `${Math.round(seconds * 1000)}ms`;
}

async function parseError(response: Response) {
  try {
    const data = await response.json();
    return data.detail ?? "Unexpected server error.";
  } catch {
    return "Unexpected server error.";
  }
}

export default function TrimPage() {
  const [file, setFile] = useState<File | null>(null);
  const [originalPreviewUrl, setOriginalPreviewUrl] = useState<string>("");
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [silenceData, setSilenceData] = useState<DetectSilenceResponse | null>(null);
  const [trimResult, setTrimResult] = useState<TrimResponse | null>(null);
  const [thresholdDb, setThresholdDb] = useState<number>(-45);
  const [minSilenceMs, setMinSilenceMs] = useState<number>(150);
  const [paddingMs, setPaddingMs] = useState<number>(20);
  const [mode, setMode] = useState<TrimMode>("start_end_only");
  const [error, setError] = useState<string>("");
  const [info, setInfo] = useState<string>("");
  const [analyzing, setAnalyzing] = useState(false);
  const [detecting, setDetecting] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const processedFileUrl = useMemo(() => {
    if (!trimResult?.processed_file_url) {
      return "";
    }
    return `${API_BASE_URL}${trimResult.processed_file_url}`;
  }, [trimResult]);

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0] ?? null;
    setTrimResult(null);
    setSilenceData(null);
    setAnalysis(null);
    setError("");
    setInfo("");

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

  const validateSettings = () => {
    if (thresholdDb < -80 || thresholdDb > -20) {
      return "Silence Threshold는 -80 dBFS에서 -20 dBFS 사이여야 합니다.";
    }
    if (minSilenceMs < 50 || minSilenceMs > 2000) {
      return "Min Silence Duration은 50ms에서 2000ms 사이여야 합니다.";
    }
    if (paddingMs < 0 || paddingMs > 500) {
      return "Padding은 0ms에서 500ms 사이여야 합니다.";
    }
    return "";
  };

  const buildDetectionFormData = () => {
    if (!file) {
      return null;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("threshold_db", String(thresholdDb));
    formData.append("min_silence_ms", String(minSilenceMs));
    formData.append("padding_ms", String(paddingMs));
    return formData;
  };

  const handleDetectSilence = async () => {
    setError("");
    setInfo("");
    setTrimResult(null);

    if (!file) {
      setError("먼저 WAV 파일을 업로드해 주세요.");
      return;
    }

    const validationError = validateSettings();
    if (validationError) {
      setError(validationError);
      return;
    }

    const formData = buildDetectionFormData();
    if (!formData) {
      return;
    }

    try {
      setDetecting(true);
      const response = await fetch(`${API_BASE_URL}/api/audio/detect-silence`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await parseError(response));
      }

      const data = (await response.json()) as DetectSilenceResponse;
      setSilenceData(data);
      if (data.silence_regions.length === 0) {
        setInfo("No silence regions detected.");
      }
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "무음 탐지에 실패했습니다.");
    } finally {
      setDetecting(false);
    }
  };

  const handleApplyTrim = async () => {
    setError("");
    setInfo("");

    if (!file) {
      setError("먼저 WAV 파일을 업로드해 주세요.");
      return;
    }

    const validationError = validateSettings();
    if (validationError) {
      setError(validationError);
      return;
    }

    const formData = buildDetectionFormData();
    if (!formData) {
      return;
    }
    formData.append("mode", mode);

    try {
      setProcessing(true);
      const response = await fetch(`${API_BASE_URL}/api/audio/trim-silence`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await parseError(response));
      }

      const data = (await response.json()) as TrimResponse;
      setTrimResult(data);
      setSilenceData({
        duration: data.original_duration,
        silence_regions: data.silence_regions,
      });
      if (data.silence_regions.length === 0) {
        setInfo("No silence regions detected. 원본과 동일한 파일이 생성되었습니다.");
      }
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "트림 적용에 실패했습니다.");
    } finally {
      setProcessing(false);
    }
  };

  const handleDownload = async () => {
    if (!processedFileUrl) {
      return;
    }

    try {
      setDownloading(true);
      const response = await fetch(processedFileUrl);
      if (!response.ok) {
        throw new Error("처리된 파일을 다운로드하지 못했습니다.");
      }

      const blob = await response.blob();
      const objectUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = `trimmed-${file?.name ?? "processed.wav"}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(objectUrl);
    } catch (downloadError) {
      setError(
        downloadError instanceof Error
          ? downloadError.message
          : "처리된 파일을 다운로드하지 못했습니다.",
      );
    } finally {
      setDownloading(false);
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
                Silence Trim Tester
              </h1>
              <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-300 md:text-base">
                WAV loop 파일의 앞/뒤 또는 내부 무음 구간을 탐지하고, 트림 전후 결과를
                비교하는 기술 검증용 페이지입니다.
              </p>
            </div>
            <div className="rounded-3xl border border-cyan-300/20 bg-cyan-300/10 px-4 py-3 text-sm text-cyan-100">
              FastAPI + Next.js + numpy / soundfile
            </div>
          </div>
        </section>

        {error ? (
          <div className="flex items-start gap-3 rounded-3xl border border-rose-400/30 bg-rose-500/10 p-4 text-rose-100">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
            <p className="text-sm leading-6">{error}</p>
          </div>
        ) : null}

        {info ? (
          <div className="rounded-3xl border border-cyan-300/20 bg-cyan-300/10 p-4 text-sm text-cyan-50">
            {info}
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
                <div className="relative mb-5 flex h-36 items-end gap-2 overflow-hidden rounded-[20px] border border-white/6 bg-[linear-gradient(180deg,rgba(8,15,33,0.65),rgba(2,6,23,0.95))] px-4 py-4">
                  {waveformBars.map((bar) => (
                    <div
                      key={bar.id}
                      className="flex-1 rounded-full bg-gradient-to-t from-cyan-500/25 via-cyan-300/60 to-white/90"
                      style={{ height: `${bar.height}%` }}
                    />
                  ))}
                  {silenceData?.duration
                    ? silenceData.silence_regions.map((region, index) => (
                        <div
                          key={`${region.start}-${region.end}-${index}`}
                          className="absolute top-0 bottom-0 rounded-xl border border-amber-300/25 bg-amber-300/16"
                          style={{
                            left: `${(region.start / silenceData.duration) * 100}%`,
                            width: `${Math.max(
                              1.5,
                              ((region.end - region.start) / silenceData.duration) * 100,
                            )}%`,
                          }}
                        />
                      ))
                    : null}
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
              <div className="mb-4 flex items-center gap-2 text-cyan-100">
                <ScissorsLineDashed className="h-5 w-5" />
                <h2 className="text-lg font-medium">Detected Silence Regions</h2>
              </div>

              {detecting ? (
                <div className="flex items-center gap-3 rounded-2xl border border-white/8 bg-slate-950/70 p-4 text-sm text-slate-300">
                  <LoaderCircle className="h-4 w-4 animate-spin" />
                  무음 구간을 분석하는 중입니다.
                </div>
              ) : silenceData?.silence_regions.length ? (
                <div className="space-y-3">
                  {silenceData.silence_regions.map((region, index) => (
                    <div
                      key={`${region.start}-${region.end}-${index}`}
                      className="rounded-2xl border border-white/8 bg-slate-950/70 p-4"
                    >
                      <p className="text-sm font-medium text-white">
                        {index + 1}. {region.start.toFixed(2)}s ~ {region.end.toFixed(2)}s
                      </p>
                      <p className="mt-2 text-sm text-slate-400">
                        {formatMilliseconds(region.duration)} / {region.type}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="rounded-2xl border border-white/8 bg-slate-950/70 p-4 text-sm leading-6 text-slate-400">
                  Detect Silence를 누르면 탐지된 시작/중간/끝 무음 구간이 여기에 표시됩니다.
                </p>
              )}

              <div className="mt-4 grid gap-4 md:grid-cols-3">
                <div className="rounded-2xl border border-white/8 bg-slate-950/70 p-4">
                  <p className="text-sm text-slate-400">Original Duration</p>
                  <p className="mt-2 text-lg font-medium text-white">
                    {trimResult ? formatSeconds(trimResult.original_duration) : "-"}
                  </p>
                </div>
                <div className="rounded-2xl border border-white/8 bg-slate-950/70 p-4">
                  <p className="text-sm text-slate-400">Processed Duration</p>
                  <p className="mt-2 text-lg font-medium text-white">
                    {trimResult ? formatSeconds(trimResult.processed_duration) : "-"}
                  </p>
                </div>
                <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/8 p-4">
                  <p className="text-sm text-cyan-100/70">Removed Duration</p>
                  <p className="mt-2 text-lg font-medium text-white">
                    {trimResult ? formatSeconds(trimResult.removed_duration) : "-"}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section className="space-y-6 xl:col-span-3">
            <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="mb-4 flex items-center gap-2 text-cyan-100">
                <SlidersHorizontal className="h-5 w-5" />
                <h2 className="text-lg font-medium">Silence Detection</h2>
              </div>
              <div className="space-y-4">
                <label className="block rounded-[24px] border border-white/8 bg-slate-950/70 p-4">
                  <span className="text-sm text-slate-300">Silence Threshold</span>
                  <input
                    type="number"
                    min={-80}
                    max={-20}
                    value={thresholdDb}
                    onChange={(event) => setThresholdDb(Number(event.target.value))}
                    className="mt-3 w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                  />
                  <p className="mt-2 text-xs text-slate-500">-80 dBFS to -20 dBFS</p>
                </label>

                <label className="block rounded-[24px] border border-white/8 bg-slate-950/70 p-4">
                  <span className="text-sm text-slate-300">Min Silence Duration</span>
                  <input
                    type="number"
                    min={50}
                    max={2000}
                    value={minSilenceMs}
                    onChange={(event) => setMinSilenceMs(Number(event.target.value))}
                    className="mt-3 w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                  />
                  <p className="mt-2 text-xs text-slate-500">50ms to 2000ms</p>
                </label>

                <label className="block rounded-[24px] border border-white/8 bg-slate-950/70 p-4">
                  <span className="text-sm text-slate-300">Padding</span>
                  <input
                    type="number"
                    min={0}
                    max={500}
                    value={paddingMs}
                    onChange={(event) => setPaddingMs(Number(event.target.value))}
                    className="mt-3 w-full rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-white outline-none transition focus:border-cyan-300"
                  />
                  <p className="mt-2 text-xs text-slate-500">0ms to 500ms</p>
                </label>
              </div>

              <button
                type="button"
                onClick={handleDetectSilence}
                disabled={!file || analyzing || detecting || processing}
                className="mt-5 inline-flex w-full items-center justify-center rounded-2xl border border-cyan-200/25 bg-slate-900/80 px-4 py-3 font-medium text-cyan-100 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:border-slate-700 disabled:bg-slate-900 disabled:text-slate-500"
              >
                {detecting ? (
                  <>
                    <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                    Detecting...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Detect Silence
                  </>
                )}
              </button>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
              <h2 className="text-lg font-medium text-white">Trim Mode</h2>
              <div className="mt-4 space-y-3">
                {trimModes.map((trimMode) => (
                  <button
                    key={trimMode.value}
                    type="button"
                    onClick={() => setMode(trimMode.value)}
                    className={`w-full rounded-2xl border p-4 text-left transition ${
                      mode === trimMode.value
                        ? "border-cyan-300/40 bg-cyan-300/10"
                        : "border-white/8 bg-slate-950/70"
                    }`}
                  >
                    <p className="text-sm font-medium text-white">{trimMode.title}</p>
                    <p className="mt-2 text-sm leading-6 text-slate-400">{trimMode.detail}</p>
                  </button>
                ))}
              </div>

              <button
                type="button"
                onClick={handleApplyTrim}
                disabled={!file || analyzing || detecting || processing}
                className="mt-5 inline-flex w-full items-center justify-center rounded-2xl bg-cyan-300 px-4 py-3 font-medium text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-300"
              >
                {processing ? (
                  <>
                    <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                    Applying Trim...
                  </>
                ) : (
                  "Apply Trim"
                )}
              </button>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="mb-4 flex items-center gap-2 text-cyan-100">
                <Download className="h-5 w-5" />
                <h2 className="text-lg font-medium">Download</h2>
              </div>
              <button
                type="button"
                onClick={handleDownload}
                className={`inline-flex w-full items-center justify-center rounded-2xl px-4 py-3 font-medium transition ${
                  processedFileUrl
                    ? "bg-white text-slate-950 hover:bg-slate-100"
                    : "cursor-not-allowed bg-slate-800 text-slate-500"
                }`}
                disabled={!processedFileUrl || downloading}
              >
                {downloading ? "Downloading..." : "Download Processed WAV"}
              </button>
              <p className="mt-3 text-sm leading-6 text-slate-400">
                트림 적용이 끝나면 처리된 WAV 파일을 바로 내려받을 수 있습니다.
              </p>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
