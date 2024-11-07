from flask import Flask, render_template, make_response
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from pymongo import MongoClient
from collections import Counter
import base64

app = Flask(__name__)

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
    return render_template('index.html')  # Página principal de la app

@app.route('/year')
def generate_year():
    by_year = Counter([doc['year'] for doc in collection.find()])

    fig, ax = plt.subplots()
    ax.bar(by_year.keys(), by_year.values(), color="skyblue")
    ax.set_title("Productos por Año")
    ax.set_xlabel("Año")
    ax.set_ylabel("Cantidad de Productos")
    img_base64 = create_base64_image(fig)

    data = {
        'title': 'Productos por Año de Publicación',
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
        'title': 'Productos por Tipo y BDOrigen',
        'text': 'Gráfico mostrando productos agrupados por Tipo y BDOrigen',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/generate_stats')
def generate_stats():

    # Obtener los 15 artículos más citados y desglosar autores
    top_cited_articles = list(collection.find().sort("citations", -1).limit(15))
    
    # Desglosar autores en una lista a partir de top_cited_articles y contarlos
    all_authors = []
    for doc in top_cited_articles:
        authors = doc['author'].split(", ")
        all_authors.extend(authors)
    top_authors = Counter(all_authors).most_common(15)

    # Crear el gráfico de barras para los autores más citados
    fig, ax = plt.subplots()
    authors, counts = zip(*top_authors)
    ax.barh(authors, counts, color='skyblue')
    ax.set_title("Top 15 Autores Más Citados")
    ax.set_xlabel("Cantidad de Citaciones")
    
    # Convertir el gráfico a PNG y luego a Base64 para renderizar en HTML
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plot_data = base64.b64encode(output.getvalue()).decode()


    # Pasar imágenes codificadas en base64 a la plantilla
    return render_template('stats.html')

if __name__ == '__main__':
    app.run(debug=True)
