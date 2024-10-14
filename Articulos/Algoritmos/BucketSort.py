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

    bucket_sort(dic, campo)

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

def bucket_sort(dic, campo):
    buckets = {}

    min_value = float('inf')
    max_value = float('-inf')
    
    for key in dic:
        try:
            value = dic[key].get(campo)
            ascii_value = ord(value[0])
            if ascii_value < min_value:
                min_value = ascii_value
            if ascii_value > max_value:
                max_value = ascii_value
        except:
            value = dic[key].get(campo)
            if isinstance(value, int):
                if value < min_value:
                    min_value = value
                if value > max_value:
                    max_value = value

    min_value = int(min_value)
    max_value = int(max_value)

    bucket_count = max_value - min_value + 1
    bucket_count = int(bucket_count)
    for i in range(bucket_count):
        buckets[i] = []

    for key in dic:
        value = dic[key].get(campo)
        try:
            ascii_value = ord(value[0])
            if isinstance(value, str):
                bucket_index = ascii_value - min_value
                buckets[bucket_index].append(dic[key])
        except:
            if isinstance(value, str):
                bucket_index = value - min_value
                buckets[bucket_index].append(dic[key])

    sorted_dic = {}
    index = 0
    for i in range(bucket_count):
        sorted_bucket = sorted(buckets[i], key=lambda x: x.get(campo, 0))
        for item in sorted_bucket:
            sorted_dic[index] = item
            index += 1

    dic.clear()
    dic.update(sorted_dic)

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
    algoritmo = "./Datos/BucketSort_Year.bib"
    origen = './../unificados.bib'

    print("Ejecución para los años:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'title'
    algoritmo = "./Datos/BucketSort_Title.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los títulos:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'journal'
    algoritmo = "./Datos/BucketSort_Journal.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por revista:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'BDOrigen'
    algoritmo = "./Datos/BucketSort_BDOrigen.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por Base de datos origen:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)
