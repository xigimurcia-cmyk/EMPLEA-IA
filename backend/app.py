from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from flask_mysqldb import MySQL
import re

app = Flask(__name__)

# Configuracion de JWT
app.config['JWT_SECRET_KEY'] = 'emplea-ia-secret-key'
jwt = JWTManager(app)

# Configuracion de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'TU_CONTRASENA_MYSQL'
app.config['MYSQL_DB'] = 'emplea_ia'
mysql = MySQL(app)

if __name__ == '__main__':
    app.run(debug=True)