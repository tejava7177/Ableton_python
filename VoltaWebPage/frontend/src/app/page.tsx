import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-3xl rounded-[32px] border border-white/10 bg-white/5 p-10 backdrop-blur">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200/70">Volta Web Page</p>
        <h1 className="mt-4 text-4xl font-semibold text-white">Audio Tool Prototypes</h1>
        <p className="mt-4 text-base leading-7 text-slate-300">
          WAV 업로드 기반 오디오 전처리 도구를 빠르게 검증하는 테스트 페이지 모음입니다.
        </p>
        <div className="mt-8 flex flex-col gap-4 md:flex-row">
          <Link
            href="/tools/low-high-cut"
            className="inline-flex rounded-2xl bg-cyan-300 px-5 py-3 font-medium text-slate-950 transition hover:bg-cyan-200"
          >
            Open Low / High Cut Tester
          </Link>
          <Link
            href="/tools/trim"
            className="inline-flex rounded-2xl border border-cyan-200/30 bg-slate-900/70 px-5 py-3 font-medium text-cyan-100 transition hover:bg-slate-800"
          >
            Open Silence Trim Tester
          </Link>
        </div>
      </div>
    </main>
  );
}
