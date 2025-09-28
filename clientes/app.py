from flask import Flask, request, jsonify
import requests
import os
import time, datetime
import json

app = Flask(__name__)

# URLs de los servicios
AUTH_URL = os.environ.get("AUTH_URL", "http://servicio_autorizador:5000/login")
LOGISTICS_URL = os.environ.get("LOGISTICS_URL", "http://servicio_logistica:5000/routes")

# Tiempo máximo de respuesta a las solicitudes
MAX_RESPONSE_TIME_MS = 500

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


@app.route('/get_routes', methods=['POST'])
def get_routes():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    # Tiempo inicial de la solicitud
    time_i = time.time()

    try:
        auth_response = requests.post(AUTH_URL, json={"username": username, "password": password})
    except requests.exceptions.RequestException as e:
        writeLog("ERROR", "Clientes", "Error al comunicarse con el autorizador", f"{e}")
        return jsonify({"msg": f"Error al comunicarse con el autorizador: {e}"}), 500
    
    # Duracion de la solicitud
    delta_time = (time.time() - time_i)*1000

    if auth_response.status_code != 200:
        writeLog("ALERT", "Clientes", "Autenticación fallida")
        return jsonify({"msg": "Autenticación fallida", "details": auth_response.json()}), auth_response.status_code

    if delta_time > MAX_RESPONSE_TIME_MS:
        writeLog("ALERT", "Clientes", f"Retardo en los mensajes detectado! Duración de la solicitud con el autorizador: {delta_time}ms", "Sistema bajo posible ataque")
        return jsonify({"msg": f"Retardo en los mensajes detectado! Duración de la solicitud con el autorizador: {delta_time}ms. Sistema bajo posible ataque"})

    access_token = auth_response.json().get("access_token")
    if not access_token:
        writeLog("AUDIT", "Clientes", "No se recibió token del autorizador")
        return jsonify({"msg": "No se recibió token del autorizador"}), 500

    headers = {"Authorization": f"Bearer {access_token}"}

    # Tiempo inicial
    time_i = time.time()

    try:
        logistics_response = requests.get(LOGISTICS_URL, headers=headers)
    except requests.exceptions.RequestException as e:
        writeLog("ERROR", "Clientes", "Error al comunicarse con logística", f"{e}")
        return jsonify({"msg": f"Error al comunicarse con logística: {e}"}), 500

    # Duracion de la solicitud
    delta_time = (time.time() - time_i)*1000

    if delta_time > MAX_RESPONSE_TIME_MS:
        writeLog("ALERT", "Clientes", f"Retardo en los mensajes detectado! Duración de la solicitud con logística: {delta_time}ms", "Sistema bajo posible ataque")
        return jsonify({"msg": f"Retardo en los mensajes detectado! Duración de la solicitud con logística: {delta_time}ms. Sistema bajo posible ataque"})

    if logistics_response.status_code == 200:
        writeLog("AUDIT", "Clientes", "Accediendo a la información de las rutas")
        return jsonify(logistics_response.json()), 200
    elif logistics_response.status_code == 403:
        writeLog("ALERT", "Clientes", "Acceso no autorizado al servicio de logistica", f"Sistema bajo posible ataque, acceso no autorizado por el ususario por el ususario '{username}'")
        print(f"ALERTA: Acceso no autorizado al servicio de logística por el usuario '{username}'", flush=True)
        return jsonify({"msg": "Acceso no autorizado"}), 403
    else:
        writeLog("ERROR", "Clientes", "Error inesperado en logística", f"{logistics_response.text}")
        return jsonify({"msg": "Error inesperado en logística", "details": logistics_response.text}), logistics_response.status_code


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
