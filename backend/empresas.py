from flask import Blueprint, request, jsonify
from firebase_admin import auth 
from extensions import mysql # Importamos desde el nuevo archivo

empresas_bp = Blueprint('empresas', __name__)


empresas_bp = Blueprint('empresas', __name__)

@empresas_bp.route('/api/empresas/registro', methods=['POST'])
def registro_empresa():
    data = request.get_json() # Recibimos el JSON del frontend
    nombre = data.get('nombre_empresa')
    correo = data.get('correo')
    contrasena = data.get('contrasena')
    telefono = data.get('telefono')

    # Firebase: Crear usuario
    try:
        user = auth.create_user(email=correo, password=contrasena)
        uid = user.uid
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # MySQL: Insertar datos (sin contraseña, solo UID)
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO empresas (id_empresa, nombre_empresa, correo, telefono) VALUES (%s, %s, %s, %s)", 
                    (uid, nombre, correo, telefono))
        mysql.connection.commit()
        cur.close()
        return jsonify({'mensaje': 'Empresa registrada'}), 201
    except Exception as e:
        return jsonify({'error': 'Error en BD: ' + str(e)}), 500