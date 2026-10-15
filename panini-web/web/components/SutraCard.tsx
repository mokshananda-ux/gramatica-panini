import Link from "next/link";
import type { SutraListItem } from "@/lib/api";

export function SutraCard({ item }: { item: SutraListItem }) {
  return (
    <Link
      href={`/sutras/${item.id}`}
      className="group block rounded-lg border border-parchment-200 bg-white px-4 py-3 shadow-sm transition hover:border-saffron-400/50 hover:shadow-md"
    >
      <div className="flex items-baseline gap-2">
        <span className="font-mono text-sm font-semibold text-saffron-600">
          {item.id}
        </span>
        <span className="font-serif text-base text-ink-800 group-hover:text-terracotta-600">
          {item.sanskrit}
        </span>
      </div>
      <p className="mt-1 line-clamp-2 text-sm text-ink-700/75">
        {item.translation_preview}
      </p>
      {item.notes_count > 0 && (
        <p className="mt-1.5 text-xs text-ink-700/45">
          {item.notes_count} nota{item.notes_count !== 1 ? "s" : ""}
        </p>
      )}
    </Link>
  );
}
