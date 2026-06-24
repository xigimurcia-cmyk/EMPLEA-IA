# Importaciones necesarias para las rutas de empresas
from flask import Blueprint, request, jsonify
from firebase_admin import auth  # Firebase para autenticacion
import re  # Para expresiones regulares (validar correo)

# Blueprint del modulo de empresas
# Un Blueprint es un modulo de rutas separado que se registra en app.py
empresas_bp = Blueprint('empresas', __name__)

# VALIDACIONES

# Valida que el correo tenga formato correcto
# Ejemplo valido: empresa@gmail.com
# Ejemplo invalido: empresagmail.com
def validar_correo(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo)

# Valida que la contrasena sea segura
# Debe tener minimo 8 caracteres, una mayuscula, un numero y un caracter especial
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
# Metodo POST estamos enviando datos del formulario
@empresas_bp.route('/api/empresas/registro', methods=['POST'])
def registro_empresa():

    from app import mysql

    # Obtener los datos que mando el formulario HTML
    nombre_empresa = request.form['nombre_empresa']
    correo = request.form['correo']
    contrasena = request.form['contrasena']

    # Validar que el correo tenga formato correcto
    if not validar_correo(correo):
        return jsonify({'error': 'El correo no tiene formato valido'}), 400

    # Validar que la contrasena cumpla los requisitos
    valida, mensaje = validar_contrasena(contrasena)
    if not valida:
        return jsonify({'error': mensaje}), 400

    # Registrar el usuario en Firebase Authentication
    # Si el correo ya existe, Firebase lanza un error
    try:
        usuario_firebase = auth.create_user(email=correo, password=contrasena)
    except auth.EmailAlreadyExistsError:
        return jsonify({'error': 'Este correo ya esta registrado'}), 400

    # Guardar los datos de la empresa en MySQL
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO empresas (nombre_empresa, correo, contrasena) VALUES (%s, %s, %s)',
                   (nombre_empresa, correo, contrasena))
    mysql.connection.commit()  # Confirmar los cambios en la base de datos
    cursor.close()  # Cerrar la conexion

    # Responder que el registro fue exitoso
    return jsonify({'mensaje': 'Empresa registrada exitosamente'}), 201

# Ruta para login de empresa
# Verifica que el correo exista en Firebase
@empresas_bp.route('/api/empresas/login', methods=['POST'])
def login_empresa():
    
    correo = request.form['correo']
    contrasena = request.form['contrasena']

    # Buscar el usuario en Firebase por correo
    # Si no existe, Firebase lanza un error
    try:
        usuario = auth.get_user_by_email(correo)
    except auth.UserNotFoundError:
        return jsonify({'error': 'Correo o contrasena incorrectos'}), 401

    # Si existe, login exitoso y regresa el uid del usuario
    return jsonify({'mensaje': 'Login exitoso', 'uid': usuario.uid}), 200