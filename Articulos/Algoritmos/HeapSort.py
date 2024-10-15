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

    heap_sort(dic, campo)

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

def heapify(dic, campo, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    keys = list(dic.keys())

    val_root = dic[keys[largest]].get(campo)
    val_left = dic[keys[left]].get(campo) if left < n else None
    val_right = dic[keys[right]].get(campo) if right < n else None

    if val_left is not None:
        if isinstance(val_root, int) and isinstance(val_left, int):
            if val_left > val_root:
                largest = left
        elif isinstance(val_root, str) and isinstance(val_left, str):
            if val_left > val_root:
                largest = left

    if val_right is not None:
        if isinstance(val_root, int) and isinstance(val_right, int):
            if val_right > val_root:
                largest = right
        elif isinstance(val_root, str) and isinstance(val_right, str):
            if val_right > val_root:
                largest = right

    if largest != i:
        keys[i], keys[largest] = keys[largest], keys[i]
        dic_sorted = {key: dic[key] for key in keys} 
        dic.clear()
        dic.update(dic_sorted)

        heapify(dic, campo, n, largest)

def heap_sort(dic, campo):
    keys = list(dic.keys())
    n = len(keys)

    for i in range(n // 2 - 1, -1, -1):
        heapify(dic, campo, n, i)

    for i in range(n - 1, 0, -1):
        keys[i], keys[0] = keys[0], keys[i]
        dic_sorted = {key: dic[key] for key in keys} 
        dic.clear()
        dic.update(dic_sorted)

        heapify(dic, campo, i, 0)


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
    algoritmo = "./Datos/HeapSort_Year.bib"
    origen = './../unificados.bib'

    print("Ejecución para los años:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'title'
    algoritmo = "./Datos/HeapSort_Title.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los titulos:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'journal'
    algoritmo = "./Datos/HeapSort_Journal.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por revista:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'BDOrigen'
    algoritmo = "./Datos/HeapSort_BDOrigen.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por Base de datos origen:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)
