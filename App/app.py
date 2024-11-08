from flask import Flask, render_template, make_response, url_for
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from pymongo import MongoClient
from collections import Counter
import textwrap
import base64
from collections import Counter, defaultdict

app = Flask(__name__, static_folder='images')

# Conectar a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["analisis"]
collection = db["articulos"]

def create_base64_image(fig):
    img = io.BytesIO()
    FigureCanvas(fig).print_png(img)
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf8')

@app.route('/')
def index():
    titles = [
        "Cantidad de productos por tipo y base de datos origen", 
        "Productos por año de publicación", 
        "Autores más concurrentes en títulos (Top 15)", 
        "Journals mas citados (Top 15)", 
        "Cantidad de articulos por base de datos", 
        "Cantidad y tipo de productos por año", 
        "Cantidad de publicaciones por autor y base de datos", 
        "Gráfico 8 xxxx", 
        "Gráfico 9 xxxx", 
        "Gráfico 10 xxxx", 
        "Gráfico 11 xxxx", 
        "Gráfico 12 xxxx", 
        "Gráfico 13 xxxx", 
        "Gráfico 14 xxxx", 
        "Gráfico 15 xxxx"
    ]

    # Diccionario de URLs
    url_map = {
        1: '/tipe', 
        2: '/year', 
        3: 'author',
        4: '/top_journals',
        5: '/database_articles',
        6: '/products_by_year_and_type',
        7: '/author_by_database'
        
    }
    
    cards = [
        {
            "title": titles[i-1],
            "description": f"Gráfico {i}",
            "graph_id": i,
            "url": url_map.get(i, url_for('plot_page', graph_id=i)),
            "image_url": url_for('static', filename=f'grafico{i}.png')
        }
        for i in range(1, 16)  # Crea 15 tarjetas
    ]
    
    return render_template('index.html', cards=cards)

