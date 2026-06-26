import re

from firebase_admin import auth
from flask import Blueprint, jsonify, redirect, request

from extensions import mysql


candidatos_bp = Blueprint("candidatos", __name__)

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


@candidatos_bp.route("/api/candidatos/registro", methods=["POST"])
def registro_candidato():
    try:
        data = request.form if request.form else (request.get_json() or {})

        nombre = data.get("nombre")
        apellido = data.get("apellido")
        correo = data.get("correo")
        contrasena = data.get("contrasena")
        confirmar_contrasena = data.get("confirmar_contrasena")
        telefono = data.get("telefono")

        if not nombre or not correo or not contrasena:
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        if confirmar_contrasena and contrasena != confirmar_contrasena:
            return jsonify({"error": "Las contrasenas no coinciden"}), 400

        if not re.match(EMAIL_REGEX, correo):
            return jsonify({"error": "El formato del correo electronico no es valido"}), 400

        contrasena_valida, mensaje = validar_contrasena(contrasena)
        if not contrasena_valida:
            return jsonify({"error": mensaje}), 400

        try:
            user_firebase = auth.create_user(
                email=correo,
                password=contrasena,
                display_name=f"{nombre} {apellido or ''}".strip(),
            )
            firebase_uid = user_firebase.uid
        except Exception as firebase_err:
            return jsonify({"error": f"Error en Firebase: {str(firebase_err)}"}), 400

        cur = mysql.connection.cursor()
        cur.execute(
            """
            INSERT INTO usuarios (firebase_uid, correo, tipo)
            VALUES (%s, %s, %s)
            """,
            (firebase_uid, correo, "candidato"),
        )
        id_usuario = cur.lastrowid
        cur.execute(
            """
            INSERT INTO candidatos (id_usuario, nombre, apellido, telefono)
            VALUES (%s, %s, %s, %s)
            """,
            (id_usuario, nombre, apellido, telefono),
        )
        mysql.connection.commit()
        cur.close()

        if request.form:
            return redirect("http://127.0.0.1:5500/candidatos/dashboard.html")

        return jsonify(
            {
                "mensaje": "Registro candidato exitoso",
                "uid_firebase": firebase_uid,
            }
        ), 201

    except Exception as e:
        mysql.connection.rollback()
        if "firebase_uid" in locals():
            try:
                auth.delete_user(firebase_uid)
            except Exception:
                pass
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
