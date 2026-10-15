"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Inicio" },
  { href: "/sutras", label: "Sūtras" },
  { href: "/annexes/pratyaharas", label: "Pratyāhāras" },
  { href: "/annexes/dhatus", label: "Dhātus" },
  { href: "/annexes/nominal-bases", label: "Bases" },
];

export function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const [q, setQ] = useState("");

  function onSearch(e: FormEvent) {
    e.preventDefault();
    const query = q.trim();
    if (!query) return;
    router.push(`/search?q=${encodeURIComponent(query)}`);
  }

  return (
    <header className="sticky top-0 z-40 border-b border-parchment-200 bg-parchment-50/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center gap-3 px-4 py-3">
        <Link
          href="/"
          className="font-serif text-lg font-semibold tracking-tight text-ink-800"
        >
          Aṣṭādhyāyī
          <span className="ml-1.5 text-sm font-normal text-ink-700/60">
            es
          </span>
        </Link>

        <nav className="ml-2 hidden items-center gap-1 sm:flex">
          {NAV.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded-md px-2.5 py-1 text-sm transition-colors",
                  active
                    ? "bg-saffron-500/15 font-medium text-saffron-600"
                    : "text-ink-700/70 hover:bg-parchment-200 hover:text-ink-800"
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <form onSubmit={onSearch} className="ml-auto flex min-w-[12rem] flex-1 max-w-xs">
          <input
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Buscar sūtra o texto…"
            className="w-full rounded-l-md border border-parchment-300 bg-white px-3 py-1.5 text-sm text-ink-800 placeholder:text-ink-700/40 focus:border-saffron-400 focus:outline-none focus:ring-1 focus:ring-saffron-400"
          />
          <button
            type="submit"
            className="rounded-r-md bg-ink-800 px-3 py-1.5 text-sm text-parchment-50 hover:bg-ink-700"
          >
            Buscar
          </button>
        </form>
      </div>
    </header>
  );
}
