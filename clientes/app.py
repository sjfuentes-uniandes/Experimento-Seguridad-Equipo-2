from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

AUTHORIZER_URL = "http://autorizador:5002/auth"

CLIENTES = [
    {"id": 1, "nombre": "Carlos"},
    {"id": 2, "nombre": "Nicolas"},
    {"id": 3, "nombre": "Santiago"}
]

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    if not data or "usuario" not in data or "contrasena" not in data:
        return jsonify({"error": "Faltan credenciales"}), 400

    try:
        response = requests.post(AUTHORIZER_URL, json=data)
        if response.status_code == 200:
            token = response.json().get("token")
            return jsonify({"token": token}), 200
        else:
            return jsonify({"error": "Credenciales inválidas"}), 401
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "No se pudo conectar al autorizador"}), 500
    
@app.route("/clientes", methods=["GET"])
def get_clientes():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token requerido"}), 401

    try:
        response = requests.post("http://localhost:5002/verify", headers={"Authorization": token})
        if response.status_code != 200:
            return jsonify({"error": "Token inválido"}), 403
    except requests.exceptions.RequestException:
        return jsonify({"error": "No se pudo contactar al autorizador"}), 500

    return jsonify(CLIENTES), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
