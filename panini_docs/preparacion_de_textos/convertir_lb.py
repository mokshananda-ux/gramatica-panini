import re
import pandas as pd
from docx import Document


def convertir_bases_nominales_a_xlsx(ruta_docx, ruta_xlsx):
    doc = Document(ruta_docx)

    datos = []
    grupo_actual = ""
    sutra_actual = ""

    # Expresión regular para capturar la regla/sutra entre corchetes
    patron_sutra = re.compile(r'^\s*\[(.*?)\]\s*$')

    for p in doc.paragraphs:
        texto = re.sub(r'\s+', ' ', p.text).strip()
        if not texto:
            continue

        # Caso 1: Es la regla/sutra entre corchetes
        match_sutra = patron_sutra.match(texto)
        if match_sutra:
            sutra_actual = match_sutra.group(0)  # Guarda la cadena completa con corchetes
            continue

        # Caso 2: Es el título del grupo (suele comenzar por número o nombre de grupo)
        # Si la línea no tiene corchetes ni empieza con listado de ítems (ej. "1 aṁśu-")
        if not re.match(r'^\d+\s+[a-zA-Zāīūṛṝḷēōṁḥñṅṇśṣ\-\–\—]', texto) and not texto.startswith('['):
            # Limpiamos prefijo de numeración de grupo si existe (ej. "1. aṁśu..." -> "aṁśu...")
            grupo_actual = re.sub(r'^\d+\.\s*', '', texto).strip()
            sutra_actual = ""  # Resetea la regla para el nuevo grupo
            continue

        # Caso 3: Es la lista de bases nominales
        # Separamos la lista por comas o puntos y comas cuando antecedan a un número de ítem
        elementos = re.split(r'[,;]\s*(?=\d+\s)', texto)
        for elem in elementos:
            elem = elem.strip()
            if elem:
                if elem.endswith('.'):
                    elem = elem[:-1].strip()

                datos.append({
                    "Grupo": grupo_actual,
                    "Sutra / Referencia": sutra_actual,
                    "Base Nominal / Detalle": elem
                })

    # Crear el DataFrame de Pandas
    df = pd.DataFrame(datos)

    # Exportar a Excel con openpyxl
    with pd.ExcelWriter(ruta_xlsx, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Bases Nominales')

    print(f"¡Conversión exitosa! Se procesaron {len(df)} registros.")
    print(f"Archivo guardado en: {ruta_xlsx}")


if __name__ == '__main__':
    archivo_entrada = "/home/anselmo/PycharmProjects/panini-grammar/panini_docs/anexos/lista_bases_nominales.docx"
    archivo_salida = "/home/anselmo/PycharmProjects/panini-grammar/panini_docs/anexos/lista_bases_nominales.xlsx"

    convertir_bases_nominales_a_xlsx(archivo_entrada, archivo_salida)