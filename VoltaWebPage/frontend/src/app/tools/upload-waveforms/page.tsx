"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  CheckCircle2,
  Clock3,
  Music2,
  Plus,
  Upload,
  Waves,
} from "lucide-react";

type UploadStatus = "queued" | "uploading" | "decoding" | "ready" | "error";

type UploadTrack = {
  id: string;
  file: File;
  name: string;
  duration: number | null;
  waveform: number[];
  progress: number;
  status: UploadStatus;
  error?: string;
  colorClass: string;
};

type ParsedWavHeader = {
  audioFormat: number;
  channelCount: number;
  sampleRate: number;
  bitsPerSample: number;
  blockAlign: number;
  dataOffset: number;
  dataSize: number;
  duration: number;
};

const trackColors = [
  "bg-purple-500",
  "bg-fuchsia-500",
  "bg-cyan-400",
  "bg-emerald-400",
  "bg-amber-400",
  "bg-orange-500",
  "bg-rose-400",
  "bg-lime-400",
  "bg-sky-400",
  "bg-indigo-400",
];

const timelineMarks = ["0:00", "0:30", "1:00", "1:30", "2:00", "2:30", "3:00", "3:30"];

function formatSeconds(seconds: number | null) {
  if (seconds == null) {
    return "--:--";
  }

  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0");
  return `${mins}:${secs}`;
}

function getStatusLabel(status: UploadStatus) {
  switch (status) {
    case "queued":
      return "Queued";
    case "uploading":
      return "Uploading";
    case "decoding":
      return "Generating waveform";
    case "ready":
      return "Ready";
    case "error":
      return "Error";
    default:
      return status;
  }
}

function sleep(ms: number) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function readAscii(view: DataView, start: number, length: number) {
  let result = "";
  for (let i = 0; i < length; i += 1) {
    result += String.fromCharCode(view.getUint8(start + i));
  }
  return result;
}

async function parseWavHeader(file: File): Promise<ParsedWavHeader | null> {
  const headerBytes = Math.min(file.size, 128 * 1024);
  const buffer = await file.slice(0, headerBytes).arrayBuffer();
  const view = new DataView(buffer);

  if (view.byteLength < 44) {
    return null;
  }

  if (readAscii(view, 0, 4) !== "RIFF" || readAscii(view, 8, 4) !== "WAVE") {
    return null;
  }

  let offset = 12;
  let audioFormat = 1;
  let channelCount = 1;
  let sampleRate = 44100;
  let bitsPerSample = 16;
  let blockAlign = 2;
  let dataOffset = -1;
  let dataSize = 0;

  while (offset + 8 <= view.byteLength) {
    const chunkId = readAscii(view, offset, 4);
    const chunkSize = view.getUint32(offset + 4, true);
    const chunkDataOffset = offset + 8;

    if (chunkId === "fmt " && chunkDataOffset + 16 <= view.byteLength) {
      audioFormat = view.getUint16(chunkDataOffset, true);
      channelCount = view.getUint16(chunkDataOffset + 2, true);
      sampleRate = view.getUint32(chunkDataOffset + 4, true);
      blockAlign = view.getUint16(chunkDataOffset + 12, true);
      bitsPerSample = view.getUint16(chunkDataOffset + 14, true);
    } else if (chunkId === "data") {
      dataOffset = chunkDataOffset;
      dataSize = chunkSize;
      break;
    }

    offset = chunkDataOffset + chunkSize + (chunkSize % 2);
  }

  if (dataOffset < 0 || dataSize <= 0 || blockAlign <= 0 || sampleRate <= 0) {
    return null;
  }

  const duration = dataSize / blockAlign / sampleRate;
  return {
    audioFormat,
    channelCount,
    sampleRate,
    bitsPerSample,
    blockAlign,
    dataOffset,
    dataSize,
    duration,
  };
}

