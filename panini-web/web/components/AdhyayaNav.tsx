import Link from "next/link";
import { ADHYAYA_LABELS, cn } from "@/lib/utils";

export function AdhyayaNav({
  currentAdhyaya,
  currentPada,
}: {
  currentAdhyaya?: number | null;
  currentPada?: number | null;
}) {
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-1.5">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((a) => (
          <Link
            key={a}
            href={`/sutras?adhyaya=${a}`}
            className={cn(
              "rounded-full px-3 py-1 text-sm font-medium transition",
              currentAdhyaya === a
                ? "bg-ink-800 text-parchment-50"
                : "bg-parchment-200 text-ink-700 hover:bg-parchment-300"
            )}
            title={ADHYAYA_LABELS[a]}
          >
            {a}
          </Link>
        ))}
      </div>
      {currentAdhyaya != null && (
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-xs text-ink-700/50">Pada:</span>
          {[1, 2, 3, 4].map((p) => (
            <Link
              key={p}
              href={`/sutras?adhyaya=${currentAdhyaya}&pada=${p}`}
              className={cn(
                "rounded-full px-2.5 py-0.5 text-xs font-medium transition",
                currentPada === p
                  ? "bg-saffron-500 text-white"
                  : "bg-parchment-100 text-ink-700 hover:bg-parchment-200"
              )}
            >
              {p}
            </Link>
          ))}
          <Link
            href={`/sutras?adhyaya=${currentAdhyaya}`}
            className="ml-1 text-xs text-ink-700/50 underline-offset-2 hover:underline"
          >
            todos
          </Link>
        </div>
      )}
    </div>
  );
}
