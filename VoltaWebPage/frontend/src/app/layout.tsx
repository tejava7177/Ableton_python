import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Volta Audio Tools",
  description: "Low / High Cut Tester",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
