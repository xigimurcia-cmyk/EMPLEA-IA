import re

from firebase_admin import auth
from flask import Blueprint, jsonify, redirect, request

from extensions import mysql


empresas_bp = Blueprint("empresas", __name__)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def validar_contrasena(contrasena):
    if len(contrasena) < 8:
        return False, "La contrasena debe tener minimo 8 caracteres"
    if not any(c.isupper() for c in contrasena):
        return False, "La contrasena debe tener al menos una mayuscula"
    if not any(c.isdigit() for c in contrasena):
        return False, "La contrasena debe tener al menos un numero"
    if not any(c in "!@#$%^&*" for c in contrasena):
        return False, "La contrasena debe tener al menos un caracter especial (!@#$%^&*)"
    return True, "OK"


@empresas_bp.route("/api/empresas/registro", methods=["POST"])
def registro_empresa():
    data = request.form if request.form else (request.get_json() or {})

    nombre = data.get("nombre_empresa")
    correo = data.get("correo")
    contrasena = data.get("contrasena")
    telefono = data.get("telefono")

    if not nombre or not correo or not contrasena or not telefono:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    if not re.match(EMAIL_REGEX, correo):
        return jsonify({"error": "El formato del correo electronico no es valido"}), 400

    contrasena_valida, mensaje = validar_contrasena(contrasena)
    if not contrasena_valida:
        return jsonify({"error": mensaje}), 400

    try:
        user = auth.create_user(email=correo, password=contrasena)
        uid = user.uid
    except Exception as e:
        return jsonify({"error": f"Error en Firebase: {str(e)}"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute(
            """
            INSERT INTO usuarios (firebase_uid, correo, tipo)
            VALUES (%s, %s, %s)
            """,
            (uid, correo, "empresa"),
        )
        id_usuario = cur.lastrowid
        cur.execute(
            """
            INSERT INTO empresas (id_usuario, nombre_empresa, telefono)
            VALUES (%s, %s, %s)
            """,
            (id_usuario, nombre, telefono),
        )
        mysql.connection.commit()
        cur.close()
        if request.form:
            return redirect("http://127.0.0.1:5500/empresas/dashboard-empresas.html")
        return jsonify({"mensaje": "Empresa registrada"}), 201
    except Exception as e:
        mysql.connection.rollback()
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

    if request.form:
        return redirect("http://127.0.0.1:5500/empresas/dashboard-empresas.html")

    return jsonify({"mensaje": "Login provisional exitoso"}), 200
