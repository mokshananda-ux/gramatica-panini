import os
from docx import Document
from docxcompose.composer import Composer


def fusionar_documentos(directorio_entrada, archivo_salida, lista_archivos=None):
    """
    Fusiona múltiples archivos .docx en uno solo de forma ordenada y preservando estilos.
    """
    # Si no se pasa una lista específica, toma todos los .docx del directorio ordenados alfabéticamente
    if not lista_archivos:
        lista_archivos = sorted([
            f for f in os.listdir(directorio_entrada) if f.endswith(".docx")
        ])

    if not lista_archivos:
        print("No se encontraron archivos .docx para fusionar.")
        return

    print(f"Iniciando fusión de {len(lista_archivos)} documentos...")

    # 1. Tomamos el primer archivo como el documento maestro
    primer_archivo = os.path.join(directorio_entrada, lista_archivos[0])
    master = Document(primer_archivo)
    composer = Composer(master)

    # 2. Iteramos sobre el resto de los documentos en orden
    for archivo in lista_archivos[1:]:
        ruta_archivo = os.path.join(directorio_entrada, archivo)
        print(f"Agregando: {archivo}")

        sub_doc = Document(ruta_archivo)

        # Opcional: Inserta un salto de página para separar visualmente cada documento/capítulo
        master.add_page_break()

        # Fusionamos el contenido preservando los estilos
        composer.append(sub_doc)

    # 3. Guardamos el resultado final
    composer.save(archivo_salida)
    print(f"¡Fusión completada con éxito! Archivo guardado como: {archivo_salida}")

# ==========================================
# AQUÍ CONFIGURAS TU DIRECTORIO Y SALIDA:
# ==========================================
directorio = "/home/anselmo/PycharmProjects/panini-grammar/panini_docs/gramatica"
salida = "/home/anselmo/PycharmProjects/panini-grammar/panini_docs/gramatica/gramatica_completa.docx"

# Ejecutamos la función
fusionar_documentos(directorio, salida)