# Importaciones necesarias para las rutas de empresas
from flask import Blueprint, request, jsonify
from firebase_admin import auth  # Firebase para autenticacion
import re  # Para expresiones regulares (validar correo)

# Blueprint del modulo de empresas
empresas_bp = Blueprint('empresas', __name__)

# ---- VALIDACIONES ----

# Valida que el correo tenga formato correcto
def validar_correo(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo)

# Valida que la contrasena sea segura
def validar_contrasena(contrasena):
    if len(contrasena) < 8:
        return False, 'La contrasena debe tener minimo 8 caracteres'
    if not any(c.isupper() for c in contrasena):
        return False, 'Debe tener al menos una letra mayuscula'
    if not any(c.isdigit() for c in contrasena):
        return False, 'Debe tener al menos un numero'
    if not any(c in '!@#$%^&*' for c in contrasena):
        return False, 'Debe tener al menos un caracter especial (!@#$%^&*)'
    return True, 'OK'

# ---- RUTAS ----

# Ruta para registrar una empresa nueva
@empresas_bp.route('/api/empresas/registro', methods=['POST'])
def registro_empresa():
    from app import mysql

    nombre_empresa = request.form['nombre_empresa']
    correo = request.form['correo']
    contrasena = request.form['contrasena']
    telefono = request.form['telefono']

    if not validar_correo(correo):
        return jsonify({'error': 'El correo no tiene formato valido'}), 400

    valida, mensaje = validar_contrasena(contrasena)
    if not valida:
        return jsonify({'error': mensaje}), 400

    try:
        usuario_firebase = auth.create_user(email=correo, password=contrasena)
    except auth.EmailAlreadyExistsError:
        return jsonify({'error': 'Este correo ya esta registrado'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO empresas (nombre_empresa, correo, contrasena, telefono) VALUES (%s, %s, %s, %s)',
                   (nombre_empresa, correo, contrasena, telefono))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'mensaje': 'Empresa registrada exitosamente'}), 201

# Ruta para login de empresa
@empresas_bp.route('/api/empresas/login', methods=['POST'])
def login_empresa():
    correo = request.form['correo']
    contrasena = request.form['contrasena']

    try:
        usuario = auth.get_user_by_email(correo)
    except auth.UserNotFoundError:
        return jsonify({'error': 'Correo o contrasena incorrectos'}), 401

    return jsonify({'mensaje': 'Login exitoso', 'uid': usuario.uid}), 200