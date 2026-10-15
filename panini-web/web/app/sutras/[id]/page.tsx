import Link from "next/link";
import { notFound } from "next/navigation";
import { RefLink } from "@/components/RefLink";
import { getSutra } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  return { title: `Sūtra ${id}` };
}

export default async function SutraDetailPage({ params }: Props) {
  const { id } = await params;
  let sutra;
  try {
    sutra = await getSutra(id);
  } catch (e) {
    if (e instanceof Error && e.message === "NOT_FOUND") notFound();
    return (
      <div className="rounded-lg border border-terracotta-500/30 bg-terracotta-500/5 p-6 text-center">
        <p>Error al cargar el sūtra {id}.</p>
      </div>
    );
  }

  const [a, p] = [sutra.adhyaya, sutra.pada];

  return (
    <article className="space-y-8">
      {/* Breadcrumb */}
      <nav className="flex flex-wrap items-center gap-1.5 text-sm text-ink-700/50">
        <Link href="/sutras" className="hover:text-ink-800">
          Sūtras
        </Link>
        <span>/</span>
        <Link href={`/sutras?adhyaya=${a}`} className="hover:text-ink-800">
          {a}
        </Link>
        <span>/</span>
        <Link
          href={`/sutras?adhyaya=${a}&pada=${p}`}
          className="hover:text-ink-800"
        >
          {a}.{p}
        </Link>
        <span>/</span>
        <span className="font-mono text-ink-800">{sutra.id}</span>
      </nav>

      {/* Cabecera del sūtra */}
      <header className="space-y-3 border-b border-parchment-200 pb-6">
        <div className="flex flex-wrap items-baseline gap-3">
          <h1 className="font-mono text-xl font-bold text-saffron-600">
            {sutra.id}
          </h1>
          <p className="sanskrit font-serif text-2xl leading-snug text-ink-800">
            {sutra.sanskrit}
          </p>
        </div>
        <p className="text-lg leading-relaxed text-ink-700">
          {sutra.translation}
        </p>
      </header>

      {/* Notas */}
      {sutra.notes.length > 0 && (
        <section className="space-y-4">
          <h2 className="text-sm font-medium uppercase tracking-wide text-ink-700/50">
            Notas y comentarios
          </h2>
          <ol className="space-y-4">
            {sutra.notes.map((n) => (
              <li
                key={n.id}
                className="rounded-lg border border-parchment-200 bg-white px-4 py-3"
              >
                <div className="flex gap-2">
                  {n.note_number != null && (
                    <span className="mt-0.5 shrink-0 font-mono text-xs font-semibold text-saffron-600">
                      {n.note_number}.
                    </span>
                  )}
                  <div className="note-body whitespace-pre-wrap">{n.content}</div>
                </div>
                {n.note_type && (
                  <span className="mt-2 inline-block rounded bg-parchment-100 px-1.5 py-0.5 text-[10px] uppercase tracking-wider text-ink-700/40">
                    {n.note_type}
                  </span>
                )}
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* Referencias cruzadas */}
      {sutra.cross_references.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-sm font-medium uppercase tracking-wide text-ink-700/50">
            Referencias
          </h2>
          <ul className="flex flex-wrap gap-2">
            {sutra.cross_references.map((x) => (
              <li
                key={x.id}
                className="rounded-md border border-parchment-200 bg-parchment-50 px-2.5 py-1 text-sm"
                title={x.reference_text || undefined}
              >
                <RefLink ref={x.to_sutra_ref} />
                {x.ref_type && (
                  <span className="ml-1.5 text-xs text-ink-700/40">
                    {x.ref_type}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Navegación previa/siguiente aproximada por order_index no disponible aquí;
          enlaces de vuelta al pada */}
      <div className="flex justify-between border-t border-parchment-200 pt-6 text-sm">
        <Link
          href={`/sutras?adhyaya=${a}&pada=${p}`}
          className="text-ink-700/60 hover:text-ink-800"
        >
          ← Volver al pada {a}.{p}
        </Link>
      </div>
    </article>
  );
}
