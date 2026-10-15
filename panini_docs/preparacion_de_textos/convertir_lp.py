import re
import pandas as pd
from docx import Document


def convertir_docx_a_xlsx(ruta_docx, ruta_xlsx):
    doc = Document(ruta_docx)

    datos = []
    grupo_actual = ""
    seccion_actual = ""
    subseccion_actual = ""
    nivel_4_actual = ""

    # Patrones mejorados y flexibles
    patron_grupo = re.compile(r'^(X|IX|VIII|VII|VI|V|IV|III|II|I)\.\s+[a-zA-Zāīūṛṝḷēōṁḥñṅṇṇśṣ\-\–\—].*')
    patron_seccion = re.compile(r'^(X|IX|VIII|VII|VI|V|IV|III|II|I)\.\s*[A-Z]\.\s+.*')

    # CORREGIDO: Permite capturar de forma flexible subsecciones de 1 o 2 dígitos (ej: I.A.5, I.A.12)
    patron_subseccion = re.compile(r'^(X|IX|VIII|VII|VI|V|IV|III|II|I)\.\s*[A-Z]\.\s*\d{1,2}\.\s+.*')

    # Nivel 4: ej. I.A.21.a
    patron_nivel4 = re.compile(r'^(X|IX|VIII|VII|VI|V|IV|III|II|I)\.\s*[A-Z]\.\s*\d{1,2}\.\s*[a-z]\.?\s+.*')

    for p in doc.paragraphs:
        texto = re.sub(r'\s+', ' ', p.text).strip()
        if not texto:
            continue

        if patron_nivel4.match(texto):
            nivel_4_actual = texto
        elif patron_subseccion.match(texto):
            subseccion_actual = texto
            nivel_4_actual = ""  # Resetea el nivel inferior si cambia la subsección
        elif patron_seccion.match(texto):
            seccion_actual = texto
            subseccion_actual = ""
            nivel_4_actual = ""
        elif patron_grupo.match(texto):
            grupo_actual = texto
            seccion_actual = ""
            subseccion_actual = ""
            nivel_4_actual = ""
        else:
            # Si el texto de la línea coincide por accidente con un encabezado que no atrapó el if, lo filtramos o lo tratamos como primitivo
            if patron_subseccion.match(texto) or patron_seccion.match(texto):
                continue

            # Es un bloque de primitivos, los separamos por punto y coma seguido de número
            primitivos = re.split(r';\s*(?=\(?\d+)', texto)
            for prim in primitivos:
                prim = prim.strip()
                if prim:
                    if prim.endswith(';'):
                        prim = prim[:-1].strip()

                    datos.append({
                        "Grupo": grupo_actual,
                        "Sección Mayor": seccion_actual,
                        "Subsección": subseccion_actual,
                        "Nivel 4": nivel_4_actual,
                        "Primitivo / Detalle": prim
                    })

    # Crear DataFrame con Pandas
    df = pd.DataFrame(datos)

    # Exportar a Excel
    with pd.ExcelWriter(ruta_xlsx, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Primitivos Sánscritos')

    print(f"¡Conversión perfecta y exitosa! Archivo guardado en: {ruta_xlsx}")


if __name__ == '__main__':
    archivo_entrada = "/home/anselmo/PycharmProjects/panini-grammar/panini_docs/anexos/lista_primitivos.docx"
    archivo_salida = "/home/anselmo/PycharmProjects/panini-grammar/panini_docs/anexos/lista_primitivos.xlsx"

    convertir_docx_a_xlsx(archivo_entrada, archivo_salida)