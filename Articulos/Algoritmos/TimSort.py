import time
import tracemalloc

dic = {}

def unificar_archivos_bib(algoritmo, origen, campo):
    with open(algoritmo, "w", encoding="utf-8") as salida:       
        procesar_archivo(origen, salida, campo)

def unificar_archivos_bib_auth(algoritmo, origen, campo):
    with open(algoritmo, "w", encoding="utf-8") as salida:       
        procesar_archivo_auth(origen, salida, campo)

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

    if (campo == "year"):
        dicT = dict(sorted(dic.items(), key=lambda item: item[1].get(campo, 0), reverse=True))
    else:
        dicT = dict(sorted(dic.items(), key=lambda item: item[1].get(campo, '')))

    for key in dicT:
        try:
            if not dicT[key].get(campo):
                continue

            salida.write("------------------------------------\n")
            salida.write(f"BDOrigen: {dicT[key].get('BDOrigen', 'No BDOrigen')}\n")
            salida.write(f"author: {dicT[key].get('author', 'No author')}\n")
            salida.write(f"title: {dicT[key].get('title', 'No title')}\n")
            salida.write(f"year: {dicT[key]['year']}\n")
            salida.write(f"journal: {dicT[key].get('journal', 'No journal')}\n")
            salida.write(f"doi: {dicT[key].get('doi', 'No doi')}\n")
            salida.write(f"abstract: {dicT[key].get('abstract', 'No abstract')}\n")
        except:
            pass

def procesar_archivo_auth(archivo, salida, campo):
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
                elif key == "author":
                    autores = value.strip().split(",")
                    lista[campo] = len(autores)
                    lista[key] = value.strip()
                else:
                    lista[key] = value.strip()
            except ValueError:
                contador += 1
                lista = {}
                dic[contador] = lista

        dic[contador] = lista

    dicT = dict(sorted(dic.items(), key=lambda item: item[1].get(campo, 0)))

    for key in dicT:
        try:
            if not dicT[key].get(campo):
                continue

            salida.write("------------------------------------\n")
            salida.write(f"BDOrigen: {dicT[key].get('BDOrigen', 'No BDOrigen')}\n")
            salida.write(f"author: {dicT[key].get('author', 'No author')}\n")
            salida.write(f"title: {dicT[key].get('title', 'No title')}\n")
            salida.write(f"year: {dicT[key]['year']}\n")
            salida.write(f"journal: {dicT[key].get('journal', 'No journal')}\n")
            salida.write(f"doi: {dicT[key].get('doi', 'No doi')}\n")
            salida.write(f"abstract: {dicT[key].get('abstract', 'No abstract')}\n")
            salida.write(f"{campo}: {dicT[key].get(campo, 'No '+campo)}\n")
        except:
            pass

def medir_tiempo_y_memoria(func, *args):
    tracemalloc.start()
    start_time = time.time()

    func(*args)

    end_time = time.time()
    memory_usage, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Tiempo de ejecución: {end_time - start_time:.4f} segundos")
    print(f"Memoria usada: {memory_usage / 1024:.4f} KB\n")
    #print(f"Pico de memoria: {peak_memory / 1024:.4f} KB")

if __name__ == "__main__":
    campo = 'year'
    algoritmo = "./Datos/TimSorts_Year.bib"
    origen = './../unificados.bib'

    print("Ejecución para los años:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'title'
    algoritmo = "./Datos/TimSorts_Title.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los titulos:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'journal'
    algoritmo = "./Datos/TimSorts_Journal.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por revista:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)

    campo = 'cantidad autores'
    algoritmo = "./Datos/TimSorts_CantAutores.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los articulos por cantidad de autores:")
    medir_tiempo_y_memoria(unificar_archivos_bib_auth, algoritmo, origen, campo)

    campo = 'BDOrigen'
    algoritmo = "./Datos/TimSorts_BDOrigen.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar los artículos por Base de datos origen:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)