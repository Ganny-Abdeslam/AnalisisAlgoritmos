from pathlib import Path
import re

count = 0

def unificar_archivos_bib(archivo_unificado, origenes):
    with open(archivo_unificado, "w", encoding="utf-8") as salida:
        for origen in origenes:
            archivos = obtener_archivos_bib(origen)
            for archivo in archivos:
                procesar_archivo(archivo, salida)

def obtener_archivos_bib(origen):
    directory = Path(origen)
    archivos = directory.glob("*.bib")
    return archivos

def procesar_archivo(archivo, salida):
    with open(archivo, 'r', encoding="utf-8") as a:
        contenido = a.read()
        lineas = contenido.split('\n')
        extraer_campos(lineas, salida)

def extraer_campos(lineas, salida):
    global count
    desired_fields = ('author', 'title', 'doi', 'year', 'abstract', 'journal')

    for linea in lineas:
        try:
            key, value = linea.split("=", 1)
            key = key.strip()
            if key in desired_fields:
                procesar_campo(key, value, salida)
            elif '@' in linea:
                count += 1
                salida.write("------------------------------------\n")
        except:
            if linea and linea[0] == '@':
                count += 1
                salida.write("------------------------------------\n")
            else:
                pass

def procesar_campo(key, value, salida):
    if key == "author":
        autores = formatear_autores(value)
        salida.write(f"{key}: {autores}\n")

    elif key == "year":
        temp = re.sub(r'[a-zA-Z]', '', value).strip().replace("{", "").replace("},", "")
        salida.write(f"{key}: {temp}\n")

    else:
        temp = value.strip().replace("{", "").replace("},", "").replace("}", "")
        salida.write(f"{key}: {temp}\n")

def formatear_autores(value):
    temp = value.strip().replace(" and ", ',').split(',')
    autores = ", ".join([autor.strip() for autor in temp]).replace("{", "").replace("},", "")
    return autores

if __name__ == "__main__":
    archivo_unificado = "unificados.bib"
    origenes = ['./IEEE/', './Sage/', './ScienceDirect/', './Scopus/']
    
    unificar_archivos_bib(archivo_unificado, origenes)

    print(f"Total de artículos procesados: {count}")