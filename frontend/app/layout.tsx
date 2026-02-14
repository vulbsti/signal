import type { Metadata } from "next";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/playfair-display/700.css";
import "./globals.css";
import NavBar from "@/components/NavBar";

export const metadata: Metadata = {
  title: "Signal Flow",
  description: "Your personal noise reducer — powered by Gemini",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-signal-bg text-gray-200 antialiased">
        <NavBar />
        <main className="pt-20 px-6 max-w-7xl mx-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
