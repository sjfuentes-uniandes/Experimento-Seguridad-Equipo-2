from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, JWTManager
import os

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "super-secret-key-change-it")
api = Api(app)
jwt = JWTManager(app)

TRUCK_ROUTES = [
    {"id": 1, "truck": "T-01", "destination": "Bodega Central", "route": ["Calle 1", "Av. Principal", "Zona Industrial"]},
    {"id": 2, "truck": "T-02", "destination": "Punto de Entrega Norte", "route": ["Autopista Norte", "Calle 127"]}
]

class RouteResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        claims = get_jwt()
        if claims.get("role") == "logistics":
            return jsonify(routes=TRUCK_ROUTES)
        else:
            return {"msg": "Acceso no autorizado para este rol"}, 403

api.add_resource(RouteResource, '/routes')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)