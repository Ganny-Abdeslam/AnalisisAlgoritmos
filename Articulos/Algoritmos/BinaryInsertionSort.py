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

    # Llamada al algoritmo Binary Insertion Sort
    binary_insertion_sort(dic, campo)

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

# Implementación de Binary Insertion Sort
def binary_insertion_sort(dic, campo):
    keys = list(dic.keys())
    
    for i in range(1, len(keys)):
        current_key = keys[i]
        current_value = dic[current_key].get(campo)

        if current_value is None:
            continue
        
        low, high = 0, i - 1

        # Encuentra la posición de inserción utilizando búsqueda binaria
        while low <= high:
            mid = (low + high) // 2
            mid_value = dic[keys[mid]].get(campo)

            if mid_value is None:
                mid_value = float('-inf')

            if isinstance(current_value, int) and isinstance(mid_value, int):
                if current_value < mid_value:
                    high = mid - 1
                else:
                    low = mid + 1
            elif isinstance(current_value, str) and isinstance(mid_value, str):
                if current_value < mid_value:
                    high = mid - 1
                else:
                    low = mid + 1
            else:
                break

        # Desplazar los elementos hacia la derecha para hacer espacio para el nuevo elemento
        for j in range(i, low, -1):
            keys[j] = keys[j - 1]

        # Insertar el valor en la posición correcta
        keys[low] = current_key

    # Reorganizar el diccionario de acuerdo a las claves ordenadas
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
    algoritmo = "./Datos/BinaryInsertionSort_Year.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar por años:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'title'
    algoritmo = "./Datos/BinaryInsertionSort_Title.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar por títulos:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'journal'
    algoritmo = "./Datos/BinaryInsertionSort_Journal.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar por revista:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'BDOrigen'
    algoritmo = "./Datos/BinaryInsertionSort_BDOrigen.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar por Base de Datos de Origen:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)
