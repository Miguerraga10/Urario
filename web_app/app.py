import os
from flask import Flask, jsonify, request, send_from_directory
from web_app import db, convert
from web_app.generate import generate_schedule
from Metodos.Metodos import extraer_informacion
from Revisa_Materias import cargar_materias_posibles_por_carrera
from flask_cors import CORS

app = Flask(__name__, static_folder='static', static_url_path='/')
CORS(app)

@app.route('/api/materias', methods=['GET'])
def api_get_materias():
    docs = db.get_all_materias()
    return jsonify(docs)

@app.route('/api/materias/manual', methods=['POST'])
def api_add_manual():
    data = request.json or {}
    texto = data.get('texto', '')
    obligatoria = data.get('obligatoria', True)
    universidad = data.get('universidad', 'UNAL')
    if not texto:
        return jsonify({'success': False, 'error': 'Texto vacío'}), 400
    materia = extraer_informacion(texto, obligatoria, universidad)
    if materia is None:
        return jsonify({'success': False, 'error': 'No se pudo extraer la materia'}), 400
    doc = convert.materia_to_dict(materia)
    inserted_id = db.insert_materia(doc)
    return jsonify({'success': True, 'id': inserted_id, 'materia': doc})

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.json or {}
    intervalos = data.get('intervalos', {})
    materias = data.get('materias')
    if materias is None:
        materias = db.get_all_materias()
    # convert any DB ids out
    for m in materias:
        m.pop('id', None)
    result = generate_schedule(materias, intervalos)
    if not result.get('success'):
        return jsonify(result), 400
    return jsonify(result)


@app.route('/api/materias/clear', methods=['POST'])
def api_clear_materias():
    db.clear_materias()
    return jsonify({'success': True})


@app.route('/api/carreras', methods=['GET'])
def api_get_carreras():
    try:
        docs = db.get_all_carreras()
        for d in docs:
            d['id'] = str(d.pop('_id'))
        return jsonify({'success': True, 'carreras': docs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/posibles', methods=['POST'])
def api_posibles():
    data = request.json or {}
    nombre_carrera = data.get('carrera')
    materias_vistas = data.get('materias_vistas', [])
    if not nombre_carrera:
        return jsonify({'success': False, 'error': 'Falta nombre de la carrera'}), 400
    posibles, fuente = cargar_materias_posibles_por_carrera(nombre_carrera, materias_vistas)
    if posibles is None:
        return jsonify({'success': False, 'error': 'No se pudieron obtener materias posibles para la carrera'}), 404
    return jsonify({'success': True, 'posibles': posibles, 'fuente': str(fuente)})


@app.route('/api/carreras/upload', methods=['POST'])
def api_upload_carreras():
    docs = request.json or []
    if not isinstance(docs, list):
        return jsonify({'success': False, 'error': 'Payload inválido, se espera lista'}), 400
    try:
        db.insert_carreras(docs)
        return jsonify({'success': True, 'inserted': len(docs)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '5000'))
    app.run(host=host, port=port, debug=True)
