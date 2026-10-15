import clsx, { ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

/** Convierte refs como "1.1.3-6,73" en lista de ids navegables cuando es id simple */
export function isSimpleSutraId(ref: string): boolean {
  return /^\d{1,2}\.\d{1,2}\.\d{1,3}$/.test(ref.trim());
}

export const ADHYAYA_LABELS: Record<number, string> = {
  1: "I — Saṃjñā y reglas generales",
  2: "II — Samāsa y kāraka",
  3: "III — Kṛt y taddhita",
  4: "IV — Taddhita (continuación)",
  5: "V — Taddhita y kṛt",
  6: "VI — Saṃdhi y acentuación",
  7: "VII — Añges y conjugación",
  8: "VIII — Saṃdhi final y miscelánea",
};
