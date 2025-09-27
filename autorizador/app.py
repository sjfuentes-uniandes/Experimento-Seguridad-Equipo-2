from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager
import datetime
import os

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-key-change-it")
jwt = JWTManager(app)

AUTHORIZED_USERS = {
    "logistica_user": {
        "password": "password123",
        "role": "logistics"
    },
    "invitado_user": {
        "password": "inv123",
        "role": "guest"
    }
}

def notify_admin(username):
    print(f"ALERTA DE SEGURIDAD: Intento de inicio de sesión fallido para el usuario '{username}'.",flush=True)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', None)
    password = data.get('password', None)

    user = AUTHORIZED_USERS.get(username)

    if user and user["password"] == password:
        access_token = create_access_token(
            identity=username,
            additional_claims={"role": user["role"]},
            expires_delta=datetime.timedelta(minutes=15)
        )
        return jsonify(access_token=access_token), 200
    else:
        notify_admin(username)
        return jsonify({"msg": "Credenciales incorrectas"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)