@app.route('/year')
def generate_year():
    by_year = Counter([doc['year'] for doc in collection.find()])

    # Colormap for the points
    colormap = plt.get_cmap("viridis")
    norm = plt.Normalize(0, len(by_year))

    # Create a larger figure for better visibility
    fig, ax = plt.subplots(figsize=(10, 6))  # Increase the figure size
    years = list(by_year.keys())
    counts = list(by_year.values())
    
    # Scatter plot
    ax.scatter(years, counts, c=counts, cmap=colormap, s=100, edgecolors='black', alpha=0.7)

    # Connect the points with thin lines from the origin (y=0)
    for i, year in enumerate(years):
        ax.plot([year, year], [0, counts[i]], color='gray', linewidth=1)

    # Add titles and labels
    ax.set_title("Productos por Año", fontsize=16)
    ax.set_xlabel("Año", fontsize=14)
    ax.set_ylabel("Cantidad de Productos", fontsize=14)
    
    # Make sure the labels are clear
    ax.tick_params(axis='both', which='major', labelsize=12)
    
    # Generate the image and encode it to base64
    img_base64 = create_base64_image(fig)

    # Return the data to render in the template
    data = {
        'title': 'Cantidad de publicaciones por año',
        'text': 'Gráfico de los Años',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/tipe')
def generate_tipe():
    pipeline = [
        {
            '$group': {
                '_id': {
                    'BDOrigen': '$BDOrigen',
                    'Tipe': '$Tipe'
                },
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'count': -1}  # Ordenar de mayor a menor según la cantidad
        }
    ]

    # Ejecutar la agregación
    results = collection.aggregate(pipeline)

    # Preparar los datos para el gráfico
    by_bd_origen = {}
    for result in results:
        bd_origen = result['_id']['BDOrigen']
        tipo = result['_id']['Tipe']
        count = result['count']
        
        if bd_origen not in by_bd_origen:
            by_bd_origen[bd_origen] = {}
        
        by_bd_origen[bd_origen][tipo] = count

    # Crear el gráfico
    fig, ax = plt.subplots(figsize=(10, 6))

    # Colores para cada tipo
    colormap = plt.get_cmap("viridis")
    unique_tipes = sorted(set(t for bd in by_bd_origen.values() for t in bd.keys()))
    norm = plt.Normalize(0, len(unique_tipes))

    # Ancho de las barras
    width = 0.8 / len(unique_tipes)

    # Dibujar las barras por cada tipo dentro de cada BDOrigen
    for idx, tipo in enumerate(unique_tipes):
        positions = []
        values = []
        
        for i, (bd_origen, tipos) in enumerate(by_bd_origen.items()):
            positions.append(i + width * (idx - (len(unique_tipes) - 1) / 2))  # Ajustar posiciones para cada tipo
            values.append(tipos.get(tipo, 0))
        
        ax.bar(positions, values, width, label=tipo, color=colormap(norm(idx)), zorder=3)

    # Ajustes para las etiquetas y leyenda
    ax.set_title("Productos por BDOrigen y Tipo")
    ax.set_xlabel("BDOrigen")
    ax.set_ylabel("Cantidad de Productos")
    ax.set_xticks(range(len(by_bd_origen)))
    ax.set_xticklabels(list(by_bd_origen.keys()))
    ax.legend(title="Tipo de Producto")

    # Convertir el gráfico a base64
    img_base64 = create_base64_image(fig)

    # Datos a pasar a la plantilla
    data = {
        
        'title': 'Cantidad de productos por tipo y base de datos origen',
        'text': 'Gráfico mostrando productos agrupados por Tipo y BDOrigen',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/author')
def generate_author():
    # Obtener todos los documentos de la colección y desglosar los autores en una lista
    all_authors = []
    for doc in collection.find():
        # Desglosar autores, eliminar espacios y filtrar autores vacíos
        authors = [author.strip() for author in doc['author'].split(",") if author.strip()]
        # Evitar duplicados dentro del mismo título
        unique_authors = set(authors)
        all_authors.extend(unique_authors)
    
    # Contar la cantidad de títulos por autor y obtener los 15 principales
    top_authors = Counter(all_authors).most_common(15)

    # Crear el gráfico de barras horizontal para los autores con más artículos
    fig, ax = plt.subplots(figsize=(10, 6))  # Tamaño ajustado para mejor visualización
    authors, counts = zip(*top_authors)
    
    # Aplicar la paleta de colores 'viridis'
    ax.barh(authors, counts, color=plt.cm.viridis([i / len(counts) for i in range(len(counts))]))
    
    ax.set_title("Top 15 Autores con Más Apariciones en Títulos")
    ax.set_xlabel("Cantidad de Títulos")
    
    # Convertir el gráfico a PNG y luego a Base64 para renderizar en HTML
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    img_base64 = base64.b64encode(output.getvalue()).decode()

    data = {
        'title': 'Autores más concurrentes en títulos',
        'text': 'Gráfico de autores',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/top_journals')
def top_journals():
    # Contar el número de citas para cada journal, ignorando los vacíos
    journal_counts = Counter([doc['journal'] for doc in collection.find() if 'journal' in doc and doc['journal']])

    # Seleccionar los 15 journals más citados
    top_journals = journal_counts.most_common(15)
    journals = [item[0] for item in top_journals]
    counts = [item[1] for item in top_journals]

    # Configurar la paleta de colores 'viridis' de matplotlib
    colors = [plt.cm.viridis(i / len(counts)) for i in range(len(counts))]

    # Configurar la figura y ajustar el tamaño para mostrar los nombres completos
    fig, ax = plt.subplots(figsize=(15, 10))  # Ajustar el tamaño de la figura

    # Crear un gráfico de barras horizontal para mejor legibilidad
    bars = ax.barh(journals, counts, color=colors, height=0.6)  # Ajustar la altura de las barras

    # Aumentar el espacio entre las barras
    ax.set_ylim(-0.5, len(journals) - 0.5)  # Incrementa el límite superior e inferior para dar más espacio

    ax.invert_yaxis()  # Invertir el eje Y para que el journal más citado esté arriba

    # Ajustar las etiquetas de los journals con textwrap (agregar saltos de línea)
    wrapped_journals = [textwrap.fill(journal, width=25) for journal in journals]  # Ajustar el ancho

    # Ajustar las etiquetas y los títulos
    ax.set_title("Top 15 Journals Más Citados", fontsize=14)  # Reducir tamaño del título
    ax.set_xlabel("Número de Citas", fontsize=12)  # Reducir tamaño de las etiquetas
    ax.set_ylabel("Journal", fontsize=12)  # Reducir tamaño de las etiquetas

    # Ajustar las etiquetas de Y
    ax.set_yticklabels(wrapped_journals, fontsize=10)  # Aplicar el texto envuelto y ajustar el tamaño de fuente

    # Aumentar el tamaño de las etiquetas y añadir márgenes para mejor visibilidad
    ax.tick_params(axis='y', labelsize=6)  # Reducir el tamaño de las etiquetas en Y
    fig.subplots_adjust(left=0.4)  # Ajustar márgenes de la figura

    # Etiquetas de cada barra
    for bar, count in zip(bars, counts):
        ax.text(count + 1, bar.get_y() + bar.get_height() / 2, str(count), va='center', fontsize=8)

    # Convertir la figura a imagen en base64
    img_base64 = create_base64_image(fig)

    # Retornar los datos para la plantilla
    data = {
        'text': 'Top 15 Journals Más Citados',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/database_articles')
def generate_database_articles():
    # Obtener todos los documentos de la colección y desglosar las bases de datos
    all_databases = []
    for doc in collection.find():
        # Obtener la base de datos (BDOrigen) y agregarla a la lista
        if 'BDOrigen' in doc:  # Asegurarse de que la base de datos exista
            all_databases.append(doc['BDOrigen'])
    
    # Contar la cantidad de artículos por base de datos y obtener los 15 principales
    top_databases = Counter(all_databases).most_common(15)

    # Crear el gráfico de barras verticales para las bases de datos con más artículos
    fig, ax = plt.subplots(figsize=(10, 6))  # Tamaño ajustado para mejor visualización
    databases, counts = zip(*top_databases)
    
    # Crear el gráfico de barras verticales
    bars = ax.bar(databases, counts, color=plt.cm.viridis([i / len(counts) for i in range(len(counts))]))

    # Agregar etiquetas de cantidad encima de cada barra
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 1,  # Colocar encima de la barra
                str(int(yval)), ha='center', va='bottom', fontsize=10)

    # Título y etiquetas
    ax.set_title("Cantidad de artículos por base de datos")
    ax.set_xlabel("Base de Datos")
    ax.set_ylabel("Cantidad de Artículos")

    # Rotar las etiquetas del eje X si son muy largas
    ax.set_xticklabels(databases, rotation=0, ha='right', fontsize=10)

    # Convertir el gráfico a PNG y luego a Base64 para renderizar en HTML
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    img_base64 = base64.b64encode(output.getvalue()).decode()

    data = {
        'title': 'Distribución de artículos por cada base de datos',
        'text': 'Gráfico de Artículos por Base de Datos',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/products_by_year_and_type')
def generate_products_by_year_and_type():
    # Pipeline de agregación para obtener el conteo de productos por año y tipo
    pipeline = [
        {
            '$group': {
                '_id': {
                    'year': '$year',
                    'Tipe': '$Tipe'
                },
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'_id.year': 1}  # Ordenar por año
        }
    ]

    # Ejecutar la agregación
    results = collection.aggregate(pipeline)

    # Preparar los datos para el gráfico
    by_year_and_type = {}
    all_types = set()  # Para rastrear todos los tipos únicos
    for result in results:
        year = result['_id']['year']
        tipe = result['_id']['Tipe']
        count = result['count']

        # Añadir datos al diccionario por año y tipo
        if year not in by_year_and_type:
            by_year_and_type[year] = {}
        by_year_and_type[year][tipe] = count
        all_types.add(tipe)  # Registrar el tipo único

    # Crear el gráfico de barras apiladas
    fig, ax = plt.subplots(figsize=(15, 8))
    years = sorted(by_year_and_type.keys())
    types = sorted(all_types)  # Tipos ordenados para consistencia de colores
    bottom = [0] * len(years)  # Inicialización para apilar

    # Colores para cada tipo
    colormap = plt.get_cmap("viridis")
    norm = plt.Normalize(0, len(types))
    
    # Dibujar las barras apiladas
    for idx, tipe in enumerate(types):
        counts = [by_year_and_type[year].get(tipe, 0) for year in years]
        ax.bar(years, counts, bottom=bottom, label=tipe, color=colormap(norm(idx)), zorder=3)
        bottom = [bottom[i] + counts[i] for i in range(len(counts))]  # Acumular para apilar

    # Configurar etiquetas y leyenda
    ax.set_title("Cantidad de Productos por Año y Tipo")
    ax.set_xlabel("Año")
    ax.set_ylabel("Cantidad de Productos")
    ax.legend(title="Tipo de Producto")

    # Convertir el gráfico a base64 para mostrar en HTML
    img_base64 = create_base64_image(fig)

    # Datos a pasar a la plantilla
    data = {
        'title': 'Cantidad de productos por tipo y año',
        'text': 'Gráfico mostrando productos agrupados por Tipo y Año',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/author_by_database')
def generate_author_by_database():
    # Obtener todos los documentos de la colección y desglosar los autores por BDOrigen
    author_db_data = defaultdict(lambda: Counter())
    for doc in collection.find():
        # Separar autores y filtrar nombres vacíos
        authors = [author.strip() for author in doc['author'].split(",") if author.strip()]
        # Evitar duplicados dentro del mismo título
        unique_authors = set(authors)
        # Contar publicaciones por BDOrigen para cada autor
        for author in unique_authors:
            author_db_data[author][doc['BDOrigen']] += 1

    # Seleccionar los 15 autores con más publicaciones en total
    total_counts = {author: sum(db_counts.values()) for author, db_counts in author_db_data.items()}
    top_authors = dict(sorted(total_counts.items(), key=lambda x: x[1], reverse=True)[:15])

    # Preparar los datos para el gráfico apilado
    db_sources = sorted({db for counts in author_db_data.values() for db in counts})  # Listar todas las BDOrigen
    counts_by_db = {db: [] for db in db_sources}
    for author in top_authors:
        for db in db_sources:
            counts_by_db[db].append(author_db_data[author].get(db, 0))  # Obtener el conteo o 0 si no hay datos

    # Crear el gráfico de barras apiladas horizontales
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = [0] * len(top_authors)  # Inicializar la posición inferior para apilar

    # Colores para cada base de datos
    colormap = plt.get_cmap("viridis")
    norm = plt.Normalize(0, len(db_sources))

    for idx, db in enumerate(db_sources):
        ax.barh(list(top_authors.keys()), counts_by_db[db], left=bottom,
                label=db, color=colormap(norm(idx)), zorder=3)
        bottom = [bottom[i] + counts_by_db[db][i] for i in range(len(bottom))]  # Acumular para apilar

    # Ajustes de etiquetas y leyenda
    ax.set_title("Autores por Base de Datos")
    ax.set_xlabel("Cantidad de Títulos")
    ax.legend(title="BDOrigen", bbox_to_anchor=(0.78, 1), loc='upper left')  # Colocar leyenda fuera del gráfico

    # Convertir el gráfico a base64 para el renderizado en HTML
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    img_base64 = base64.b64encode(output.getvalue()).decode()

    # Datos a pasar a la plantilla
    data = {
        'title': 'Cantidad de publicaciones por autor y base de datos',
        'text': 'Gráfico de autores por BDOrigen',
        'img': img_base64
    }

    return render_template('stats.html', data=data)







@app.route('/grafico/<int:graph_id>')
def plot_page(graph_id):
    # Aquí defines la lógica para mostrar la página individual con la gráfica
    return render_template('plot.html', graph_id=graph_id)

if __name__ == '__main__':
    app.run(debug=True)


