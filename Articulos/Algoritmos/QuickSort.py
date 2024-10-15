import time
import tracemalloc
import sys

sys.setrecursionlimit(2000)

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

    quicksort(dic, campo, 0, len(dic) - 1)

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

def median_of_three(dic, campo, low, high):
    mid = (low + high) // 2

    low_value = dic[low].get(campo, float('-inf'))
    mid_value = dic[mid].get(campo, float('-inf'))
    high_value = dic[high].get(campo, float('-inf'))

    pivot_candidates = [low_value, mid_value, high_value]
    
    pivot_candidates.sort()

    return pivot_candidates[1]

def partition(dic, campo, low, high):
    pivot = median_of_three(dic, campo, low, high)
    i = low - 1

    for j in range(low, high):
        val_j = dic[j].get(campo)
        
        if isinstance(pivot, str) and isinstance(val_j, str):
            if val_j < pivot:
                i += 1
                dic[i], dic[j] = dic[j], dic[i]
        elif isinstance(pivot, int) and isinstance(val_j, int):
            if val_j < pivot:
                i += 1
                dic[i], dic[j] = dic[j], dic[i]

    dic[i + 1], dic[high] = dic[high], dic[i + 1]
    return i + 1

def quicksort(dic, campo, low, high):
    if low < high:
        pi = partition(dic, campo, low, high)

        quicksort(dic, campo, low, pi - 1)
        quicksort(dic, campo, pi + 1, high)

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
    algoritmo = "./Datos/QuickSort_Year.bib"
    origen = './../unificados.bib'

    print("Ejecución para los años:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    try:
        campo = 'title'
        algoritmo = "./Datos/QuickSort_Title.bib"
        origen = './../unificados.bib'

        print("Ejecución para ordenar los títulos:")
        medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)
    except:
        print("Llega a la máxima recursión posible")

    # campo = 'journal'
    # algoritmo = "./Datos/QuickSort_Journal.bib"
    # origen = './../unificados.bib'

    # print("Ejecución para ordenar los artículos por revista:")
    # medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    # campo = 'BDOrigen'
    # algoritmo = "./Datos/QuickSort_BDOrigen.bib"
    # origen = './../unificados.bib'

    # print("Ejecución para ordenar los artículos por Base de datos origen:")
    # medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)
