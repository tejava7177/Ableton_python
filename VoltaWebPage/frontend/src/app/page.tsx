import Link from "next/link";

export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-2xl rounded-[32px] border border-white/10 bg-white/5 p-10 backdrop-blur">
        <p className="text-sm uppercase tracking-[0.24em] text-cyan-200/70">Volta Web Page</p>
        <h1 className="mt-4 text-4xl font-semibold text-white">Audio Tool Prototypes</h1>
        <p className="mt-4 text-base leading-7 text-slate-300">
          첫 번째 기술 검증 페이지는 WAV 업로드 후 Low Cut / High Cut 처리를 테스트하는 도구입니다.
        </p>
        <Link
          href="/tools/low-high-cut"
          className="mt-8 inline-flex rounded-2xl bg-cyan-300 px-5 py-3 font-medium text-slate-950 transition hover:bg-cyan-200"
        >
          Open Low / High Cut Tester
        </Link>
      </div>
    </main>
  );
}
