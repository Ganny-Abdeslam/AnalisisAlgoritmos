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

    # Llamada al algoritmo Radix Sort
    radix_sort(dic, campo)

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

# Implementación de Radix Sort
def radix_sort(dic, campo):
    # Extraer los valores de los campos
    keys = list(dic.keys())
    
    # Si el campo es "year" (un número), Radix Sort se puede aplicar
    if isinstance(dic[keys[0]].get(campo), int):
        max_value = max(dic[keys[i]].get(campo, 0) for i in keys)
        
        # Radix sort por dígitos
        exp = 1
        while max_value // exp > 0:
            counting_sort_by_digit(dic, campo, keys, exp)
            exp *= 10

    # Si el campo es "title" (un texto), hacemos un ordenamiento por caracteres
    elif isinstance(dic[keys[0]].get(campo), str):
        for i in range(len(dic[keys[0]].get(campo, ''))):
            counting_sort_by_char(dic, campo, keys, i)


def counting_sort_by_digit(dic, campo, keys, exp):
    n = len(keys)
    output = [0] * n
    count = [0] * 10

    # Contar las ocurrencias de los dígitos en la posición actual
    for i in range(n):
        value = dic[keys[i]].get(campo, 0)
        digit = (value // exp) % 10
        count[digit] += 1

    # Sumar los elementos de count para que contengan las posiciones reales
    for i in range(1, 10):
        count[i] += count[i - 1]

    # Construir el array de salida
    for i in range(n - 1, -1, -1):
        value = dic[keys[i]].get(campo, 0)
        digit = (value // exp) % 10
        output[count[digit] - 1] = keys[i]
        count[digit] -= 1

    # Copiar el array de salida en diccionario
    for i in range(n):
        keys[i] = output[i]

# Para ordenar por caracteres (en caso de que el campo sea un texto)
def counting_sort_by_char(dic, campo, keys, index):
    n = len(keys)
    output = [0] * n
    count = [0] * 256  # Asumiendo caracteres ASCII

    # Contar las ocurrencias de los caracteres en la posición actual
    for i in range(n):
        value = dic[keys[i]].get(campo, '')
        char = ord(value[index]) if index < len(value) else 0
        count[char] += 1

    # Sumar los elementos de count para que contengan las posiciones reales
    for i in range(1, 256):
        count[i] += count[i - 1]

    # Construir el array de salida
    for i in range(n - 1, -1, -1):
        value = dic[keys[i]].get(campo, '')
        char = ord(value[index]) if index < len(value) else 0
        output[count[char] - 1] = keys[i]
        count[char] -= 1

    # Copiar el array de salida en diccionario
    for i in range(n):
        keys[i] = output[i]

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
    algoritmo = "./Datos/RadixSort_Year.bib"
    origen = './../unificados.bib'

    print("Ejecución para ordenar por años:")
    medir_tiempo_y_memoria(unificar_archivos_bib, algoritmo, origen, campo)
