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

    bitonic_sort(dic, campo)

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

def bitonic_sort(dic, campo):
    keys = list(dic.keys())
    n = len(keys)

    # Llamada inicial para construir la secuencia bitónica
    bitonic_sort_recursive(dic, campo, 0, n, True)

    # Actualizamos el diccionario con el orden obtenido
    dic_sorted = {key: dic[key] for key in keys} 
    dic.clear()
    dic.update(dic_sorted)

# Función recursiva para el Bitonic Sort
def bitonic_sort_recursive(dic, campo, low, cnt, ascending):
    if cnt > 1:
        k = cnt // 2

        # Ordenar en forma ascendente la primera mitad
        bitonic_sort_recursive(dic, campo, low, k, True)

        # Ordenar en forma descendente la segunda mitad
        bitonic_sort_recursive(dic, campo, low + k, cnt - k, False)

        # Unir ambas mitades
        bitonic_merge(dic, campo, low, cnt, ascending)

# Función para mezclar dos secuencias bitónicas
def bitonic_merge(dic, campo, low, cnt, ascending):
    if cnt > 1:
        k = cnt // 2
        for i in range(low, low + k):
            if should_swap(dic, campo, i, i + k, ascending):
                swap(dic, i, i + k)

        # Mezclar las dos mitades
        bitonic_merge(dic, campo, low, k, ascending)
        bitonic_merge(dic, campo, low + k, cnt - k, ascending)

# Función para verificar si se debe hacer el intercambio
def should_swap(dic, campo, i, j, ascending):
    val_i = dic[i].get(campo)
    val_j = dic[j].get(campo)

    if val_i is None or val_j is None:
        return False

    if ascending:
        if isinstance(val_i, int) and isinstance(val_j, int):
            return val_i > val_j
        elif isinstance(val_i, str) and isinstance(val_j, str):
            return val_i > val_j
    else:
        if isinstance(val_i, int) and isinstance(val_j, int):
            return val_i < val_j
        elif isinstance(val_i, str) and isinstance(val_j, str):
            return val_i < val_j

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
    algoritmo = "./Datos/BitonicSort_Year.bib"
    origen = './../unificados.bib'

    print("Ejecución para los años:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'title'
    algoritmo = "./Datos/BitonicSort_Title.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los titulos:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'journal'
    algoritmo = "./Datos/BitonicSort_Journal.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por revista:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'BDOrigen'
    algoritmo = "./Datos/BitonicSort_BDOrigen.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por Base de datos origen:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)