function readSampleAmplitude(
  view: DataView,
  byteOffset: number,
  header: ParsedWavHeader,
) {
  const bytesPerChannel = Math.max(1, header.bitsPerSample / 8);
  const availableChannels = Math.max(1, header.channelCount);
  let sum = 0;

  for (let channel = 0; channel < availableChannels; channel += 1) {
    const sampleOffset = byteOffset + channel * bytesPerChannel;
    let normalized = 0;

    if (header.audioFormat === 3 && bytesPerChannel === 4) {
      normalized = Math.abs(view.getFloat32(sampleOffset, true));
    } else if (bytesPerChannel === 1) {
      normalized = Math.abs((view.getUint8(sampleOffset) - 128) / 128);
    } else if (bytesPerChannel === 2) {
      normalized = Math.abs(view.getInt16(sampleOffset, true) / 32768);
    } else if (bytesPerChannel === 3) {
      const b0 = view.getUint8(sampleOffset);
      const b1 = view.getUint8(sampleOffset + 1);
      const b2 = view.getUint8(sampleOffset + 2);
      let value = b0 | (b1 << 8) | (b2 << 16);
      if (value & 0x800000) {
        value |= ~0xffffff;
      }
      normalized = Math.abs(value / 8388608);
    } else if (bytesPerChannel === 4) {
      normalized = Math.abs(view.getInt32(sampleOffset, true) / 2147483648);
    }

    sum += normalized;
  }

  return Math.min(1, sum / availableChannels);
}

async function readApproximateWaveform(
  file: File,
  header: ParsedWavHeader | null,
  bars = 160,
) {
  if (!header) {
    const fallbackBytes = new Uint8Array(await file.slice(0, Math.min(file.size, 256 * 1024)).arrayBuffer());
    if (fallbackBytes.length === 0) {
      return Array.from({ length: bars }, () => 8);
    }

    const blockSize = Math.max(1, Math.floor(fallbackBytes.length / bars));
    return Array.from({ length: bars }, (_, index) => {
      const start = index * blockSize;
      const end = Math.min(fallbackBytes.length, start + blockSize);
      let peak = 0;

      for (let i = start; i < end; i += 1) {
        peak = Math.max(peak, Math.abs(fallbackBytes[i] - 128) / 128);
      }

      return Math.max(6, Math.round(peak * 100));
    });
  }

  const windowCount = 20;
  const barsPerWindow = Math.ceil(bars / windowCount);
  const windows = Array.from({ length: windowCount }, (_, index) => {
    const relativeStart = (header.dataSize * index) / windowCount;
    const absoluteStart = header.dataOffset + Math.floor(relativeStart);
    const windowSize = Math.min(
      16 * 1024,
      Math.max(header.blockAlign * 64, Math.floor(header.dataSize / windowCount)),
    );
    const absoluteEnd = Math.min(file.size, absoluteStart + windowSize);
    return { absoluteStart, absoluteEnd };
  });

  const buffers = await Promise.all(
    windows.map((windowInfo) => file.slice(windowInfo.absoluteStart, windowInfo.absoluteEnd).arrayBuffer()),
  );

  const waveform = buffers.flatMap((buffer) => {
    const view = new DataView(buffer);
    const frameCount = Math.max(1, Math.floor(view.byteLength / header.blockAlign));
    const framesPerBar = Math.max(1, Math.floor(frameCount / barsPerWindow));

    return Array.from({ length: barsPerWindow }, (_, index) => {
      const frameStart = index * framesPerBar;
      const frameEnd = Math.min(frameCount, frameStart + framesPerBar);
      let peak = 0;

      for (let frameIndex = frameStart; frameIndex < frameEnd; frameIndex += 1) {
        const byteOffset = frameIndex * header.blockAlign;
        peak = Math.max(peak, readSampleAmplitude(view, byteOffset, header));
      }

      return Math.max(6, Math.round(peak * 100));
    });
  });

  return waveform.slice(0, bars);
}

async function readAudioDuration(file: File, header: ParsedWavHeader | null) {
  if (header) {
    return header.duration;
  }

  return await new Promise<number>((resolve, reject) => {
    const objectUrl = window.URL.createObjectURL(file);
    const audio = new Audio();

    const cleanup = () => {
      audio.src = "";
      window.URL.revokeObjectURL(objectUrl);
    };

    audio.preload = "metadata";
    audio.onloadedmetadata = () => {
      const duration = Number.isFinite(audio.duration) ? audio.duration : 0;
      cleanup();
      resolve(duration);
    };
    audio.onerror = () => {
      cleanup();
      reject(new Error("Audio metadata could not be read."));
    };
    audio.src = objectUrl;
  });
}

