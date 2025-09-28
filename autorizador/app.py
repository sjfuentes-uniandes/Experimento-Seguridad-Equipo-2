from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, JWTManager
import datetime, time
import os
import json

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

LOG_FILE = "/app/event_log.txt"

def writeLog(event_type, source, message, details=None):
    timestamp = datetime.datetime.now().isoformat()
    log = {
        "timestamp": timestamp,
        "type": event_type,
        "source": source,
        "message": message,
        "details": details if details else {}
    }
    try:
        with open(LOG_FILE, 'a') as file:
            file.write(json.dumps(log) + '\n')
    except Exception as e:
        print(f"ERROR ESCRITURA: No fue posible escribir en el archivo del log {LOG_FILE}: {e}", flush=True)

def notify_admin(username):
    writeLog("ALERT", "Autorizador", "Intento de inicio de sesion fallido", f"Intento realizado por el ususario {username}")
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
        writeLog("AUDIT", "Autorizador", "Token de acceso concedido", f"Token concedido al usuario {username}")
        return jsonify(access_token=access_token), 200
    else:
        notify_admin(username)
        writeLog("ALERT", "Autorizador", "Credenciales incorrectas", f"Token denegado al usuario {username}")
        return jsonify({"msg": "Credenciales incorrectas"}), 401


# Metodo con login tardío simulado
@app.route('/slow_login', methods=['POST'])
def slow_login():
    LAG_TIME = 1
    
    print(f"SIMULACIÓN: Retardo excesivo activo. Pausando por {LAG_TIME} segundos...", flush=True)
    time.sleep(LAG_TIME) 
    
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
        writeLog("AUDIT", "Autorizador", "Token de acceso concedido con retardo simulado", f"Retardo simulado. Token concedido al usuario {username}")
        return jsonify(access_token=access_token), 200
    else:
        writeLog("ALERT", "Autorizador", "Credenciales incorrectas", f"Token denegado al usuario {username}")
        return jsonify({"msg": "Credenciales incorrectas"}), 401
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)