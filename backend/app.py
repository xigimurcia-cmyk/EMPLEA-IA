from flask import Flask
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from extensions import mysql

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '489350'
app.config['MYSQL_DB'] = 'emplea_ia'

mysql.init_app(app) # Inicializamos aquí

# Ahora importamos los módulos
from candidatos import candidatos_bp
from empresas import empresas_bp

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

app.register_blueprint(candidatos_bp)
app.register_blueprint(empresas_bp)

if __name__ == '__main__':
    app.run(debug=True)