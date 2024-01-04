from flask import Flask, render_template, request, redirect, send_file
import csv
from datetime import datetime
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import base64

app = Flask(__name__)

# Lista para almacenar transacciones
transacciones = []

def generar_grafico():
    # Lógica para obtener estadísticas (puedes ajustar según tus necesidades)
    total_gastado = sum(transaccion['monto'] for transaccion in transacciones)
    categorias = list(set(transaccion['categoria'] for transaccion in transacciones))
    gastos_por_categoria = [sum(transaccion['monto'] for transaccion in transacciones if transaccion['categoria'] == categoria) for categoria in categorias]

    # Crear un gráfico de barras
    fig, ax = plt.subplots()
    ax.bar(categorias, gastos_por_categoria)
    ax.set_xlabel('Categoría')
    ax.set_ylabel('Monto Gastado')
    ax.set_title('Gastos por Categoría')

    # Guardar la imagen del gráfico en un objeto BytesIO
    img = io.BytesIO()
    FigureCanvas(fig).print_png(img)
    img.seek(0)
    plt.close(fig)

    # Codificar la imagen en base64 para mostrarla en HTML
    imagen_base64 = base64.b64encode(img.getvalue()).decode()
    
    return total_gastado, imagen_base64

@app.route('/')
def index():
    return render_template('index.html', transacciones=transacciones)

@app.route('/agregar', methods=['POST'])
def agregar():
    concepto = request.form.get('concepto')
    monto = float(request.form.get('monto'))
    categoria = request.form.get('categoria')

    # Agrega la fecha a la transacción
    fecha = datetime.now()

    transacciones.append({'concepto': concepto, 'monto': monto, 'categoria': categoria, 'fecha': fecha})
    
    return redirect('/')

@app.route('/exportar-csv')
def exportar_csv():
    filename = 'transacciones.csv'
    with open(filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Concepto', 'Monto', 'Categoría', 'Fecha'])
        for transaccion in transacciones:
            csv_writer.writerow([transaccion['concepto'], transaccion['monto'], transaccion['categoria'], transaccion['fecha']])
    return send_file(filename, as_attachment=True)

@app.route('/importar-csv', methods=['POST'])
def importar_csv():
    if 'archivo' not in request.files:
        return redirect('/')
    
    archivo = request.files['archivo']
    
    if archivo.filename == '':
        return redirect('/')
    
    if archivo and archivo.filename.endswith('.csv'):
        # Lógica de importación aquí
        # Puedes utilizar la biblioteca csv para leer el archivo CSV
        # Agrega las transacciones a la lista transacciones
        return redirect('/')
    else:
        return redirect('/')

@app.route('/estadisticas')
def estadisticas():
    total_gastado, imagen_base64 = generar_grafico()
    return render_template('estadisticas.html', total_gastado=total_gastado, imagen_base64=imagen_base64)

@app.route('/editar/<int:index>', methods=['GET', 'POST'])
def editar(index):
    if request.method == 'GET':
        transaccion = transacciones[index]
        return render_template('editar.html', index=index, transaccion=transaccion)
    elif request.method == 'POST':
        # Lógica para actualizar la transacción
        transacciones[index]['concepto'] = request.form.get('concepto')
        transacciones[index]['monto'] = float(request.form.get('monto'))
        transacciones[index]['categoria'] = request.form.get('categoria')
        return redirect('/')

@app.route('/eliminar/<int:index>')
def eliminar(index):
    # Lógica para eliminar la transacción
    del transacciones[index]
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
