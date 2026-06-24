# Importaciones necesarias para las rutas de candidatos
from flask import Blueprint, request, jsonify, current_app
from flask_mysqldb import MySQL
import re

# Blueprint del modulo de candidatos
candidatos_bp = Blueprint('candidatos', __name__)

# Ruta de registro de candidato
@candidatos_bp.route('/api/candidatos/registro', methods=['POST'])
def registro_candidato():
    # Por ahorita solo confirma que la ruta funciona
    # Itzel agrega la logica aqui
    return jsonify({'mensaje': 'Registro candidato'})