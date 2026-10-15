import { AdhyayaNav } from "@/components/AdhyayaNav";
import { SutraCard } from "@/components/SutraCard";
import { listSutras } from "@/lib/api";
import { ADHYAYA_LABELS } from "@/lib/utils";
import Link from "next/link";

export const dynamic = "force-dynamic";

type Props = {
  searchParams: Promise<{ adhyaya?: string; pada?: string; page?: string }>;
};

export default async function SutrasPage({ searchParams }: Props) {
  const sp = await searchParams;
  const adhyaya = sp.adhyaya ? parseInt(sp.adhyaya, 10) : undefined;
  const pada = sp.pada ? parseInt(sp.pada, 10) : undefined;
  const page = Math.max(1, parseInt(sp.page || "1", 10) || 1);
  const limit = 40;
  const offset = (page - 1) * limit;

  let data;
  try {
    data = await listSutras({ adhyaya, pada, limit, offset });
  } catch {
    return (
      <div className="rounded-lg border border-terracotta-500/30 bg-terracotta-500/5 p-6 text-center">
        <p className="text-ink-800">No se pudo conectar con la API.</p>
        <p className="mt-1 text-sm text-ink-700/60">
          Comprueba que FastAPI esté en marcha en{" "}
          <code className="text-xs">localhost:8000</code>.
        </p>
      </div>
    );
  }

  const totalPages = Math.max(1, Math.ceil(data.total / limit));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-2xl font-semibold text-ink-800">
          {adhyaya != null
            ? `Adhyāya ${adhyaya}${pada != null ? `.${pada}` : ""}`
            : "Todos los sūtras"}
        </h1>
        {adhyaya != null && (
          <p className="mt-1 text-sm text-ink-700/60">
            {ADHYAYA_LABELS[adhyaya]}
          </p>
        )}
        <p className="mt-1 text-sm text-ink-700/50">
          {data.total} sūtra{data.total !== 1 ? "s" : ""}
        </p>
      </div>

      <AdhyayaNav currentAdhyaya={adhyaya} currentPada={pada} />

      <div className="grid gap-2">
        {data.items.map((item) => (
          <SutraCard key={item.id} item={item} />
        ))}
        {data.items.length === 0 && (
          <p className="py-8 text-center text-ink-700/50">
            No hay sūtras en este rango.
          </p>
        )}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-2">
          {page > 1 && (
            <Link
              href={`/sutras?${new URLSearchParams({
                ...(adhyaya != null ? { adhyaya: String(adhyaya) } : {}),
                ...(pada != null ? { pada: String(pada) } : {}),
                page: String(page - 1),
              })}`}
              className="rounded-md border border-parchment-300 px-3 py-1.5 text-sm hover:bg-parchment-100"
            >
              ← Anterior
            </Link>
          )}
          <span className="text-sm text-ink-700/50">
            {page} / {totalPages}
          </span>
          {page < totalPages && (
            <Link
              href={`/sutras?${new URLSearchParams({
                ...(adhyaya != null ? { adhyaya: String(adhyaya) } : {}),
                ...(pada != null ? { pada: String(pada) } : {}),
                page: String(page + 1),
              })}`}
              className="rounded-md border border-parchment-300 px-3 py-1.5 text-sm hover:bg-parchment-100"
            >
              Siguiente →
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
