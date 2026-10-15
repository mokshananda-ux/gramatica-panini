import { listDhatus } from "@/lib/api";
import Link from "next/link";

export const dynamic = "force-dynamic";

type Props = {
  searchParams: Promise<{ gana?: string; page?: string }>;
};

export default async function DhatusPage({ searchParams }: Props) {
  const sp = await searchParams;
  const gana = sp.gana ? parseInt(sp.gana, 10) : undefined;
  const page = Math.max(1, parseInt(sp.page || "1", 10) || 1);
  const limit = 50;
  const offset = (page - 1) * limit;

  let data;
  try {
    data = await listDhatus({ gana, limit, offset });
  } catch {
    return (
      <p className="text-center text-ink-700/50">
        No se pudieron cargar los dhātus.
      </p>
    );
  }

  const totalPages = Math.max(1, Math.ceil(data.total / limit));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-2xl font-semibold text-ink-800">
          Dhātu-pāṭha
        </h1>
        <p className="mt-1 text-sm text-ink-700/60">
          {data.total} primitivos
          {gana != null ? ` · gaṇa ${gana}` : ""}
        </p>
      </div>

      <div className="flex flex-wrap gap-1.5">
        <Link
          href="/annexes/dhatus"
          className={`rounded-full px-3 py-1 text-xs font-medium ${
            gana == null
              ? "bg-ink-800 text-parchment-50"
              : "bg-parchment-200 text-ink-700"
          }`}
        >
          Todos
        </Link>
        {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((g) => (
          <Link
            key={g}
            href={`/annexes/dhatus?gana=${g}`}
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              gana === g
                ? "bg-ink-800 text-parchment-50"
                : "bg-parchment-200 text-ink-700 hover:bg-parchment-300"
            }`}
          >
            {g}
          </Link>
        ))}
      </div>

      <div className="overflow-hidden rounded-lg border border-parchment-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-parchment-200 bg-parchment-100/80 text-xs uppercase tracking-wide text-ink-700/50">
              <th className="px-3 py-2 font-medium">#</th>
              <th className="px-3 py-2 font-medium">Raíz</th>
              <th className="px-3 py-2 font-medium">Significado</th>
              <th className="px-3 py-2 font-medium">Grupo</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((d) => (
              <tr
                key={d.id}
                className="border-b border-parchment-100 last:border-0 hover:bg-parchment-50"
              >
                <td className="px-3 py-2 font-mono text-xs text-ink-700/40">
                  {d.entry_number ?? d.order_index}
                </td>
                <td className="px-3 py-2 font-serif font-medium text-ink-800">
                  {d.root}
                </td>
                <td className="px-3 py-2 text-ink-700/80">
                  {d.meaning || d.detail || "—"}
                </td>
                <td className="px-3 py-2 text-xs text-ink-700/50">
                  {d.group_label || "—"}
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
              href={`/annexes/dhatus?${new URLSearchParams({
                ...(gana != null ? { gana: String(gana) } : {}),
                page: String(page - 1),
              })}`}
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
              href={`/annexes/dhatus?${new URLSearchParams({
                ...(gana != null ? { gana: String(gana) } : {}),
                page: String(page + 1),
              })}`}
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
