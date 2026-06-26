import os

import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from extensions import mysql


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
CORS(app)

app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "localhost")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "emplea_ia")

mysql.init_app(app)

if not firebase_admin._apps:
    service_account_path = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT",
        os.path.join(BASE_DIR, "serviceAccountKey.json"),
    )
    if not os.path.isabs(service_account_path):
        service_account_path = os.path.join(BASE_DIR, service_account_path)
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

from candidatos import candidatos_bp
from empresas import empresas_bp

app.register_blueprint(candidatos_bp)
app.register_blueprint(empresas_bp)

if __name__ == "__main__":
    app.run(debug=True)
