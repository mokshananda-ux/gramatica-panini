import type { Metadata } from "next";
import { Inter, Literata } from "next/font/google";
import { Header } from "@/components/Header";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const literata = Literata({
  subsets: ["latin"],
  variable: "--font-literata",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Aṣṭādhyāyī — Gramática de Pāṇini (español)",
    template: "%s · Aṣṭādhyāyī",
  },
  description:
    "Lectura interactiva de la Aṣṭādhyāyī de Pāṇini en sánscrito-español: sūtras, notas, referencias y anexos.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className={`${inter.variable} ${literata.variable}`}>
      <body className="min-h-screen font-sans">
        <Header />
        <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
        <footer className="border-t border-parchment-200 py-6 text-center text-xs text-ink-700/40">
          Aṣṭādhyāyī · Traducción al español · Sólo lectura · &copy 2026 Mokshananda-UX Dev
        </footer>
      </body>
    </html>
  );
}
