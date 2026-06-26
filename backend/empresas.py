from firebase_admin import auth
from flask import Blueprint, jsonify, request

from extensions import mysql


empresas_bp = Blueprint("empresas", __name__)


@empresas_bp.route("/api/empresas/registro", methods=["POST"])
def registro_empresa():
    data = request.get_json() or {}

    nombre = data.get("nombre_empresa")
    correo = data.get("correo")
    contrasena = data.get("contrasena")
    telefono = data.get("telefono")

    if not nombre or not correo or not contrasena or not telefono:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    try:
        user = auth.create_user(email=correo, password=contrasena)
        uid = user.uid
    except Exception as e:
        return jsonify({"error": f"Error en Firebase: {str(e)}"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
            INSERT INTO empresas (firebase_uid, nombre_empresa, correo, telefono)
            VALUES (%s, %s, %s, %s)
            """,
            (uid, nombre, correo, telefono),
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({"mensaje": "Empresa registrada"}), 201
    except Exception as e:
        try:
            auth.delete_user(uid)
        except Exception:
            pass
        return jsonify({"error": "Error en BD: " + str(e)}), 500


@empresas_bp.route("/api/empresas/login", methods=["POST"])
def login_empresa():
    correo = request.form.get("correo")

    if not correo:
        return jsonify({"error": "El correo es obligatorio"}), 400

    try:
        usuario = auth.get_user_by_email(correo)
        return jsonify({"mensaje": "Login exitoso", "uid": usuario.uid}), 200
    except auth.UserNotFoundError:
        return jsonify({"error": "Correo o contrasena incorrectos"}), 401
    except Exception as e:
        return jsonify({"error": f"Error en Firebase: {str(e)}"}), 400
