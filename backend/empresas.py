# Importaciones necesarias para las rutas de empresas
from flask import Blueprint, request, jsonify
from app import mysql
import re

# Blueprint del modulo de empresas
# Xitlaly agrega sus rutas aqui
empresas_bp = Blueprint('empresas', __name__)

# Ruta de registro de empresa
@empresas_bp.route('/api/empresas/registro', methods=['POST'])
def registro_empresa():
    # Por ahorita solo confirma que la ruta funciona
    # Xitlaly agrega la logica aqui
    return jsonify({'mensaje': 'Registro empresa'})