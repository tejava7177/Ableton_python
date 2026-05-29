"use client";

type UploadPanelProps = {
  projectName: string;
  onProjectNameChange: (value: string) => void;
  onCreateProject: () => void;
  onFileChange: (file: File | null) => void;
  onUploadTrack: () => void;
  hasProject: boolean;
  isBusy: boolean;
};

export function UploadPanel({
  projectName,
  onProjectNameChange,
  onCreateProject,
  onFileChange,
  onUploadTrack,
  hasProject,
  isBusy,
}: UploadPanelProps) {
  return (
    <section className="rounded-2xl bg-panel p-6 shadow-lg">
      <h2 className="text-xl font-semibold">Project Setup</h2>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <label className="block text-sm text-slate-300">Project Name</label>
          <input
            className="w-full rounded-lg border border-slate-600 bg-card px-4 py-3"
            value={projectName}
            onChange={(event) => onProjectNameChange(event.target.value)}
            placeholder="Hiphop Demo Mix"
          />
          <button
            className="rounded-lg bg-accent px-4 py-2 font-medium text-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
            onClick={onCreateProject}
            disabled={isBusy}
          >
            Create Project
          </button>
        </div>

        <div className="space-y-2">
          <label className="block text-sm text-slate-300">WAV Upload</label>
          <input
            className="block w-full rounded-lg border border-dashed border-slate-600 bg-card px-4 py-3"
            type="file"
            accept=".wav,audio/wav"
            onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
          />
          <button
            className="rounded-lg border border-slate-500 px-4 py-2 font-medium disabled:cursor-not-allowed disabled:opacity-40"
            onClick={onUploadTrack}
            disabled={!hasProject || isBusy}
          >
            Upload Track
          </button>
        </div>
      </div>
    </section>
  );
}

