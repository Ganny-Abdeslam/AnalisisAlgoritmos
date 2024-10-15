import time
import tracemalloc

dic = {}

def unificar_archivos_bib(algoritmo, origen, campo):
    with open(algoritmo, "w", encoding="utf-8") as salida:       
        procesar_archivo(origen, salida, campo)

def procesar_archivo(archivo, salida, campo):
    global dic
    dic.clear()

    with open(archivo, 'r', encoding="utf-8") as a:
        contenido = a.read()
        lineas = contenido.split('\n')

        contador = -1
        lista = {}

        for linea in lineas:
            try:
                key, value = linea.split(":", 1)
                key = key.strip()

                if key == "year":
                    lista[key] = int(value.strip())
                else:
                    lista[key] = value.strip()
            except ValueError:
                contador += 1
                lista = {}
                dic[contador] = lista

        dic[contador] = lista

    # Llamada al algoritmo Gnome Sort
    gnome_sort(dic, campo)

    # Escribir en el archivo de salida con el diccionario ya ordenado
    for key in dic:
        try:
            if not dic[key].get(campo):
                continue

            salida.write("------------------------------------\n")
            salida.write(f"BDOrigen: {dic[key].get('BDOrigen', 'No BDOrigen')}\n")
            salida.write(f"author: {dic[key].get('author', 'No author')}\n")
            salida.write(f"title: {dic[key].get('title', 'No title')}\n")
            salida.write(f"year: {dic[key]['year']}\n")
            salida.write(f"journal: {dic[key].get('journal', 'No journal')}\n")
            salida.write(f"doi: {dic[key].get('doi', 'No doi')}\n")
            salida.write(f"abstract: {dic[key].get('abstract', 'No abstract')}\n")
        except:
            pass

# Implementación de Gnome Sort

def gnome_sort(dic, campo):
    keys = list(dic.keys())
    i = 1
    while i < len(keys):
        val_i = dic[keys[i]].get(campo)
        if i > 0 and (val_i is None or should_swap(dic, campo, keys[i-1], keys[i])):
            # Intercambiar
            swap(dic, keys[i-1], keys[i])
            i -= 1
        else:
            i += 1

# Función para verificar si se debe hacer el intercambio
def should_swap(dic, campo, i, j):
    val_i = dic[i].get(campo)
    val_j = dic[j].get(campo)

    if val_i is None or val_j is None:
        return False

    if isinstance(val_i, int) and isinstance(val_j, int):
        return val_i > val_j
    elif isinstance(val_i, str) and isinstance(val_j, str):
        return val_i > val_j

    return False

# Función de intercambio de elementos en el diccionario
def swap(dic, i, j):
    dic[i], dic[j] = dic[j], dic[i]

def medir_tiempo_y_memoria(func, *args):
    tracemalloc.start()
    start_time = time.time()

    func(*args)

    end_time = time.time()
    memory_usage, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Tiempo de ejecución: {end_time - start_time:.4f} segundos")
    print(f"Memoria usada: {memory_usage / 1024:.4f} KB\n")


if __name__ == "__main__":
    campo = 'year'
    algoritmo = "./Datos/GnomeSort_Year.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar por años:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'title'
    algoritmo = "./Datos/GnomeSort_Title.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar por títulos:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'journal'
    algoritmo = "./Datos/GnomeSort_Journal.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar por revista:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'BDOrigen'
    algoritmo = "./Datos/GnomeSort_BDOrigen.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar por Base de Datos de Origen:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)
