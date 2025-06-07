# backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, session
import logging

# Importamos el controlador que será inyectado
from backend.controllers.auth_controller import AuthController

logger = logging.getLogger(__name__) # Inicializamos el logger para este módulo

# Creamos un Blueprint para las rutas de autenticación.
# El nombre 'auth_api' se usará para referenciar estas rutas.
auth_bp = Blueprint('auth_api', __name__)

# Esta variable global será asignada desde app.py para inyectar el controlador.
# Es un patrón simple para inyección de dependencias en Flask con Blueprints.
_auth_controller: AuthController = None

def init_auth_routes(controller: AuthController):
    """
    Función para inicializar las rutas de autenticación con el controlador adecuado.
    Esta función será llamada desde app.py para inyectar la instancia de AuthController.
    Sigue el principio de Inversión de Dependencias (DIP).
    """
    global _auth_controller
    _auth_controller = controller
    logger.info("Rutas de autenticación inicializadas con el controlador.")

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint para el inicio de sesión de usuarios.
    Recibe email y contraseña, los valida y gestiona la sesión.
    """
    logger.info("Petición POST recibida en /api/login")
    # Verificación para asegurarse de que el controlador ha sido inicializado
    if not _auth_controller:
        logger.error("Controlador de autenticación no inicializado en /api/login")
        return jsonify({'message': 'Error interno del servidor: controlador no inicializado'}), 500

    data = request.form # Los datos vienen del formulario HTML
    email = data.get('email')
    password = data.get('password')

    # Validación básica de entrada
    if not email or not password:
        logger.warning("Intento de login con campos faltantes.")
        return jsonify({'message': 'Faltan email o contraseña'}), 400

    # Llamamos al método del controlador para la lógica de negocio
    user_info = _auth_controller.login_user(email, password)

    if user_info:
        logger.info(f"Login exitoso para {email}")
        # El controlador ya establece la sesión de Flask
        return jsonify({'message': 'Inicio de sesión exitoso', 'user': user_info}), 200
    else:
        logger.warning(f"Login fallido para {email}: credenciales inválidas.")
        return jsonify({'message': 'Credenciales inválidas'}), 401

@auth_bp.route('/auth/google/callback', methods=['GET', 'POST'])
def google_callback():
    """
    Endpoint para manejar el callback de autenticación de Google OAuth 2.0.
    Recibe el código de autorización de Google y lo intercambia por tokens.
    """
    logger.info("Petición recibida en /api/auth/google/callback")
    if not _auth_controller:
        logger.error("Controlador de autenticación no inicializado en /api/auth/google/callback")
        return jsonify({'message': 'Error interno del servidor: controlador no inicializado'}), 500

    # Google puede enviar el código en request.args (GET) o request.form (POST)
    code = request.args.get('code') or request.form.get('code')

    if code:
        logger.info(f"Código de Google recibido: {code[:10]}...") # Log parcial por seguridad
        user_info = _auth_controller.handle_google_callback(code)
        if user_info:
            logger.info(f"Callback de Google procesado exitosamente para usuario: {user_info.get('email')}")
            # El controlador ya establece la sesión de Flask
            return jsonify({'message': 'Inicio de sesión con Google exitoso', 'user': user_info}), 200
        else:
            logger.error("Error al procesar el callback de Google en el controlador.")
            return jsonify({'message': 'Error al procesar el callback de Google'}), 401
    else:
        logger.warning("No se recibió el código de Google en el callback.")
        return jsonify({'message': 'No se recibió el código de Google'}), 400


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint para el registro de nuevos usuarios.
    Recibe email, contraseña y confirmación, los valida y registra al usuario.
    """
    logger.info("Petición POST recibida en /api/register")
    if not _auth_controller:
        logger.error("Controlador de autenticación no inicializado en /api/register")
        return jsonify({'message': 'Error interno del servidor: controlador no inicializado'}), 500

    data = request.form # Los datos vienen del formulario HTML
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Validación de entrada
    if not email or not password or not confirm_password:
        logger.warning("Intento de registro con campos faltantes.")
        return jsonify({'message': 'Faltan campos'}), 400

    if password != confirm_password:
        logger.warning("Intento de registro: las contraseñas no coinciden.")
        return jsonify({'message': 'Las contraseñas no coinciden'}), 400

    # Llamamos al método del controlador para la lógica de negocio
    user_info = _auth_controller.register_user(email, password)
    if user_info:
        logger.info(f"Registro exitoso para {email}")
        return jsonify({'message': 'Registro exitoso', 'user': user_info}), 201 # 201 Created
    else:
        logger.warning(f"Registro fallido para {email}. El email ya podría estar en uso.")
        return jsonify({'message': 'El registro falló. El email ya podría estar en uso'}), 409 # 409 Conflict

