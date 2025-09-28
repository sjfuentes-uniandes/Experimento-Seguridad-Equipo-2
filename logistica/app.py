from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, JWTManager
import os
import datetime
import json

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-key-change-it")
api = Api(app)
jwt = JWTManager(app)

TRUCK_ROUTES = [
    {"id": 1, "truck": "T-01", "destination": "Bodega Central", "route": ["Calle 1", "Av. Principal", "Zona Industrial"]},
    {"id": 2, "truck": "T-02", "destination": "Punto de Entrega Norte", "route": ["Autopista Norte", "Calle 127"]}
]

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

class RouteResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get("role")
        if user_role == "logistics":
            writeLog("AUDIT", "Logistica", "Acceso a rutas concedido")
            return jsonify(routes=TRUCK_ROUTES)
        else:
            writeLog("ALERTA", "Logistica", "Acceso DENEGADO por intento con rol no autorizado", f"Intento de acceso por rol {user_role}")
            return {"msg": "Acceso no autorizado para este rol"}, 403

api.add_resource(RouteResource, '/routes')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)