import Link from "next/link";
import { listPratyaharas } from "@/lib/api";
import { isSimpleSutraId } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function PratyaharasPage() {
  let items;
  try {
    items = await listPratyaharas();
  } catch {
    return (
      <p className="text-center text-ink-700/50">
        No se pudieron cargar los pratyāhāras. ¿API en marcha?
      </p>
    );
  }

  // Ordenar por order_index si existe
  const sorted = [...items].sort(
    (a, b) => (a.order_index ?? 999) - (b.order_index ?? 999)
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-2xl font-semibold text-ink-800">
          Pratyāhāras
        </h1>
        <p className="mt-1 text-sm text-ink-700/60">
          {sorted.length} siglas técnicas usadas en la Aṣṭādhyāyī
        </p>
      </div>

      <div className="overflow-hidden rounded-lg border border-parchment-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-parchment-200 bg-parchment-100/80 text-xs uppercase tracking-wide text-ink-700/50">
              <th className="px-4 py-2.5 font-medium">Sigla</th>
              <th className="px-4 py-2.5 font-medium">Definición</th>
              <th className="px-4 py-2.5 font-medium">Sūtra</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((p) => (
              <tr
                key={p.id}
                className="border-b border-parchment-100 last:border-0 hover:bg-parchment-50"
              >
                <td className="px-4 py-2.5 font-mono font-semibold text-saffron-600">
                  {p.id}
                </td>
                <td className="px-4 py-2.5 text-ink-700/85">
                  {p.definition_full || p.expansion}
                </td>
                <td className="px-4 py-2.5">
                  {p.defined_in && isSimpleSutraId(p.defined_in) ? (
                    <Link
                      href={`/sutras/${p.defined_in}`}
                      className="font-mono text-saffron-600 hover:underline"
                    >
                      {p.defined_in}
                    </Link>
                  ) : (
                    <span className="font-mono text-ink-700/50">
                      {p.defined_in || "—"}
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
