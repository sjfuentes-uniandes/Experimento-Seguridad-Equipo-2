from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# URLs de los servicios
AUTH_URL = os.environ.get("AUTH_URL", "http://servicio_autorizador:5000/login")
LOGISTICS_URL = os.environ.get("LOGISTICS_URL", "http://servicio_logistica:5000/routes")


@app.route('/get_routes', methods=['POST'])
def get_routes():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    try:
        auth_response = requests.post(AUTH_URL, json={"username": username, "password": password})
    except requests.exceptions.RequestException as e:
        return jsonify({"msg": f"Error al comunicarse con el autorizador: {e}"}), 500

    if auth_response.status_code != 200:
        return jsonify({"msg": "Autenticación fallida", "details": auth_response.json()}), auth_response.status_code

    access_token = auth_response.json().get("access_token")
    if not access_token:
        return jsonify({"msg": "No se recibió token del autorizador"}), 500

    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        logistics_response = requests.get(LOGISTICS_URL, headers=headers)
    except requests.exceptions.RequestException as e:
        return jsonify({"msg": f"Error al comunicarse con logística: {e}"}), 500

    if logistics_response.status_code == 200:
        return jsonify(logistics_response.json()), 200
    elif logistics_response.status_code == 403:
        print(f"ALERTA: Acceso no autorizado al servicio de logística por el usuario '{username}'", flush=True)
        return jsonify({"msg": "Acceso no autorizado"}), 403
    else:
        return jsonify({"msg": "Error inesperado en logística", "details": logistics_response.text}), logistics_response.status_code


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
