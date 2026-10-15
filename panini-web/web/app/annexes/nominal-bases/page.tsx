import { listNominalBases } from "@/lib/api";
import Link from "next/link";

export const dynamic = "force-dynamic";

type Props = {
  searchParams: Promise<{ page?: string }>;
};

export default async function NominalBasesPage({ searchParams }: Props) {
  const sp = await searchParams;
  const page = Math.max(1, parseInt(sp.page || "1", 10) || 1);
  const limit = 60;
  const offset = (page - 1) * limit;

  let data;
  try {
    data = await listNominalBases({ limit, offset });
  } catch {
    return (
      <p className="text-center text-ink-700/50">
        No se pudieron cargar las bases nominales.
      </p>
    );
  }

  const totalPages = Math.max(1, Math.ceil(data.total / limit));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-2xl font-semibold text-ink-800">
          Bases nominales
        </h1>
        <p className="mt-1 text-sm text-ink-700/60">
          {data.total} entradas
        </p>
      </div>

      <div className="overflow-hidden rounded-lg border border-parchment-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-parchment-200 bg-parchment-100/80 text-xs uppercase tracking-wide text-ink-700/50">
              <th className="px-3 py-2 font-medium">Base</th>
              <th className="px-3 py-2 font-medium">Grupo</th>
              <th className="px-3 py-2 font-medium">Sūtra / ref.</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((b) => (
              <tr
                key={b.id}
                className="border-b border-parchment-100 last:border-0 hover:bg-parchment-50"
              >
                <td className="px-3 py-2 font-serif font-medium text-ink-800">
                  {b.base}
                </td>
                <td className="px-3 py-2 text-xs text-ink-700/60">
                  {b.group_name || "—"}
                </td>
                <td className="px-3 py-2 font-mono text-xs text-ink-700/50">
                  {b.sutra_ref || "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center gap-3 text-sm">
          {page > 1 && (
            <Link
              href={`/annexes/nominal-bases?page=${page - 1}`}
              className="rounded-md border border-parchment-300 px-3 py-1.5 hover:bg-parchment-100"
            >
              ← Anterior
            </Link>
          )}
          <span className="text-ink-700/50">
            {page} / {totalPages}
          </span>
          {page < totalPages && (
            <Link
              href={`/annexes/nominal-bases?page=${page + 1}`}
              className="rounded-md border border-parchment-300 px-3 py-1.5 hover:bg-parchment-100"
            >
              Siguiente →
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
