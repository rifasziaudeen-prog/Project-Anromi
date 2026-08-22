import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Anromi — Open-World Xianxia RPG",
  description: "Cultivate, defy heaven, and transcend mortality.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // suppressHydrationWarning: browser extensions inject attributes into
    // <html>/<body> before React hydrates (e.g. data-extension-id) — ignore them.
    <html lang="en" className="h-full antialiased" suppressHydrationWarning>
      <body className="min-h-full flex flex-col" suppressHydrationWarning>{children}</body>
    </html>
  );
}
