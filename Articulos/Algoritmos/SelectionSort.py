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

    selection_sort(dic, campo)

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

def selection_sort(dic, campo):
    keys = list(dic.keys())
    n = len(keys)

    for i in range(n):
        min_index = i
        for j in range(i + 1, n):
            val_i = dic[keys[min_index]].get(campo)
            val_j = dic[keys[j]].get(campo)
            
            if val_i is None:
                min_index = j
            elif val_j is None:
                continue
            elif isinstance(val_i, int) and isinstance(val_j, int):
                if val_j < val_i:
                    min_index = j
            elif isinstance(val_i, str) and isinstance(val_j, str):
                if val_j < val_i:
                    min_index = j

        keys[i], keys[min_index] = keys[min_index], keys[i]

    dic_sorted = {key: dic[key] for key in keys}
    dic.clear()
    dic.update(dic_sorted)

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
    algoritmo = "./Datos/SelectionSort_Year.bib"
    origen = './../unificados.bib'

    print("Ejecución para los años:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'title'
    algoritmo = "./Datos/SelectionSort_Title.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los titulos:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'journal'
    algoritmo = "./Datos/SelectionSort_Journal.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por revista:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    # campo = 'cantidad autores'
    # algoritmo = "./Datos/SelectionSort_CantAutores.bib"
    # origen = './../unificados.bib'

    # print("Ejecución para ordenar los articulos por cantidad de autores:")
    # medir_tiempo_y_memoria(unificar_archivos_bib_auth, algoritmo, origen, campo)

    campo = 'BDOrigen'
    algoritmo = "./Datos/SelectionSort_BDOrigen.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por Base de datos origen:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)
