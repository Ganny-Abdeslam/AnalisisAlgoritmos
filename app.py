from flask import Flask, render_template, make_response
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('html/index.html')  # La página principal de la app

@app.route('/plot.png')
def plot_png():
    # Crear el gráfico
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
    ax.set_title('Ejemplo de gráfico con Flask y Matplotlib')

    # Guardar el gráfico en un objeto BytesIO
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    
    # Devolver la imagen generada en formato PNG
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

if __name__ == '__main__':
    app.run(debug=True)