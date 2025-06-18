# backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify, session, redirect, url_for
import logging
from backend.controllers.auth_controller import AuthController

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth_api', __name__)

_auth_controller: AuthController = None

def init_auth_routes(controller: AuthController):
    """
    Función para inicializar las rutas de autenticación con el controlador adecuado.
    """
    global _auth_controller
    _auth_controller = controller
    logger.info("Rutas de autenticación inicializadas con el controlador.")

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint para el registro de usuarios.
    """
    logger.info("Petición POST recibida en /api/register")
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if not email or not password or not confirm_password:
        return jsonify({'message': 'Todos los campos son requeridos.'}), 400

    if password != confirm_password:
        return jsonify({'message': 'Las contraseñas no coinciden.'}), 400

    result = _auth_controller.register_user(email, password)
    if result and result.get('message') == 'Registro exitoso. Ahora puedes iniciar sesión.':
        return jsonify(result), 201
    else:
        return jsonify(result), 409 # Conflicto si el email ya existe, u otro error

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint para el inicio de sesión de usuarios.
    """
    logger.info("Petición POST recibida en /api/login")
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return jsonify({'message': 'Email y contraseña son requeridos.'}), 400

    result = _auth_controller.login_user(email, password)
    if result and result.get('message') == 'Inicio de sesión exitoso.':
        return jsonify(result), 200
    else:
        return jsonify(result), 401 # No autorizado

@auth_bp.route('/auth/google/callback', methods=['GET', 'POST'])
def google_callback():
    """
    Endpoint de callback para la autenticación de Google OAuth.
    Este endpoint es alcanzado por la redirección de Google o por la petición JS del frontend.
    """
    logger.info("Petición recibida en /api/auth/google/callback")
    
    # El 'code' viene del request.args (para GET directo de Google) o request.form (para POST de JS)
    code = request.args.get('code') or request.form.get('code')

    if not code:
        logger.warning("No se recibió el código de Google en el callback.")
        return jsonify({'message': 'No se recibió el código de Google.'}), 400

    # Pasa el code directamente al controlador
    user_info = _auth_controller.handle_google_callback(code=code) 
    
    if user_info:
        # Aquí el controlador ya maneja la sesión
        return jsonify({'message': 'Autenticación con Google exitosa.', 'user': user_info}), 200
    else:
        logger.error("Error al procesar el callback de Google en el controlador.")
        return jsonify({'message': 'Error al procesar el callback de Google'}), 401

