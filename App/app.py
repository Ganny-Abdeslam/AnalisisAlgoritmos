from flask import Flask, render_template, make_response, url_for
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from pymongo import MongoClient
from collections import Counter
import textwrap
import base64
import pandas as pd
import seaborn as sns
from collections import Counter, defaultdict
from wordcloud import WordCloud
import random
import re

app = Flask(__name__, static_folder='images')

# Conectar a MongoDB
#client = MongoClient("mongodb://localhost:27017/")
client = MongoClient("mongodb+srv://unix:unix@cluster0.51z20q3.mongodb.net")
db = client["unilocal"]
collection = db["articulos"]

def create_base64_image(fig):
    img = io.BytesIO()
    FigureCanvas(fig).print_png(img)
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf8')

@app.route('/')
def index():

    #Aqui se definen los titulos de los graficos individuales, en orden de 1 a 12 segun se vea en el front
    titles = [
        "Cantidad de productos por tipo y base de datos origen", 
        "Productos por año de publicación", 
        "Autores más concurrentes en títulos (Top 15)", 
        "Journals mas citados (Top 15)", 
        "Cantidad de articulos por base de datos", 
        "Cantidad y tipo de productos por año", 
        "Cantidad de publicaciones por autor y base de datos", 
        "Cantidad de Artículos por Journal", 
        "Cantidad de autores por pais", 
        "Cantidad de variables por Categorías", 
        "Nube de palabras (Variables respecto a los abstracts)", 
        "Nube de palabras respecto a los abstracts", 

    ]

    #Aqui es el mapeo de las URL para saber que boton va a llevar a que pagina
    url_map = {
        1: '/tipe', 
        2: '/year', 
        3: 'author',
        4: '/top_journals',
        5: '/database_articles',
        6: '/products_by_year_and_type',
        7: '/author_by_database',
        8: '/journal_heatmap',
        9: '/authors_by_country',
        10: '/palabras-variable',
        11: '/nube-palabrasPull',
        12: '/nube-palabras',

        
    }
    
    cards = [
    {
        "title": titles[i-1],
        "description": f"Gráfico {i}",
        "graph_id": i,
        "url": url_for('variables_page') if i == 10 else url_map.get(i, url_for('plot_page', graph_id=i)),
        "image_url": url_for('static', filename=f'grafico{i}.png')
    }
    for i in range(1, 13)  #Aqui se pueden generar la cantidad de cards que queramos poner en el front
]
    
    return render_template('index.html', cards=cards)

