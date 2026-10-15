import pandas as pd
from docx import Document


def convertir_tabla_pratyahara_a_xlsx(ruta_docx, ruta_xlsx):
    doc = Document(ruta_docx)

    datos = []

    # Recorremos todas las tablas presentes en el archivo docx
    for table in doc.tables:
        # Extraer filas
        for row in table.rows:
            celdas = [celda.text.strip() for celda in row.cells]

            # Verificamos que sea una fila válida de datos o encabezado
            if len(celdas) >= 3:
                # Si las celdas incluyen el número o la estructura esperada
                datos.append(celdas)

    # Si la tabla en el Word tiene 3 o 4 columnas, ajustamos el DataFrame:
    # Caso común: Fila con [Número, Sūtra, Definición, Siglas]
    if datos:
        # Si la primera fila es encabezado
        df = pd.DataFrame(datos)

        # Guardar en Excel con formato limpio
        with pd.ExcelWriter(ruta_xlsx, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False, sheet_name='Pratyāhāra-sūtra')

        print(f"¡Conversión exitosa! Archivo Excel guardado en: {ruta_xlsx}")
    else:
        print("No se encontraron tablas estructuradas en el archivo .docx.")


if __name__ == '__main__':
    archivo_entrada = "/home/anselmo/PycharmProjects/panini-grammar/panini_docs/anexos/pratyahara_sutra.docx"
    archivo_salida = "/home/anselmo/PycharmProjects/panini-grammar/panini_docs/anexos/pratyahara_sutra.xlsx"

    convertir_tabla_pratyahara_a_xlsx(archivo_entrada, archivo_salida)