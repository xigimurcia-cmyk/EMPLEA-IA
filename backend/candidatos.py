import re

from firebase_admin import auth
from flask import Blueprint, jsonify, request

from extensions import mysql


candidatos_bp = Blueprint("candidatos", __name__)

EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


@candidatos_bp.route("/api/candidatos/registro", methods=["POST"])
def registro_candidato():
    try:
        data = request.get_json() or {}

        nombre = data.get("nombre")
        correo = data.get("correo")
        contrasena = data.get("contrasena")

        if not nombre or not correo or not contrasena:
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        if not re.match(EMAIL_REGEX, correo):
            return jsonify({"error": "El formato del correo electronico no es valido"}), 400

        if (
            len(contrasena) < 8
            or not any(c.isdigit() for c in contrasena)
            or not any(c.isalpha() for c in contrasena)
        ):
            return jsonify(
                {
                    "error": (
                        "La contrasena debe tener al menos 8 caracteres, "
                        "incluyendo letras y numeros"
                    )
                }
            ), 400

        try:
            user_firebase = auth.create_user(
                email=correo,
                password=contrasena,
                display_name=nombre,
            )
            firebase_uid = user_firebase.uid
        except Exception as firebase_err:
            return jsonify({"error": f"Error en Firebase: {str(firebase_err)}"}), 400

        cur = mysql.connection.cursor()
        cur.execute(
            """
            INSERT INTO candidatos (firebase_uid, nombre, correo)
            VALUES (%s, %s, %s)
            """,
            (firebase_uid, nombre, correo),
        )
        mysql.connection.commit()
        cur.close()

        return jsonify(
            {
                "mensaje": "Registro candidato exitoso",
                "uid_firebase": firebase_uid,
            }
        ), 201

    except Exception as e:
        if "firebase_uid" in locals():
            try:
                auth.delete_user(firebase_uid)
            except Exception:
                pass
        return jsonify({"error": f"Error interno: {str(e)}"}), 500
