from flask import Flask, render_template, make_response, url_for
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__, static_folder='images')

@app.route('/')
def index():
    # Lista de tarjetas con toda la información necesaria
    cards = [
        {
            "title": f"Gráfico {i}",
            "description": f"Descripción breve del gráfico {i}.",
            "graph_id": i,
            "image_url": url_for('static', filename=f'grafico{i}.png')  # Usa static/images para las rutas de las imágenes
        }
        for i in range(1, 16)  # Crea 15 tarjetas
    ]
    return render_template('index.html', cards=cards)

@app.route('/grafico/<int:graph_id>')
def plot_page(graph_id):
    # Aquí defines la lógica para mostrar la página individual con la gráfica
    return render_template('plot.html', graph_id=graph_id)

if __name__ == '__main__':
    app.run(debug=True)