import Link from "next/link";

export default function NotFound() {
  return (
    <div className="py-16 text-center">
      <h1 className="font-serif text-2xl font-semibold text-ink-800">
        No encontrado
      </h1>
      <p className="mt-2 text-ink-700/60">
        Ese sūtra o página no existe en la base de datos.
      </p>
      <Link
        href="/"
        className="mt-6 inline-block rounded-md bg-ink-800 px-4 py-2 text-sm text-parchment-50 hover:bg-ink-700"
      >
        Volver al inicio
      </Link>
    </div>
  );
}
