import requests
import json

BASE_URL_AUTH = "http://localhost:5001"
BASE_URL_ROUTES = "http://localhost:5002"

def print_response(name, response):
    print(f"--- {name} ---")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print("Response Text (Not JSON):")
        print(response.text)
    print("-" * (len(name) + 8) + "\n")

#ESCENARIO 1: Acceso exitoso de usuario autorizado
print(">>> INICIANDO ESCENARIO 1: ACCESO AUTORIZADO\n")
login_payload = {
    "username": "logistica_user",
    "password": "password123"
}
response_login = requests.post(f"{BASE_URL_AUTH}/login", json=login_payload)
print_response("1.1 - Solicitud de Token", response_login)

access_token = response_login.json().get('access_token')

headers = {
    "Authorization": f"Bearer {access_token}"
}
response_routes_success = requests.get(f"{BASE_URL_ROUTES}/routes", headers=headers)
print_response("1.2 - Acceso a Rutas con Token Válido", response_routes_success)

#ESCENARIO 2: Falla de seguridad - Intento de acceso sin token
print("\n>>> INICIANDO ESCENARIO 2: ACCESO SIN TOKEN\n")
response_no_token = requests.get(f"{BASE_URL_ROUTES}/routes")
print_response("2 - Acceso a Rutas sin Token", response_no_token)

#ESCENARIO 3: Falla de seguridad - Intento de acceso con token inválido
print("\n>>> INICIANDO ESCENARIO 3: ACCESO CON TOKEN INVÁLIDO\n")
invalid_headers = {
    "Authorization": "Bearer tokenfalsificado12345"
}
response_invalid_token = requests.get(f"{BASE_URL_ROUTES}/routes", headers=invalid_headers)
print_response("3 - Acceso a Rutas con Token Inválido", response_invalid_token)

#ESCENARIO 4: Falla de autenticación y notificación
print("\n>>> INICIANDO ESCENARIO 4: FALLO DE LOGIN Y NOTIFICACIÓN\n")
failed_login_payload = {
    "username": "atacante",
    "password": "passworderroneo"
}
response_failed_login = requests.post(f"{BASE_URL_AUTH}/login", json=failed_login_payload)
print_response("4 - Intento de Login con Credenciales Inválidas", response_failed_login)
print("NOTA: Revisar la consola en docker del servicio autorizador para ver la 'ALERTA DE SEGURIDAD'.\n")