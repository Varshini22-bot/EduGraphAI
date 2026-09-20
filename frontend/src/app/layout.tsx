import type { Metadata } from "next";
import { AuthProvider } from "@/context/AuthContext";
import { SettingsProvider } from "@/context/SettingsContext";
import { ToastProvider } from "@/context/ToastContext";
import "./globals.css";

export const metadata: Metadata = {
  title: "Knowledge Graph Learning Assistant",
  description:
    "An AI-powered learning assistant that explains topics and maps how they connect.",
};

// Same three typefaces and weights as before (Space Grotesk 500/600/700,
// Inter 400/500/600, JetBrains Mono 400/500), but requested by the browser
// instead of by the Next.js server at compile time. `display=swap` renders
// the fallback immediately, and the --font-* variables these map to are
// defined in globals.css.
const GOOGLE_FONTS_HREF =
  "https://fonts.googleapis.com/css2" +
  "?family=Space+Grotesk:wght@500;600;700" +
  "&family=Inter:wght@400;500;600" +
  "&family=JetBrains+Mono:wght@400;500" +
  "&display=swap";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="stylesheet" href={GOOGLE_FONTS_HREF} />
      </head>
      <body className="font-body bg-base text-ink-primary antialiased">
        <SettingsProvider>
          <ToastProvider>
            <AuthProvider>{children}</AuthProvider>
          </ToastProvider>
        </SettingsProvider>
      </body>
    </html>
  );
}
