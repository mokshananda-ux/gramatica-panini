import Link from "next/link";
import { search } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = {
  searchParams: Promise<{ q?: string }>;
};

export default async function SearchPage({ searchParams }: Props) {
  const { q } = await searchParams;
  const query = (q || "").trim();

  if (!query) {
    return (
      <div className="space-y-4">
        <h1 className="font-serif text-2xl font-semibold">Búsqueda</h1>
        <p className="text-ink-700/60">
          Escribe un id de sūtra (p. ej. <code>1.1.1</code>) o un término en el
          buscador de la cabecera.
        </p>
      </div>
    );
  }

  let data;
  try {
    data = await search(query, 40);
  } catch {
    return (
      <div className="rounded-lg border border-terracotta-500/30 p-6 text-center">
        Error al buscar. ¿Está la API en marcha?
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-2xl font-semibold text-ink-800">
          Resultados para «{query}»
        </h1>
        <p className="mt-1 text-sm text-ink-700/50">
          {data.total} coincidencia{data.total !== 1 ? "s" : ""}
        </p>
      </div>

      <div className="grid gap-2">
        {data.items.map((item) => (
          <Link
            key={item.id}
            href={`/sutras/${item.id}`}
            className="block rounded-lg border border-parchment-200 bg-white px-4 py-3 hover:border-saffron-400/50 hover:shadow-sm"
          >
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-sm font-semibold text-saffron-600">
                {item.id}
              </span>
              <span className="font-serif text-ink-800">{item.sanskrit}</span>
              <span className="ml-auto text-[10px] uppercase tracking-wider text-ink-700/35">
                {item.match_in}
              </span>
            </div>
            <p className="mt-1 line-clamp-2 text-sm text-ink-700/70">
              {item.translation_preview}
            </p>
          </Link>
        ))}
        {data.items.length === 0 && (
          <p className="py-8 text-center text-ink-700/50">Sin resultados.</p>
        )}
      </div>
    </div>
  );
}
