from flask import Flask, render_template, jsonify, request
from datos_iniciales import salones, cursos, bloques_de_tiempo
from gestion_asignaciones import asignar_salon

app = Flask(__name__)

# Ruta para cargar la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para obtener los datos de salones
@app.route('/api/salones')
def get_salones():
    salones_formateados = []
    for salon in salones:
        salon_info = {
            'id': salon['id'],
            'capacidad': salon['capacidad'],
            'equipos': salon['equipos'],
            'disponibilidad': salon.get('disponibilidad', 'Disponible')  # Ajusta según la estructura de `salon`
        }
        salones_formateados.append(salon_info)
    return jsonify(salones_formateados)


# Ruta para obtener los datos de cursos
@app.route('/api/cursos')
def get_cursos():
    return jsonify(cursos)

# Ruta para obtener los bloques de tiempo
@app.route('/api/bloques')
def get_bloques():
    bloques_formateados = [str(bloque) for bloque in bloques_de_tiempo]  # Convierte a texto cada bloque
    return jsonify(bloques_formateados)


# Ruta para asignar curso a un salón
@app.route('/api/asignar', methods=['POST'])
def asignar():
    data = request.json
    curso_id = data.get('curso_id')
    bloque = data.get('bloque')
    asignar_salon(curso_id, bloque)
    return jsonify({"message": "Curso asignado"}), 200

if __name__ == '__main__':
    app.run(debug=True)
