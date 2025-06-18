import logging
from typing import Dict, Any, Optional
import google_auth_oauthlib.flow
import google.oauth2.credentials
import requests
from flask import session, request 
from backend.repositories.user_repository import UserRepository
from config import Config
from oauthlib.oauth2.rfc6749 import errors as oauth2_errors 
from backend.models.user import User

logger = logging.getLogger(__name__)

class AuthController:
    """
    Controlador encargado de la lógica de negocio de autenticación.
    Maneja el registro, inicio de sesión y la autenticación con Google.
    """
    def __init__(self, user_repository: UserRepository, config: Config):
        """
        Inicializa AuthController.

        Args:
            user_repository (UserRepository): Instancia del repositorio de usuarios.
            config (Config): Instancia de la configuración de la aplicación.
        """
        self.user_repository = user_repository
        self.config = config
        self.google_client_id = self.config.GOOGLE_CLIENT_ID
        self.google_redirect_uri = self.config.GOOGLE_REDIRECT_URI
        self.google_client_secret_file = self.config.GOOGLE_CLIENT_SECRET_FILE
        logger.info("AuthController inicializado.")

    def register_user(self, email: str, password: str) -> Dict[str, str] | None:
        """
        Registra un nuevo usuario en el sistema.
        """
        logger.info(f"Intentando registrar usuario con email: {email}")
        existing_user = self.user_repository.find_user_by_email(email)
        if existing_user:
            logger.warning(f"Intento de registro fallido: el email {email} ya existe.")
            return {'message': 'El email ya está registrado.'}

        # MODIFICADO AQUÍ: Crear una instancia de User en lugar de un diccionario
        new_user = User(
            email=email,
            password=password,
            name=email.split('@')[0] # Usar el prefijo del email como nombre por defecto
        )
        
        # Pasar el objeto User al repositorio
        user = self.user_repository.add_user(new_user)

        if user:
            # Una vez guardado, el objeto user que retorna el repositorio ya tiene el ID, email hasheado/encriptado
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email # El email ya viene desencriptado del repositorio en el User object
            logger.info(f"Usuario {email} registrado exitosamente con ID: {user.id}")
            return {'message': 'Registro exitoso. Ahora puedes iniciar sesión.'}
        else:
            logger.error(f"Fallo al registrar usuario: {email}")
            return {'message': 'Error al registrar el usuario.'}

    def login_user(self, email: str, password: str) -> Dict[str, str] | None:
        """
        Autentica a un usuario.
        """
        logger.info(f"Intentando iniciar sesión con email: {email}")
        user = self.user_repository.find_user_by_email_and_password(email, password)
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email
            logger.info(f"Usuario {email} inició sesión exitosamente.")
            return {'message': 'Inicio de sesión exitoso.'}
        else:
            logger.warning(f"Intento de inicio de sesión fallido para el email: {email}")
            return {'message': 'Email o contraseña incorrectos.'}
            
    def handle_google_callback(self, code: str) -> Dict[str, Any] | None: 
        """
        Maneja el callback de Google OAuth 2.0.
        Intercambia el código de autorización por tokens de acceso y obtiene la información del usuario.
        """
        logger.info("Procesando callback de Google.")
        if not code:
            logger.warning("No se recibió el código de autorización de Google.")
            return None

        try:
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                self.google_client_secret_file,
                scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid'],
                redirect_uri=self.google_redirect_uri 
            )
            
            logger.info(f"Flow object initialized with redirect_uri: {flow.redirect_uri}") 
            
            logger.info(f"Intentando fetch_token con code: {code} (sin pasar redirect_uri explícitamente)")
            flow.fetch_token(code=code) 
            
            credentials = flow.credentials
            
            userinfo_endpoint = 'https://www.googleapis.com/oauth2/v3/userinfo'
            response = requests.get(userinfo_endpoint, headers={'Authorization': 'Bearer ' + credentials.token})
            response.raise_for_status() 
            user_info = response.json()

            google_id = user_info['sub']
            email = user_info['email']
            name = user_info.get('name', email.split('@')[0])
            profile_picture_url = user_info.get('picture')

            user = self.user_repository.find_user_by_google_id(google_id)
            if not user:
                # Crear instancia de User para Google OAuth
                new_user = User(
                    email=email,
                    name=name,
                    profile_picture_url=profile_picture_url,
                    google_id=google_id
                )
                user = self.user_repository.add_user(new_user)
                logger.info(f"Nuevo usuario de Google registrado: {email}")
            else:
                logger.info(f"Usuario de Google existente inició sesión: {email}")
                # Actualizar datos del usuario existente si es necesario
                updated_data = {}
                if user.name != name: updated_data['name'] = name
                if user.profile_picture_url != profile_picture_url: updated_data['profile_picture_url'] = profile_picture_url
                if updated_data:
                    self.user_repository.update_user(user.id, updated_data)
                    logger.info(f"Datos de usuario de Google actualizados para {email}")

            if user:
                return {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'profile_picture_url': user.profile_picture_url
                }
            else:
                logger.error(f"Fallo al guardar/recuperar usuario de Google: {email}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error en la petición a Google Userinfo API: {e}", exc_info=True)
            return None
        except oauth2_errors.OAuth2Error as e: 
            logger.error(f"Error de OAuth2 (probablemente redirect_uri_mismatch): {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Error inesperado en handle_google_callback: {e}", exc_info=True)
            return None

