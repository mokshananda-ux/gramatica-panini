import pandas as pd

# Listado completo estructurado
datos = [
    {"Número": 1, "Sigla": "aK", "Definición / Referencia": "Las vocales simples a, i, u, y las retroflejas ṛ, ḷ (con características supra-segmentales de 3 medidas prosódicas, 3 acentos y presencia o ausencia (±) de nasalidad); Cf. 6.1.101, 128."},
    {"Número": 2, "Sigla": "aC", "Definición / Referencia": "Todas las vocales: a, i, u, ṛ, ḷ, e, o, ai, au (con características supra-segmentales de 3 medidas prosódicas, 3 acentos y presencia o ausencia (±) de nasalidad); Cf. 1.1.10, 47, 73; 2.2.7; 3.2 etc."},
    {"Número": 3, "Sigla": "aṬ", "Definición / Referencia": "Todas las vocales + la fricativa sonora h + las semivocales excepto l; Cf. 8.3.3, 9; 4.6.3."},
    {"Número": 4, "Sigla": "aṆ1", "Definición / Referencia": "Las vocales simples a, i, u; Cf. 1.1.51; 6.3.111."},
    {"Número": 5, "Sigla": "aṆ2", "Definición / Referencia": "Todas las vocales (aC) + la fricativa sonora h + todas las semivocales; Cf. 1.1.69."},
    {"Número": 6, "Sigla": "aM", "Definición / Referencia": "Las vocales + h + las semivocales + las consonantes nasales; Cf. 8.3.6."},
    {"Número": 7, "Sigla": "aL", "Definición / Referencia": "Las vocales (aC) + las consonantes (haL). Aquí las semivocales cuentan como consonantes."},
    {"Número": 8, "Sigla": "aŚ", "Definición / Referencia": "Todos los fonemas sonoros (aC + haŚ); 8.3.17."},
    {"Número": 9, "Sigla": "iK", "Definición / Referencia": "Las vocales simples i, u, ṛ, ḷ; 1.1.3, 45, 48; 2.9."},
    {"Número": 10, "Sigla": "iC", "Definición / Referencia": "Todas las vocales excepto a; 6.1.104; 3.68."},
    {"Número": 11, "Sigla": "iṆ2", "Definición / Referencia": "Todas las vocales (excepto a) + h + las semivocales."},
    {"Número": 12, "Sigla": "uK", "Definición / Referencia": "Las vocales simples u, ṛ, ḷ; 8.1.70; 2.11; 3.57."},
    {"Número": 13, "Sigla": "eṄ", "Definición / Referencia": "Los diptongos e, o; 1.1.2, 75; 6.1.69, 94, 109 y siguientes."},
    {"Número": 14, "Sigla": "eC", "Definición / Referencia": "Todos los diptongos: e, o, ai, au; 1.1.48; 6.1.45 y siguientes."},
    {"Número": 15, "Sigla": "aiC", "Definición / Referencia": "Los diptongos ai, au; 1.1.1, 8; 7.8.8; 8.2.106."},
    {"Número": 16, "Sigla": "kha̱Y", "Definición / Referencia": "Todas las sordas oclusivas: kh, ph, ch, ṭh, th, k, p, c, ṭ, t; 7.4.61; 8.3.6."},
    {"Número": 17, "Sigla": "kha̱R", "Definición / Referencia": "Todas las consonantes sordas (incluyendo las sibilantes): (kha̱Y) + (śaR = ś, ṣ, s)."},
    {"Número": 18, "Sigla": "ṅaM", "Definición / Referencia": "Las consonantes nasales velar, retrofleja y dental; 8.3.32."},
    {"Número": 19, "Sigla": "ca̱R", "Definición / Referencia": "Las oclusivas sordas no aspiradas + las sibilantes; 1.1.58; 4.53 y sig.; 8.2.39."},
    {"Número": 20, "Sigla": "cha̱V", "Definición / Referencia": "Las oclusivas sordas palatal, retrofleja y dental: ch, ṭh, th, c, ṭ, t; 8.3.7."},
    {"Número": 21, "Sigla": "ja̱Ś", "Definición / Referencia": "Las oclusivas sonoras no aspiradas: j, b, g, ḍ, d; 1.1.58; 4.53 y sig.; 8.2.39."},
    {"Número": 22, "Sigla": "jha̱Y", "Definición / Referencia": "Todas las consonantes oclusivas que no son nasales: jh, bh, gh, ḍh, dh, j, b, g ḍ, d, kh, ph, ch, ṭh, th, c, ṭ, t, k, p; 5.4.111; 4.62 y sig.; 8.2.10."},
    {"Número": 23, "Sigla": "jha̱R", "Definición / Referencia": "Todas las consonantes oclusivas que no son nasales + las sibilantes (jha̱Y + śa̱R)."},
    {"Número": 24, "Sigla": "jha̱L", "Definición / Referencia": "Todas las consonantes oclusivas que no son nasales + las fricativas (jha̱Y + śa̱L)."},
    {"Número": 25, "Sigla": "jha̱Ś", "Definición / Referencia": "Las oclusivas sonoras: jh, bh, gh, ḍh, dh, j, b, g ḍ, d; 8.4.53."},
    {"Número": 26, "Sigla": "jha̱Ṣ", "Definición / Referencia": "Las oclusivas sonoras aspiradas: jh, bh, gh, ḍh, dh; 8.2.37,40."},
    {"Número": 27, "Sigla": "ba̱Ś", "Definición / Referencia": "Las oclusivas sonoras no aspiradas que no son la palatal j; 8.2.37."},
    {"Número": 28, "Sigla": "bha̱Ś", "Definición / Referencia": "Las oclusivas sonoras aspiradas que no son la palatal jh; 8.2.37."},
    {"Número": 29, "Sigla": "ma̱Y", "Definición / Referencia": "Todas las consonantes oclusivas a excepción de la nasal palatal ñ; 8.3.33."},
    {"Número": 30, "Sigla": "ya̱Ñ", "Definición / Referencia": "Las semivocales + las consonantes oclusivas nasales + jh, bh; 7.3.101 y sig."},
    {"Número": 31, "Sigla": "ya̱Ṇ", "Definición / Referencia": "Todas las semivocales: y, v, r, l; 1.1.45; 4.81,156; 6.1.77."},
    {"Número": 32, "Sigla": "ya̱M", "Definición / Referencia": "Las semivocales + las consonantes oclusivas nasales; 8.4.64."},
    {"Número": 33, "Sigla": "ya̱Y", "Definición / Referencia": "Las semivocales + las oclusivas; 8.4.58 y sig."},
    {"Número": 34, "Sigla": "ya̱R", "Definición / Referencia": "Las semivocales + las oclusivas + las sibilantes; 8.4.45 y sig."},
    {"Número": 35, "Sigla": "(*rÃ)", "Definición / Referencia": "Las líquidas r, l; 1.1.57."},
    {"Número": 36, "Sigla": "ra̱L", "Definición / Referencia": "Todas las consonantes que no son las semivocales y, v; 1.2.26."},
    {"Número": 37, "Sigla": "va̱L", "Definición / Referencia": "Todas las consonantes que no son la semivocal y; 6.1.66; 7.2.35."},
    {"Número": 38, "Sigla": "va̱Ś", "Definición / Referencia": "Las semivocales que no son y + las oclusivas sonoras; 7.2.8."},
    {"Número": 39, "Sigla": "śa̱R", "Definición / Referencia": "Las sibilantes ś, ṣ, s; 3.58; 4.49; 7.4.4; 8.3.28,35 y sig."},
    {"Número": 40, "Sigla": "śa̱L", "Definición / Referencia": "Todas las fricativas; 3.1.45."},
    {"Número": 41, "Sigla": "ha̱L", "Definición / Referencia": "Todas las consonantes; 1.1.7,10;3.1.12,83; 3.3."},
    {"Número": 42, "Sigla": "ha̱Ś", "Definición / Referencia": "Todas las consonantes sonoras; 6.1.64."}
]

df = pd.DataFrame(datos)

archivo_salida = "/home/anselmo/PycharmProjects/panini-grammar/panini_docs/anexos/siglas_pratyahara.xlsx"

with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='Siglas Pratyāhāra')

print(f"¡Archivo generado con éxito en: {archivo_salida}")