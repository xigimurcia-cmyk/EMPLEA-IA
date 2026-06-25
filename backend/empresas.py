# Importaciones necesarias para las rutas de empresas
from flask import Blueprint, request, jsonify
from flask_mail import Message  # Para mandar correos
from firebase_admin import auth  # Firebase para autenticacion
import re  # Para expresiones regulares (validar correo)

# Blueprint del modulo de empresas
# Un Blueprint es un modulo de rutas separado que se registra en app.py
empresas_bp = Blueprint('empresas', __name__)

# ---- VALIDACIONES ----

# Valida que el correo tenga formato correcto
# Ejemplo valido: empresa@gmail.com
# Ejemplo invalido: empresagmail.com
def validar_correo(correo):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo)

# Valida que la contrasena sea segura
# Debe tener minimo 8 caracteres, una mayuscula, un numero y un caracter especial
def validar_contrasena(contrasena):
    # Verificar longitud minima
    if len(contrasena) < 8:
        return False, 'La contrasena debe tener minimo 8 caracteres'
    # Verificar que tenga al menos una mayuscula
    if not any(c.isupper() for c in contrasena):
        return False, 'Debe tener al menos una letra mayuscula'
    # Verificar que tenga al menos un numero
    if not any(c.isdigit() for c in contrasena):
        return False, 'Debe tener al menos un numero'
    # Verificar que tenga al menos un caracter especial
    if not any(c in '!@#$%^&*' for c in contrasena):
        return False, 'Debe tener al menos un caracter especial (!@#$%^&*)'
    # Si pasa todas las validaciones, la contrasena es valida
    return True, 'OK'

# ---- RUTAS ----

# Ruta para registrar una empresa nueva
# Metodo POST porque estamos enviando datos del formulario
@empresas_bp.route('/api/empresas/registro', methods=['POST'])
def registro_empresa():
    # Importar mysql y mail desde app para evitar importacion circular
    from app import mysql, mail

    # Obtener los datos que mando el formulario HTML
    nombre_empresa = request.form['nombre_empresa']
    correo = request.form['correo']
    contrasena = request.form['contrasena']
    telefono = request.form['telefono']

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
    cursor.execute('INSERT INTO empresas (nombre_empresa, correo, contrasena, telefono) VALUES (%s, %s, %s, %s)',
                   (nombre_empresa, correo, contrasena, telefono))
    mysql.connection.commit()  # Confirmar los cambios en la base de datos
    cursor.close()  # Cerrar la conexion

    # Mandar correo de verificacion al usuario
    # Si falla el correo, el registro igual se guarda
    try:
        # Generar link de verificacion con Firebase
        link = auth.generate_email_verification_link(correo)
        # Crear el mensaje de correo
        msg = Message(
            'Verifica tu correo - EMPLEA IA',
            sender='empleaiaflask@gmail.com',
            recipients=[correo]
        )
        # Contenido del correo
        msg.body = f'Hola {nombre_empresa}, verifica tu correo dando clic aqui: {link}'
        # Mandar el correo
        mail.send(msg)
    except Exception as e:
        # Si hay error al mandar el correo, solo lo imprime pero no falla el registro
        print(f'Error al mandar correo: {e}')

    # Responder que el registro fue exitoso
    return jsonify({'mensaje': 'Empresa registrada exitosamente! Revisa tu correo para verificar tu cuenta'}), 201

# Ruta para login de empresa
# Verifica que el correo exista en Firebase
@empresas_bp.route('/api/empresas/login', methods=['POST'])
def login_empresa():
    # Obtener los datos del formulario
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