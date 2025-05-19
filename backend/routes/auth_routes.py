# backend/routes/auth_routes.py
from flask import Blueprint, request, jsonify, redirect, url_for
from backend.controllers.auth_controller import login_user, handle_google_callback, register_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.form
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Faltan email o contraseña'}), 400

    user = login_user(email, password)

    if user:
        return jsonify({'message': 'Inicio de sesión exitoso', 'user': {'id': user['id'], 'email': user['email']}}), 200
    else:
        return jsonify({'message': 'Credenciales inválidas'}), 401

    # Revisa la línea ANTERIOR a esta
@auth_bp.route('/auth/google/callback', methods=['POST'])
def google_callback():
    code = request.form.get('code')
    if code:
        user_info = handle_google_callback(code)
        if user_info:
            return jsonify({'message': 'Inicio de sesión con Google exitoso', 'user': user_info}), 200
        else:
            return jsonify({'message': 'Error al procesar el callback de Google'}), 401
    else:
        return jsonify({'message': 'No se recibió el código de Google'}), 400


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.form
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not email or not password or not confirm_password:
        return jsonify({'message': 'Faltan campos'}), 400

    if password != confirm_password:
        return jsonify({'message': 'Las contraseñas no coinciden'}), 400

    user = register_user(email, password)
    if user:
        return jsonify({'message': 'Registro exitoso', 'user': {'id': user['id'], 'email': user['email']}}), 201
    else:
        return jsonify({'message': 'El registro falló. El email ya podría estar en uso'}), 409