@app.route('/year')
def generate_year():
    by_year = Counter([doc['year'] for doc in collection.find()])

    colormap = plt.get_cmap("viridis")
    norm = plt.Normalize(0, len(by_year))

    fig, ax = plt.subplots(figsize=(10, 6)) 
    years = list(by_year.keys())
    counts = list(by_year.values())
    
    
    ax.scatter(years, counts, c=counts, cmap=colormap, s=100, edgecolors='black', alpha=0.7)

    for i, year in enumerate(years):
        ax.plot([year, year], [0, counts[i]], color='gray', linewidth=1)

    ax.set_title("Productos por Año", fontsize=16)
    ax.set_xlabel("Año", fontsize=14)
    ax.set_ylabel("Cantidad de Productos", fontsize=14)
    ax.set_xticks(range(1949, 2025, 10))
    
    ax.tick_params(axis='both', which='major', labelsize=12)
    

    img_base64 = create_base64_image(fig)

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
            '$sort': {'count': -1}  
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

    width = 0.8 / len(unique_tipes)

    # Dibujar las barras por cada tipo dentro de cada BDOrigen
    for idx, tipo in enumerate(unique_tipes):
        positions = []
        values = []
        
        for i, (bd_origen, tipos) in enumerate(by_bd_origen.items()):
            positions.append(i + width * (idx - (len(unique_tipes) - 1) / 2))  
            values.append(tipos.get(tipo, 0))
        
        ax.bar(positions, values, width, label=tipo, color=colormap(norm(idx)), zorder=3)

    # Ajustes para las etiquetas y leyenda
    ax.set_title("Productos por BDOrigen y Tipo")
    ax.set_xlabel("BDOrigen")
    ax.set_ylabel("Cantidad de Productos")
    ax.set_xticks(range(len(by_bd_origen)))
    ax.set_xticklabels(list(by_bd_origen.keys()))
    ax.legend(title="Tipo de Producto")

    img_base64 = create_base64_image(fig)

    data = {
        
        'title': 'Cantidad de productos por tipo y base de datos origen',
        'text': 'Gráfico mostrando productos agrupados por Tipo y BDOrigen',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/author')
def generate_author():
    all_authors = []
    for doc in collection.find():
        authors = [author.strip() for author in doc['author'].split(",") if author.strip()]
        unique_authors = set(authors)
        all_authors.extend(unique_authors)
    
    top_authors = Counter(all_authors).most_common(15)

    fig, ax = plt.subplots(figsize=(10, 6)) 
    authors, counts = zip(*top_authors)
    
    ax.barh(authors, counts, color=plt.cm.viridis([i / len(counts) for i in range(len(counts))]))
    
    ax.set_title("Top 15 Autores con Más Apariciones en Títulos")
    ax.set_xlabel("Cantidad de Títulos")
    
    for i, count in enumerate(counts):
        ax.text(count + 0.9, i, str(count), va='center')  
    
    
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
    journal_counts = Counter([doc['journal'] for doc in collection.find() if 'journal' in doc and doc['journal']])

    top_journals = journal_counts.most_common(15)
    journals = [item[0] for item in top_journals]
    counts = [item[1] for item in top_journals]

    colors = [plt.cm.viridis(i / len(counts)) for i in range(len(counts))]

    # Configurar la figura y ajustar el tamaño para mostrar los nombres completos
    fig, ax = plt.subplots(figsize=(15, 10))  

    # Crear un gráfico de barras horizontal para mejor legibilidad
    bars = ax.barh(journals, counts, color=colors, height=0.6)  

    # Aumentar el espacio entre las barras
    ax.set_ylim(-0.5, len(journals) - 0.5)  
    ax.invert_yaxis()  

    # Ajustar las etiquetas de los journals con textwrap (agregar saltos de línea)
    wrapped_journals = [textwrap.fill(journal, width=25) for journal in journals]  

    ax.set_title("Top 15 Journals Más Citados", fontsize=14)  
    ax.set_xlabel("Número de Citas", fontsize=12)  
    ax.set_ylabel("Journal", fontsize=12)  

    ax.set_yticklabels(wrapped_journals, fontsize=10)  

    ax.tick_params(axis='y', labelsize=6)  
    fig.subplots_adjust(left=0.2, right=0.8, top=0.95)  

    
    for bar, count in zip(bars, counts):
        ax.text(count + 1, bar.get_y() + bar.get_height() / 2, str(count), va='center', fontsize=8)

    
    img_base64 = create_base64_image(fig)

    
    data = {
        'title': 'Top 15 Journals Más Citados',
        'text': 'Top 15 Journals Más Citados',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/database_articles')
def generate_database_articles():
    
    all_databases = []
    for doc in collection.find():
       
        if 'BDOrigen' in doc:  
            all_databases.append(doc['BDOrigen'])
    
    #Se cuenta la cantidad de artículos por base de datos y obtener los 15 principales
    top_databases = Counter(all_databases).most_common(15)

    fig, ax = plt.subplots(figsize=(10, 6))  
    databases, counts = zip(*top_databases)
    
    bars = ax.bar(databases, counts, color=plt.cm.viridis([i / len(counts) for i in range(len(counts))]))

    #Esto para poner las etiquetas de cantidad encima de cada barra
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 1, 
                str(int(yval)), ha='center', va='bottom', fontsize=10)

    ax.set_title("Cantidad de artículos por base de datos")
    ax.set_xlabel("Base de Datos")
    ax.set_ylabel("Cantidad de Artículos")

    #Rotation para las etiquetas del eje X
    ax.set_xticklabels(databases, rotation=0, ha='right', fontsize=10)

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
            '$sort': {'_id.year': 1}  
        }
    ]

    results = collection.aggregate(pipeline)

    by_year_and_type = {}
    all_types = set()  
    for result in results:
        year = result['_id']['year']
        tipe = result['_id']['Tipe']
        count = result['count']

        #Esto es para añadir datos al diccionario
        if year not in by_year_and_type:
            by_year_and_type[year] = {}
        by_year_and_type[year][tipe] = count
        all_types.add(tipe)  

    #Se crea el gráfico de barras apiladas
    fig, ax = plt.subplots(figsize=(15, 8))
    years = sorted(by_year_and_type.keys())
    types = sorted(all_types)  
    bottom = [0] * len(years)  


    colormap = plt.get_cmap("viridis")
    norm = plt.Normalize(0, len(types))
    
    for idx, tipe in enumerate(types):
        counts = [by_year_and_type[year].get(tipe, 0) for year in years]
        ax.bar(years, counts, bottom=bottom, label=tipe, color=colormap(norm(idx)), zorder=3)
        bottom = [bottom[i] + counts[i] for i in range(len(counts))]  

    ax.set_title("Cantidad de Productos por Año y Tipo")
    ax.set_xlabel("Año")
    ax.set_ylabel("Cantidad de Productos")
    ax.legend(title="Tipo de Producto")
    ax.set_xticks(range(1952, 2025, 4))

    img_base64 = create_base64_image(fig)

    data = {
        'title': 'Cantidad de productos por tipo y año',
        'text': 'Gráfico mostrando productos agrupados por Tipo y Año',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/author_by_database')
def generate_author_by_database():
    author_db_data = defaultdict(lambda: Counter())
    for doc in collection.find():
        authors = [author.strip() for author in doc['author'].split(",") if author.strip()]
        unique_authors = set(authors)
        for author in unique_authors:
            author_db_data[author][doc['BDOrigen']] += 1

    #Seleccionar los 15 autores con más publicaciones en total
    total_counts = {author: sum(db_counts.values()) for author, db_counts in author_db_data.items()}
    top_authors = dict(sorted(total_counts.items(), key=lambda x: x[1], reverse=True)[:15])

    #Ordenar los autores en orden descendente 
    sorted_authors = sorted(top_authors.keys(), key=lambda x: total_counts[x], reverse=True)

    db_sources = sorted({db for counts in author_db_data.values() for db in counts})  
    counts_by_db = {db: [] for db in db_sources}
    for author in sorted_authors:
        for db in db_sources:
            counts_by_db[db].append(author_db_data[author].get(db, 0))  

    #Crear el gráfico de barras apiladas horizontales
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = [0] * len(sorted_authors)  

    #Paleta de colores 
    colormap = plt.get_cmap("viridis")
    norm = plt.Normalize(0, len(db_sources))

    for idx, db in enumerate(db_sources):
        ax.barh(sorted_authors, counts_by_db[db], left=bottom,
                label=db, color=colormap(norm(idx)), zorder=3)
        bottom = [bottom[i] + counts_by_db[db][i] for i in range(len(bottom))]  

    # justes de etiquetas y leyenda
    ax.set_title("Autores por Base de Datos")
    ax.set_xlabel("Cantidad de publicaciones")
    ax.invert_yaxis()  
    ax.legend(title="BDOrigen", loc='lower right')  


    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    img_base64 = base64.b64encode(output.getvalue()).decode()


    data = {
        'title': 'Cantidad de publicaciones por autor y base de datos',
        'text': 'Gráfico de autores por BDOrigen',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/journal_heatmap')
def generate_journal_heatmap():
    #Contar el número de artículos para cada journal, ignorando los vacíos
    journal_counts = Counter([doc['journal'] for doc in collection.find() if 'journal' in doc and doc['journal']])

    #Seleccionar los 15 journals con más artículos
    top_journals = journal_counts.most_common(15)
    journals = [item[0] for item in top_journals]
    counts = [item[1] for item in top_journals]

    df = pd.DataFrame({'Journal': journals, 'Articles': counts}).set_index('Journal')

    #Configurar el mapa de calor
    fig, ax = plt.subplots(figsize=(13, 8))
    sns.heatmap(df, annot=True, cmap='viridis', cbar=True, linewidths=0.5, linecolor='gray', fmt="d", ax=ax)

    #Ajustar las etiquetas de los journals con textwrap
    wrapped_journals = [textwrap.fill(journal, width=25) for journal in journals]  

    ax.set_title("Cantidad de Artículos por Journal", fontsize=16)
    ax.set_xlabel("Número de Artículos")
    ax.set_ylabel("Journal")

    ax.set_yticklabels(wrapped_journals, fontsize=5, rotation=0)  

    ax.tick_params(axis='y', labelsize=5)  
    fig.subplots_adjust(left=0.2, right=0.8)  

  
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    img_base64 = base64.b64encode(output.getvalue()).decode()


    data = {
        'title': 'Mapa de Calor de Artículos por Journal',
        'text': 'Gráfico de Mapa de Calor de la Cantidad de Artículos por Journal',
        'img': img_base64
    }

    return render_template('stats.html', data=data)

@app.route('/nube-palabras')
def generate_wordcloud():
    #Se consultan los abstract en la base de datos Mongo
    abstracts = [doc['abstract'] for doc in collection.find()]
    
    text = ' '.join(abstracts)
    
    #Se crea la nube de palabras
    wordcloud = WordCloud(width=1200, height=800, background_color='white').generate(text)
    
    #Crea el grafico
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off') 
    
 
    img_base64 = create_base64_image(fig)
    

    data = {
        'title': 'Nube de Palabras respecto a los abstracts',
        'img': img_base64
    }

    return render_template('wordcloud.html', data=data)

@app.route('/nube-palabrasPull')
def generate_wordcloudPull():

    with open('palabras.txt', 'r') as f:
        palabras_pull = set(line.strip().lower() for line in f)

    #Se consultan los abstract en la base de datos Mongo
    abstracts = [doc['abstract'] for doc in collection.find()]

    #Se unen todos los abstracts en un solo texto
    text = ' '.join(abstracts)

    # Filtrar solo las palabras que están en el pull
    palabras_filtradas = ' '.join([palabra for palabra in text.split() if palabra.lower() in palabras_pull])

    #Se crea la nube de palabras 
    wordcloud = WordCloud(width=1200, height=800, background_color='white').generate(palabras_filtradas)

    #Crea el grafico
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')  

    
    img_base64 = create_base64_image(fig)

    data = {
        'title': 'Nube de Palabras de las variables respecto a los abstracts ',
        'img': img_base64
    }

    return render_template('wordcloud.html', data=data)

def obtener_pais_aleatorio():
    paises = ['EEUU', 'Canada', 'Reino Unido', 'Alemania', 'Francia', 'España', 'Italia', 'Australia', 'India', 'China', 'México', 'Brasil', 'Japón', 'Argentina', 'Sudáfrica']
    return random.choice(paises)

@app.route('/authors_by_country')
def authors_by_country():
    
    authors_by_country = []

    for doc in collection.find():
    
        authors = [author.strip() for author in doc['author'].split(",") if author.strip()]
        #Se debe asignar un país aleatorio a cada autor
        for author in authors:
            country = obtener_pais_aleatorio()
            authors_by_country.append(country)

    #Se cuenta la cantidad de autores por país
    country_counts = Counter(authors_by_country)
    top_countries = country_counts.most_common()  

    #Se crea el grafico
    fig, ax = plt.subplots(figsize=(12, 8)) 
    countries, counts = zip(*top_countries)
    
    #Barras horizontal y paleta de colores
    ax.barh(countries, counts, color=plt.cm.viridis([i / len(counts) for i in range(len(counts))]))
    
    ax.set_title("Cantidad de Autores por País")
    ax.set_xlabel("Cantidad de Autores")
    
    # Agregar etiquetas del valor de cada barra
    for i, count in enumerate(counts):
        ax.text(count + 0.9, i, str(count), va='center') 
    
    # Convertir el gráfico a PNG y luego a Base64 para renderizar en HTML
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    img_base64 = base64.b64encode(output.getvalue()).decode()

    data = {
        'title': 'Autores por País',
        'text': 'Gráfico de autores distribuidos por país',
        'img': img_base64
    }

    return render_template('stats.html', data=data)


@app.route('/palabras-variable')
def palabras_variable():
    arr = [
     [
        'Abstraction',
        'Algorithm',
        'Algorithmic thinking',
        'Coding',
        'Collaboration',
        'Cooperation',
        'Creativity',
        'Critical thinking',
        'Debug',
        'Decomposition',
        'Evaluation',
        'Generalization',
        'Logic',
        'Logical thinking',
        'Modularity',
        'Patterns recognition',
        'Problem solving',
        'Programming',
        'Representation',
        'Reuse',
        'Simulation',
    ],

    [
        'Conditionals',
        'Control structures',
        'Directions',
        'Events',
        'Funtions',
        'Loops',
        'Modular structure',
        'Parallelism',
        'Sequences',
        'Software/hardware',
        'Variables',
    ],

    [
        'Emotional',
        'Engagement',
        'Motivation',
        'Perceptions',
        'Persistence',
        'Self-efficacy',
        'Self-perceived'
    ],

    [
        'Classical Test Theory - CTT',
        'Confirmatory Factor Analysis - CFA',
        'Exploratory Factor Analysis - EFA',
        'Item Response Theory(IRT) - IRT',
        'Reliability',
        'Structural Equation Model - SEM',
        'Validity',
    ],

    [
        'Beginners Computational Thinking test - BCTt',
        'Coding Attitudes Survey - ESCAS',
        'Collaborative Computing Observation Instrument',
        'Competent Computational Thinking test - cCTt',
        'Computational thinking skills test - CTST',
        'Computational concepts',
        'Computational Thinking Assessment for Chinese Elementary Students - CTA-CES',
        'Computational Thinking Challenge - CTC',
        'Computational Thinking Levels Scale - CTLS',
        'Computational Thinking Scale - CTS',
        'Computational Thinking Skill Levels Scale - CTS',
        'Computational Thinking Test - CTt',
        'Computational Thinking Test',
        'Computational Thinking Test for Elementary School Students - CTT-ES',
        'Computational Thinking Test for Lower Primary - CTtLP',
        'Computational thinking-skill tasks on numbers and arithmetic',
        'Computerized Adaptive Programming Concepts Test - CAPCT',
        'CT Scale - CTS',
        'Elementary Student Coding Attitudes Survey - ESCAS',
        'General self-efficacy scale',
        'ICT competency test',
        'Instrument of computational identity',
        'KBIT fluid intelligence subtest',
        'Mastery of computational concepts Test and an Algorithmic Test',
        'Multidimensional 21st Century Skills Scale',
        'Self-efficacy scale',
        'STEM learning attitude scale - STEM-LAS',
        'The computational thinking scale',
    ],

    [
        'No experimental',
        'Experimental', 'Longitudinal research',
        'Mixed methods',
        'Post-test',
        'Pre-test',
        'Quasi-experiments',
    ],

    [
        'Upper elementary education',
        'Upper elementary school',
        'Primary school',
        'Primary education',
        'Elementary school',
        'Early childhood education',
        'Kindergarten',
        'Preschool',
        'Secondary school',
        'Secondary education',
        'high school',
        'higher education',
        'University',
        'College'
    ],

    [
        'Block programming',
        'Mobile application',
        'Pair programming',
        'Plugged activities',
        'Programming',
        'Robotics',
        'Spreadsheet',
        'STEM',
        'Unplugged activities'
    ],

    [
        'Construct-by-self mind mapping',
        'CBS-MM',
        'Construct-on-scaffold mind mapping',
        'COS-MM',
        'Design-based learning',
        'CTDBL',
        'Design-based learning',
        'DBL',
        'Evidence-centred design approach',
        'Gamification',
        'Reverse engineering pedagogy',
        'REP',
        'Technology-enhanced learning',
        'Collaborative learning',
        'Cooperative learning',
        'Flipped classroom',
        'Game-based learning',
        'Inquiry-based learning',
        'Personalized learning',
        'Problem-based learning',
        'Project-based learning',
        'Universal design for learning',
    ],

    [
        'Alice',
        'Arduino',
        'Scratch',
        'ScratchJr',
        'Blockly Games',
        'Code.org',
        'Codecombat',
        'CSUnplugged',
        'Robot Turtles',
        'Hello Ruby',
        'Kodable',
        'LightbotJr',
        'KIBO robots',
        'BEE BOT',
        'CUBETTO',
        'Minecraft',
        'Agent Sheets',
        'Mimo',
        'Py Learn',
        'SpaceChem',
    ]]

        #Aqui hace el conteo de palabras en los abstracts
    arrAux = [
        sum(collection.count_documents({'abstract': re.compile(f'.*{re.escape(word.lower())}.*', re.IGNORECASE)})
            for word in category) for category in arr
    ]

    #Diccionario para las categorias de la tabla
    categorias = {
        'Habilidades': arrAux[0],
        'Conceptos computacionales': arrAux[1],
        'Actitudes': arrAux[2],
        'Propiedades psicométricas': arrAux[3],
        'Herramienta de evaluación': arrAux[4],
        'Diseño de investigación': arrAux[5],
        'Nivel de escolaridad': arrAux[6],
        'Medio': arrAux[7],
        'Estrategia': arrAux[8],
        'Herramienta': arrAux[9]
    }

    
    labels, values = zip(*sorted(categorias.items(), key=lambda x: x[1], reverse=True))

    #Se crea el gráfico de barras horizontal
    fig, ax = plt.subplots(figsize=(14, 8))  
    bar_height = 0.6  

    ax.barh(labels, values, height=bar_height, color=plt.cm.viridis([i / len(values) for i in range(len(values))]), edgecolor='black')
    ax.set_title("Distribución de Categorías", fontsize=16)
    ax.set_xlabel("Cantidad", fontsize=14, labelpad=20)  
    ax.set_ylabel("Categorías", fontsize=14)

    # Para ajustar las etiquetas del eje 
    max_label_length = 20  
    wrapped_labels = [textwrap.fill(label, width=max_label_length) for label in labels]
    ax.set_yticklabels(wrapped_labels, fontsize=10)

    # Convertir la imagen en base64 para el template
    img_base64 = create_base64_image(fig)

    data = {
        'title': 'Cantidad de variables por Categorías',
        'text': 'Gráfico de Categorías',
        'img': 'images/grafico10.png'
    }

    return render_template('variables.html', data=data)

    
@app.route('/variables_diez')
def variables_page():
    data = {
        'key': 'value', 
    }
    return render_template('variables.html', data=data)


@app.route('/grafico/<int:graph_id>')
def plot_page(graph_id):
    return render_template('plot.html', graph_id=graph_id)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')


