import Link from "next/link";
import { isSimpleSutraId } from "@/lib/utils";

/** Enlace a un sūtra si la ref es un id simple; si no, texto plano. */
export function RefLink({
  ref,
  className,
}: {
  ref: string;
  className?: string;
}) {
  const clean = ref.trim();
  if (isSimpleSutraId(clean)) {
    return (
      <Link
        href={`/sutras/${clean}`}
        className={
          className ??
          "font-mono text-saffron-600 underline-offset-2 hover:underline"
        }
      >
        {clean}
      </Link>
    );
  }
  return <span className={className ?? "font-mono text-ink-700"}>{clean}</span>;
}