function UploadProgressPill({
  progress,
  status,
}: {
  progress: number;
  status: UploadStatus;
}) {
  const width = Math.max(4, Math.min(100, progress));

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-[11px] text-zinc-500">
        <span>{getStatusLabel(status)}</span>
        <span>{Math.round(progress)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-zinc-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-cyan-300 to-purple-400 transition-[width] duration-300"
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}

function TrackWaveform({
  track,
  active,
  maxDuration,
}: {
  track: UploadTrack;
  active: boolean;
  maxDuration: number;
}) {
  const waveform = useMemo(
    () =>
      track.waveform.length > 0
        ? track.waveform
        : Array.from({ length: 160 }, (_, index) => 8 + ((index + 3) % 10) * 2),
    [track.waveform],
  );

  return (
    <div
      className={`relative h-14 border-b border-zinc-800/80 ${
        active ? "bg-purple-500/5" : "bg-zinc-950/20"
      }`}
    >
      <div
        className="absolute left-3 top-1/2 flex h-10 -translate-y-1/2 items-center gap-[2px] overflow-hidden rounded-md border border-zinc-800/70 bg-zinc-950/90 px-2"
        style={{
          width: `${Math.max(10, Math.min(100, ((track.duration ?? maxDuration) / maxDuration) * 100 - 4))}%`,
        }}
      >
        {waveform.map((height, index) => (
          <div
            key={`${track.id}-${index}`}
            className={`w-1 rounded-full ${active ? track.colorClass : "bg-zinc-600/70"}`}
            style={{ height: `${height}%`, opacity: active ? 0.95 : 0.55 }}
          />
        ))}
      </div>

      {track.status !== "ready" ? (
        <div className="absolute left-[42%] top-1/2 -translate-y-1/2 rounded-md border border-cyan-400/30 bg-cyan-400/15 px-4 py-1 text-xs text-cyan-100">
          {getStatusLabel(track.status)}
        </div>
      ) : null}
    </div>
  );
}

export default function UploadWaveformTestPage() {
  const [tracks, setTracks] = useState<UploadTrack[]>([]);
  const [selectedTrackId, setSelectedTrackId] = useState<string | null>(null);
  const activeTrackIdRef = useRef<string | null>(null);
  const generationRef = useRef(0);

  const selectedTrack =
    tracks.find((track) => track.id === selectedTrackId) ?? tracks[0] ?? null;
  const maxDuration = Math.max(
    30,
    ...tracks.map((track) => track.duration ?? 0),
  );

  useEffect(() => {
    if (activeTrackIdRef.current) {
      return;
    }

    const nextTrack = tracks.find((track) => track.status === "queued");
    if (!nextTrack) {
      return;
    }

    activeTrackIdRef.current = nextTrack.id;
    const generation = generationRef.current;

    const run = async () => {
      try {
        setTracks((current) =>
          current.map((track) =>
            track.id === nextTrack.id
              ? { ...track, status: "uploading", progress: 15 }
              : track,
          ),
        );

        await sleep(60);
        if (generation !== generationRef.current) {
          return;
        }

        setTracks((current) =>
          current.map((track) =>
            track.id === nextTrack.id
              ? { ...track, status: "uploading", progress: 42 }
              : track,
          ),
        );

        const header = await parseWavHeader(nextTrack.file);
        const [duration, waveform] = await Promise.all([
          readAudioDuration(nextTrack.file, header),
          readApproximateWaveform(nextTrack.file, header),
        ]);

        if (generation !== generationRef.current) {
          return;
        }

        setTracks((current) =>
          current.map((track) =>
            track.id === nextTrack.id
              ? { ...track, status: "decoding", progress: 80 }
              : track,
          ),
        );

        await sleep(50);
        if (generation !== generationRef.current) {
          return;
        }

        setTracks((current) =>
          current.map((track) =>
            track.id === nextTrack.id
              ? {
                  ...track,
                  duration,
                  waveform,
                  progress: 100,
                  status: "ready",
                }
              : track,
          ),
        );
      } catch (error) {
        if (generation !== generationRef.current) {
          return;
        }

        setTracks((current) =>
          current.map((track) =>
            track.id === nextTrack.id
              ? {
                  ...track,
                  status: "error",
                  error:
                    error instanceof Error
                      ? error.message
                      : "Waveform generation failed.",
                }
              : track,
          ),
        );
      } finally {
        if (activeTrackIdRef.current === nextTrack.id) {
          activeTrackIdRef.current = null;
        }
      }
    };

    void run();
  }, [tracks]);

  function handleFilesSelected(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    if (files.length === 0) {
      return;
    }

    const wavFiles = files.filter((file) => file.name.toLowerCase().endsWith(".wav"));
    const newTracks: UploadTrack[] = wavFiles.map((file, index) => ({
      id: `${file.name}-${file.size}-${Date.now()}-${index}`,
      file,
      name: file.name,
      duration: null,
      waveform: [],
      progress: 4,
      status: "queued",
      colorClass: trackColors[(tracks.length + index) % trackColors.length],
    }));

    setTracks((current) => [...current, ...newTracks]);
    setSelectedTrackId((current) => current ?? newTracks[0]?.id ?? null);
    event.target.value = "";
  }

  const readyCount = tracks.filter((track) => track.status === "ready").length;

  return (
    <div className="min-h-screen bg-[#090b10] text-zinc-100">
      <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col overflow-hidden">
        <header className="flex flex-col gap-4 border-b border-zinc-800 bg-zinc-950/95 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2 text-sm uppercase tracking-[0.28em] text-emerald-200/70">
              <Waves size={16} />
              Upload Flow Test
            </div>
            <h1 className="mt-2 text-3xl font-semibold text-white">
              Multi WAV Upload + Waveform Timeline
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-7 text-zinc-400">
              여러 WAV 파일 업로드 시 progress bar와 트랙 waveform이 DAW 스타일로 쌓이는
              UI만 빠르게 검증하는 테스트 페이지입니다.
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <label className="inline-flex cursor-pointer items-center justify-center rounded-2xl bg-emerald-400 px-5 py-3 font-medium text-zinc-950 transition hover:bg-emerald-300">
              <Upload size={16} className="mr-2" />
              Select WAV Files
              <input
                type="file"
                accept=".wav,audio/wav"
                multiple
                className="hidden"
                onChange={handleFilesSelected}
              />
            </label>
            <button
              type="button"
              onClick={() => {
                generationRef.current += 1;
                activeTrackIdRef.current = null;
                setTracks([]);
                setSelectedTrackId(null);
              }}
              className="inline-flex items-center justify-center rounded-2xl border border-zinc-700 bg-zinc-900 px-5 py-3 font-medium text-zinc-200 transition hover:bg-zinc-800"
            >
              <Plus size={16} className="mr-2 rotate-45" />
              Reset
            </button>
          </div>
        </header>

        <div className="grid flex-1 gap-0 xl:grid-cols-[300px_minmax(0,1fr)]">
          <aside className="border-r border-zinc-800 bg-zinc-950 p-3">
            <div className="mb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-semibold">Tracks ({tracks.length})</h2>
                <p className="text-xs text-zinc-500">
                  Ready {readyCount} / {tracks.length}
                </p>
              </div>
              <div className="rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-1 text-xs text-zinc-400">
                batch-ready
              </div>
            </div>

            <div className="space-y-2 overflow-y-auto pr-1 xl:max-h-[calc(100vh-220px)]">
              {tracks.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-zinc-700 bg-zinc-900/50 p-5 text-sm leading-6 text-zinc-500">
                  WAV 파일 여러 개를 선택하면 트랙별 progress와 waveform이 이 패널과
                  타임라인에 바로 반영됩니다.
                </div>
              ) : null}

              {tracks.map((track) => (
                <button
                  key={track.id}
                  type="button"
                  onClick={() => setSelectedTrackId(track.id)}
                  className={`grid w-full grid-cols-[46px_1fr_74px] items-center gap-2 rounded-xl border px-2 py-2 text-left transition ${
                    selectedTrack?.id === track.id
                      ? "border-purple-500/70 bg-purple-500/10"
                      : "border-zinc-800 bg-zinc-900/70 hover:bg-zinc-800/70"
                  }`}
                >
                  <div className="flex gap-1">
                    <span className="rounded bg-zinc-800 px-1.5 py-1 text-[10px] text-zinc-400">
                      M
                    </span>
                    <span className="rounded bg-zinc-800 px-1.5 py-1 text-[10px] text-zinc-400">
                      S
                    </span>
                  </div>

                  <div className="min-w-0">
                    <div className="truncate text-xs font-medium text-zinc-100">
                      {track.name.replace(".wav", "")}
                    </div>
                    <div className="mt-1">
                      <UploadProgressPill progress={track.progress} status={track.status} />
                    </div>
                  </div>

                  <div className="text-right text-[10px] text-zinc-400">
                    <div>{formatSeconds(track.duration)}</div>
                    <div className="mt-1">
                      {track.status === "ready" ? (
                        <span className="inline-flex items-center gap-1 text-emerald-300">
                          <CheckCircle2 size={11} />
                          ready
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-zinc-500">
                          <Clock3 size={11} />
                          wait
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </aside>

          <main className="bg-[#0d1118] p-3">
            <div className="mb-2 flex items-center justify-between text-xs text-zinc-500">
              <div className="flex flex-wrap gap-10 pl-2 xl:gap-20">
                {timelineMarks.map((mark) => (
                  <span key={mark}>{mark}</span>
                ))}
              </div>
              <span>Timeline</span>
            </div>

            <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-950/80">
              <div className="relative h-11 border-b border-zinc-800 bg-purple-500/5">
                <div className="absolute left-[42%] top-0 h-full w-px bg-purple-300 shadow-[0_0_14px_rgba(168,85,247,0.8)]" />
              </div>

              {tracks.length === 0 ? (
                <div className="flex h-[360px] items-center justify-center text-sm text-zinc-500">
                  <div className="text-center">
                    <Music2 className="mx-auto mb-3 h-8 w-8 text-zinc-600" />
                    업로드된 트랙이 아직 없습니다.
                  </div>
                </div>
              ) : (
                tracks.map((track) => (
                  <TrackWaveform
                    key={track.id}
                    track={track}
                    active={selectedTrack?.id === track.id}
                    maxDuration={maxDuration}
                  />
                ))
              )}
            </div>

            <div className="mt-3 grid gap-3 lg:grid-cols-[1.2fr_0.8fr]">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-4">
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-zinc-100">
                  <Upload size={16} />
                  Upload State
                </div>
                <div className="space-y-3">
                  {tracks.length === 0 ? (
                    <p className="text-sm text-zinc-500">
                      이 영역은 FR-UPLOAD-003 테스트용입니다. 각 트랙의 업로드 상태를
                      progress bar로 보여줍니다.
                    </p>
                  ) : (
                    tracks.map((track) => (
                      <div
                        key={`${track.id}-status`}
                        className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3"
                      >
                        <div className="mb-2 flex items-center justify-between text-sm">
                          <span className="truncate text-zinc-100">{track.name}</span>
                          <span className="text-zinc-500">{getStatusLabel(track.status)}</span>
                        </div>
                        <UploadProgressPill progress={track.progress} status={track.status} />
                        {track.error ? (
                          <p className="mt-2 text-xs text-rose-300">{track.error}</p>
                        ) : null}
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-4">
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-zinc-100">
                  <Waves size={16} />
                  Selected Track
                </div>
                {selectedTrack ? (
                  <div className="space-y-3">
                    <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
                      <div className="text-sm font-medium text-zinc-100">
                        {selectedTrack.name}
                      </div>
                      <div className="mt-1 text-xs text-zinc-500">
                        duration {formatSeconds(selectedTrack.duration)} · status{" "}
                        {getStatusLabel(selectedTrack.status)}
                      </div>
                    </div>
                    <div className="rounded-xl border border-zinc-800 bg-zinc-900/70 p-3">
                      <p className="text-xs uppercase tracking-[0.24em] text-zinc-500">
                        Waveform Preview
                      </p>
                      <div className="mt-3 flex h-24 items-end gap-[2px] overflow-hidden rounded-xl bg-zinc-950 px-2 py-3">
                        {(selectedTrack.waveform.length > 0
                          ? selectedTrack.waveform
                          : Array.from({ length: 90 }, (_, index) => 10 + (index % 9) * 5)
                        )
                          .slice(0, 90)
                          .map((height, index) => (
                            <div
                              key={`${selectedTrack.id}-preview-${index}`}
                              className={`${selectedTrack.colorClass} w-1 rounded-full`}
                              style={{ height: `${height}%` }}
                            />
                          ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-zinc-500">
                    업로드 후 트랙을 선택하면 waveform preview를 이 패널에서 볼 수 있습니다.
                  </p>
                )}
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
