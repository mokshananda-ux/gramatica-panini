import Link from "next/link";
import { AdhyayaNav } from "@/components/AdhyayaNav";
import { ADHYAYA_LABELS } from "@/lib/utils";

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="space-y-4">
        <h1 className="font-serif text-3xl font-semibold tracking-tight text-ink-800 sm:text-4xl">
          Aṣṭādhyāyī de Pāṇini
        </h1>
        <p className="max-w-2xl text-lg leading-relaxed text-ink-700/80">
          Basado en la primera traducción completa al español de Anselmo Hernández Quiroz (2021-Repositorio CRIM-UNAM). <br />
          Navega los sūtras por adhyāya y pada, consulta notas y referencias cruzadas, y explora los anexos
          (pratyāhāras, dhātu-pāṭha y bases nominales).
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-sm font-medium uppercase tracking-wide text-ink-700/50">
          Ir a un adhyāya
        </h2>
        <AdhyayaNav />
      </section>

      <section className="grid gap-3 sm:grid-cols-2">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((a) => (
          <Link
            key={a}
            href={`/sutras?adhyaya=${a}`}
            className="rounded-lg border border-parchment-200 bg-white px-4 py-3 transition hover:border-saffron-400/40 hover:shadow-sm"
          >
            <span className="font-mono text-sm text-saffron-600">
              Adhyāya {a}
            </span>
            <p className="mt-0.5 text-sm text-ink-700/70">
              {ADHYAYA_LABELS[a]}
            </p>
          </Link>
        ))}
      </section>

      <section className="grid gap-3 sm:grid-cols-3">
        <Link
          href="/annexes/pratyaharas"
          className="rounded-lg border border-parchment-200 bg-parchment-100/50 px-4 py-3 text-sm hover:border-saffron-400/40"
        >
          <span className="font-medium text-ink-800">Pratyāhāras</span>
          <p className="mt-0.5 text-ink-700/60">Siglas y Śiva-sūtras</p>
        </Link>
        <Link
          href="/annexes/dhatus"
          className="rounded-lg border border-parchment-200 bg-parchment-100/50 px-4 py-3 text-sm hover:border-saffron-400/40"
        >
          <span className="font-medium text-ink-800">Dhātu-pāṭha</span>
          <p className="mt-0.5 text-ink-700/60">Lista de primitivos</p>
        </Link>
        <Link
          href="/annexes/nominal-bases"
          className="rounded-lg border border-parchment-200 bg-parchment-100/50 px-4 py-3 text-sm hover:border-saffron-400/40"
        >
          <span className="font-medium text-ink-800">Bases nominales</span>
          <p className="mt-0.5 text-ink-700/60">Listas por grupo</p>
        </Link>
      </section>
    </div>
  );
}
