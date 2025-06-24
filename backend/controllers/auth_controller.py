# backend/controllers/auth_controller.py
import logging
import os
import secrets 
from flask import jsonify, session, request 
from typing import Optional, Dict, Any, Tuple 

from backend.repositories.user_repository import UserRepository
from backend.models.user import User 
from config import Config 

# Importar para decodificar JWT de Google (si se usa la simulación)
try:
    import jwt
except ImportError:
    logger.warning("PyJWT no instalado. Las funciones de Google Login pueden no decodificar JWT correctamente sin validación real.")


logger = logging.getLogger(__name__)

class AuthController:
    """
    Controlador encargado de la lógica de negocio de autenticación.
    Maneja el registro, inicio de sesión y la autenticación con Google.
    """
    def __init__(self, user_repository: UserRepository, config: Config):
        self.user_repo = user_repository
        self.config = config
        self.google_client_id = self.config.GOOGLE_CLIENT_ID
        logger.info("AuthController inicializado.")

    def register_user(self, email: str, password: str, name: Optional[str] = None, 
                      phone_number: Optional[str] = None, dni: Optional[str] = None) -> Tuple[Dict[str, Any], int]:
        """
        Registra un nuevo usuario con email, contraseña y campos opcionales.
        Recibe los datos directamente como argumentos.
        """
        logger.info(f"Intentando registrar usuario con email: {email}")
        
        if not email or not password:
            logger.warning(f"Faltan campos requeridos en el registro. Email: {email}, Password: {'[presente]' if password else '[ausente]'}.")
            return jsonify({"message": "Email y contraseña son obligatorios."}), 400

        if len(password) < 6:
            logger.warning(f"Intento de registro con contraseña corta para {email}.")
            return jsonify({"message": "La contraseña debe tener al menos 6 caracteres."}), 400

        # === CAMBIO CLAVE AQUÍ: ELIMINAR 'id=None' ===
        new_user = User(
            email=email,
            password=password, 
            name=name if name else email.split('@')[0], 
            phone_number=phone_number,
            dni=dni,
            is_premium=False 
        )
        # === FIN CAMBIO CLAVE ===

        try:
            registered_user = self.user_repo.add_user(new_user)

            if registered_user:
                logger.info(f"Usuario {email} registrado exitosamente. ID: {registered_user.id}")
                session['user_id'] = registered_user.id
                session['user_name'] = registered_user.name
                session['user_email'] = registered_user.email
                logger.info(f"Sesión iniciada automáticamente para el nuevo usuario {email}.")
                return jsonify({"message": "Registro exitoso. Ahora puedes navegar por los productos.", "user_id": registered_user.id}), 201
            else:
                logger.warning(f"Fallo en el registro para el email: {email}. Posiblemente ya existe.")
                return jsonify({"message": "El email ya está registrado o hubo un error."}), 409
        except Exception as e:
            logger.error(f"Error inesperado durante el registro de {email}: {e}")
            return jsonify({"message": "Error interno del servidor durante el registro."}), 500

    def login_user(self, email: str, password: str) -> Tuple[Dict[str, Any], int]:
        """
        Inicia sesión a un usuario con email y contraseña.
        Recibe los datos directamente como argumentos.
        """
        logger.info(f"Intentando iniciar sesión con email: {email}")
        
        if not email or not password:
            logger.warning("Faltan campos requeridos en el login (email o password).")
            return jsonify({"message": "Email y contraseña son obligatorios."}), 400

        user = self.user_repo.find_user_by_email_and_password(email, password)

        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email 
            logger.info(f"Usuario {email} ha iniciado sesión exitosamente.")
            return jsonify({"message": "Inicio de sesión exitoso.", "user_id": user.id}), 200
        else:
            logger.warning(f"Intento de inicio de sesión fallido para el email: {email}.")
            return jsonify({"message": "Credenciales inválidas."}), 401

    def google_login(self) -> Tuple[Dict[str, Any], int]: 
        """
        Maneja el inicio de sesión/registro de Google.
        Espera un JWT (id_token) en el cuerpo JSON.
        """
        logger.info("Petición de Google Login recibida.")
        data = request.json 
        id_token = data.get('credential') 

        if not id_token:
            logger.warning("No se recibió el token de credenciales de Google.")
            return jsonify({"message": "Token de Google no proporcionado."}), 400

        try:
            decoded_token = jwt.decode(id_token, options={"verify_signature": False})
            google_email = decoded_token.get('email')
            google_id = decoded_token.get('sub') 
            google_name = decoded_token.get('name', google_email)

            if not google_email or not google_id:
                logger.warning("El token de Google no contiene email o ID de usuario.")
                return jsonify({"message": "Información de Google incompleta."}), 400

            user = self.user_repo.find_user_by_google_id(google_id)
            if not user:
                user = self.user_repo.find_user_by_email(google_email)
                if user:
                    logger.info(f"Vincular Google ID a usuario existente con email: {google_email}")
                    user.google_id = google_id
                    user = self.user_repo.update_user(user.id, user.to_dict()) 
                    if not user: 
                        raise Exception("Fallo al vincular Google ID a usuario existente.")
                else:
                    logger.info(f"Registrando nuevo usuario con Google: {google_email}")
                    new_user = User(
                        email=google_email, # No se pasa ID aquí tampoco
                        password=None, 
                        name=google_name,
                        google_id=google_id,
                        is_premium=False
                    )
                    user = self.user_repo.add_user(new_user)

            if user:
                session['user_id'] = user.id
                session['user_name'] = user.name
                session['user_email'] = user.email
                logger.info(f"Usuario {user.email} (Google ID: {user.google_id}) ha iniciado sesión/registrado.")
                return jsonify({"message": "Inicio de sesión con Google exitoso.", "redirect_url": "/productos"}), 200
            else:
                logger.error(f"Fallo en el proceso de Google Login para {google_email}.")
                return jsonify({"message": "Error al procesar el inicio de sesión con Google."}), 500

        except Exception as e:
            logger.error(f"Error inesperado en Google Login: {e}")
            return jsonify({"message": "Error interno del servidor al procesar Google Login."}), 500

    def logout_user(self) -> Tuple[Dict[str, Any], int]: 
        """
        Cierra la sesión del usuario.
        """
        session.pop('user_id', None)
        session.pop('user_name', None)
        session.pop('user_email', None)
        logger.info("Usuario ha cerrado sesión.")
        return jsonify({"message": "Sesión cerrada exitosamente."}), 200

    def get_session_info(self) -> Tuple[Dict[str, Any], int]: 
        """
        Devuelve información sobre la sesión actual.
        """
        user_id = session.get('user_id')
        user_name = session.get('user_name')
        user_email = session.get('user_email')
        
        if user_id:
            user = self.user_repo.get_user_by_id(user_id)
            if user:
                is_premium = user.is_premium
                return jsonify({
                    "logged_in": True,
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_email": user_email,
                    "is_premium": is_premium,
                    "phone_number": user.phone_number, 
                    "dni": user.dni 
                }), 200
            else:
                session.pop('user_id', None)
                session.pop('user_name', None)
                session.pop('user_email', None)
                logger.warning(f"Usuario con ID {user_id} no encontrado en el repositorio, sesión limpiada.")
                return jsonify({"logged_in": False, "message": "Sesión inválida."}), 401
        
        return jsonify({"logged_in": False}), 200

    def update_user_profile(self) -> Tuple[Dict[str, Any], int]: 
        """
        Actualiza el perfil del usuario.
        """
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"message": "No autenticado."}), 401

        data = request.json
        if not data:
            return jsonify({"message": "Datos de actualización no proporcionados."}), 400

        logger.info(f"Intentando actualizar perfil para usuario ID: {user_id} con datos: {data}")
        updated_user = self.user_repo.update_user(user_id, data)

        if updated_user:
            session['user_name'] = updated_user.name
            session['user_email'] = updated_user.email
            logger.info(f"Perfil del usuario {user_id} actualizado exitosamente.")
            return jsonify({"message": "Perfil actualizado exitosamente.", "user": updated_user.to_dict()}), 200
        else:
            logger.warning(f"Fallo al actualizar el perfil del usuario {user_id}. Posiblemente email duplicado.")
            return jsonify({"message": "Error al actualizar el perfil. El email podría estar en uso."}), 400
