# Importaciones principales
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mysqldb import MySQL
from flask_mail import Mail
import firebase_admin
from firebase_admin import credentials, auth

# Crear la aplicacion Flask
app = Flask(__name__)

# ---- CONFIGURACION DE JWT ----
# JWT maneja la autenticacion con tokens
app.config['JWT_SECRET_KEY'] = 'emplea-ia-secret-key'
jwt = JWTManager(app)

# ---- CONFIGURACION DE MYSQL ----
# Cambia TU_CONTRASENA_MYSQL por tu contrasena de MySQL Workbench
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'TU_CONTRASENA_MYSQL'
app.config['MYSQL_DB'] = 'emplea_ia'
# DictCursor permite acceder a los datos por nombre en lugar de por posicion
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# ---- CONFIGURACION DE FIREBASE ----
if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

# ---- CONFIGURACION DE FLASK-MAIL ----
# Se usa para mandar correos de verificacion a los usuarios
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'empleaiaflask@gmail.com'
app.config['MAIL_PASSWORD'] = 'TU_CONTRASENA_APLICACION'
mail = Mail(app)

# ---- IMPORTAR RUTAS ----
# Cada modulo tiene sus propias rutas separadas
from candidatos import candidatos_bp  # rutas de Itzel
from empresas import empresas_bp      # rutas de Xitlaly

# Registrar los modulos en la app
app.register_blueprint(candidatos_bp)
app.register_blueprint(empresas_bp)

# Arrancar el servidor
if __name__ == '__main__':
    app.run(debug=True)