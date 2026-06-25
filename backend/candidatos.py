from flask import Blueprint, request, jsonify
from flask_mysqldb import MySQL
import re
from firebase_admin import auth

candidatos_bp = Blueprint('candidatos', __name__)

# Expresión regular para validar formato de correo
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

@candidatos_bp.route('/api/candidatos/registro', methods=['POST'])
def registro_candidato():
    try:
        # 1. Recibir datos del formulario (JSON)
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se proporcionaron datos'}), 400
            
        nombre = data.get('nombre')
        correo = data.get('correo')
        contrasena = data.get('contrasena')
        
        # Validar campos vacíos
        if not nombre or not correo or not contrasena:
            return jsonify({'error': 'Todos los campos son obligatorios'}), 400
            
        # 2. Validar correo electrónico
        if not re.match(EMAIL_REGEX, correo):
            return jsonify({'error': 'El formato del correo electrónico no es válido'}), 400
            
        # 3. Validar contraseña (Mínimo 8 caracteres, letras y números)
        if len(contrasena) < 8 or not any(c.isdigit() for c in contrasena) or not any(c.isalpha() for c in contrasena):
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres, incluyendo letras y números'}), 400

        # 4. Crear usuario en Firebase Authentication
        try:
            user_firebase = auth.create_user(
                email=correo,
                password=contrasena,
                display_name=nombre
            )
            firebase_uid = user_firebase.uid
        except Exception as firebase_err:
            return jsonify({'error': f'Error en Firebase: {str(firebase_err)}'}), 400

        # 5. Guardar datos en MySQL (Workbench)
        from app import mysql  # Importación local para evitar el error de importación circular
        cur = mysql.connection.cursor()
        
        # Usamos id_candidato para guardar el UID de Firebase y agregamos contrasena
        query = """
            INSERT INTO candidatos (id_candidato, nombre, correo, contrasena) 
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (firebase_uid, nombre, correo, contrasena))
        mysql.connection.commit()
        cur.close()

        return jsonify({
            'mensaje': 'Registro candidato exitoso',
            'uid_firebase': firebase_uid
        }), 201

    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500