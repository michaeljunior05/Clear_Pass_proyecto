# backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, session # Añadir session
# Eliminamos las importaciones directas de funciones del controlador
# from backend.controllers.auth_controller import login_user, handle_google_callback, register_user

auth_bp = Blueprint('auth', __name__)

# Esta variable global será asignada desde app.py para inyectar el controlador.
# No es el patrón más limpio para Flask a gran escala, pero es simple para empezar.
_auth_controller = None

def init_auth_routes(controller):
    """
    Función para inicializar las rutas de autenticación con el controlador adecuado.
    Esta función será llamada desde app.py.
    """
    global _auth_controller
    _auth_controller = controller

@auth_bp.route('/login', methods=['POST'])
def login():
    # Verificación para asegurarse de que el controlador ha sido inicializado
    if not _auth_controller:
        return jsonify({'message': 'Controlador de autenticación no inicializado'}), 500

    data = request.form
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Faltan email o contraseña'}), 400

    # Llamamos al método del objeto _auth_controller
    user_info = _auth_controller.login_user(email, password)

    if user_info:
        # El controlador ya establece session['user_id']
        return jsonify({'message': 'Inicio de sesión exitoso', 'user': user_info}), 200
    else:
        return jsonify({'message': 'Credenciales inválidas'}), 401

@auth_bp.route('/auth/google/callback', methods=['GET', 'POST']) # Aceptar GET y POST
def google_callback():
    if not _auth_controller:
        return jsonify({'message': 'Controlador de autenticación no inicializado'}), 500

    # Google puede enviar el código en request.args (GET) o request.form (POST)
    code = request.args.get('code') or request.form.get('code')

    if code:
        user_info = _auth_controller.handle_google_callback(code)
        if user_info:
            # El controlador ya establece session['user_id']
            return jsonify({'message': 'Inicio de sesión con Google exitoso', 'user': user_info}), 200
        else:
            return jsonify({'message': 'Error al procesar el callback de Google'}), 401
    else:
        return jsonify({'message': 'No se recibió el código de Google'}), 400


@auth_bp.route('/register', methods=['POST'])
def register():
    if not _auth_controller:
        return jsonify({'message': 'Controlador de autenticación no inicializado'}), 500

    data = request.form
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not email or not password or not confirm_password:
        return jsonify({'message': 'Faltan campos'}), 400

    if password != confirm_password:
        return jsonify({'message': 'Las contraseñas no coinciden'}), 400

    # Llamamos al método del objeto _auth_controller
    user_info = _auth_controller.register_user(email, password)
    if user_info:
        return jsonify({'message': 'Registro exitoso', 'user': user_info}), 201
    else:
        return jsonify({'message': 'El registro falló. El email ya podría estar en uso'}), 409

