# backend/controllers/auth_controller.py
import bcrypt # bcrypt sigue siendo útil para el controlador si no delegas TODO el hasheo al repo,
             # pero en nuestra nueva arquitectura, el repo lo maneja. Lo dejaremos por si acaso,
             # pero idealmente el controlador no debería tocar bcrypt.
import google_auth_oauthlib.flow # Esto es para el flujo de autorización completo,
                                 # que tu código original usaba. Lo ajustaremos para JWT.
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import session # Mantener para la sesión Flask
import logging # Añadir import de logging

# Importamos nuestra clase User y UserRepository
from backend.models.user import User 
from backend.repositories.user_repository import UserRepository 
from config import Config # Importamos la clase de configuración

logger = logging.getLogger(__name__) # Inicializamos el logger

class AuthController:
    """
    Controlador encargado de la lógica de negocio relacionada con la autenticación de usuarios.
    Depende de UserRepository para la persistencia de usuarios y de Config para las credenciales de OAuth.
    """
    def __init__(self, user_repository: UserRepository, config: Config):
        """
        Inicializa el AuthController.

        Args:
            user_repository (UserRepository): Instancia del repositorio de usuarios.
            config (Config): Instancia de la configuración de la aplicación.
        """
        self.user_repo = user_repository
        self.config = config
        self.google_client_id = config.GOOGLE_CLIENT_ID # Asegúrate de que este atributo existe
        self.google_redirect_uri = config.GOOGLE_REDIRECT_URI # Asegúrate de que este atributo existe

        # Validación de configuración
        if not self.google_client_id:
            logger.error("GOOGLE_CLIENT_ID no configurado en config.py")
            raise ValueError("GOOGLE_CLIENT_ID no configurado en config.py")
        
        # Si estás usando el flujo de código (flow.from_client_secrets_file),
        # entonces GOOGLE_CLIENT_SECRET_FILE es necesario.
        # Si solo usas JWTs directos, NO es necesario.
        # Asumiendo que vamos a usar JWTs directos desde el frontend (que es más simple).
        # self.google_client_secret_file = config.GOOGLE_CLIENT_SECRET_FILE 
        # if not self.google_client_secret_file:
        #    logger.warning("GOOGLE_CLIENT_SECRET_FILE no configurado en config.py. Esto puede ser un problema si usas el flujo de autorización completo de Google.")


    def register_user(self, email: str, password: str) -> dict | None:
        """
        Registra un nuevo usuario en el sistema.

        Args:
            email (str): El email del usuario.
            password (str): La contraseña en texto plano.

        Returns:
            dict | None: Un diccionario con la información del nuevo usuario (id, email, name)
                         si el registro es exitoso, o None si el email ya está en uso.
        """
        logger.info(f"Intento de registro para el email: {email}")

        # 1. Crear una nueva instancia del modelo User (email y password en texto plano)
        # El ID se asignará en el repositorio si es un usuario nuevo.
        # El nombre inicial puede ser derivado del email.
        new_user_obj = User(id=None, email=email, password=password, name=email.split('@')[0])

        # 2. Guardar el usuario utilizando el repositorio.
        # user_repo.add_user se encarga de verificar email existente, hashear contraseña,
        # encriptar email y guardar. Retorna el User objeto con el email desencriptado.
        user_registered: User = self.user_repo.add_user(new_user_obj)
        
        if user_registered:
            logger.info(f"Usuario '{user_registered.email}' registrado exitosamente con ID: {user_registered.id}.")
            # Retornar un diccionario simple con info para la respuesta API
            return user_registered.to_dict() # to_dict() ya está definido en el modelo User
        else:
            logger.warning(f"Fallo el registro para el email: {email}. Posiblemente ya existe.")
            return None

    def login_user(self, email: str, password: str) -> dict | None:
        """
        Intenta iniciar sesión a un usuario.

        Args:
            email (str): El email del usuario.
            password (str): La contraseña en texto plano.

        Returns:
            dict | None: Un diccionario con la información del usuario (id, email, name, etc.)
                         si el inicio de sesión es exitoso, o None si las credenciales son inválidas.
        """
        logger.info(f"Intento de inicio de sesión para el email: {email}")

        # 1. Obtener el usuario por email y contraseña usando el repositorio
        # user_repo.find_user_by_email_and_password se encarga de desencriptar email y verificar hash.
        user_obj: User = self.user_repo.find_user_by_email_and_password(email, password)

        if user_obj:
            logger.info(f"Usuario '{email}' ha iniciado sesión exitosamente.")
            # Guardar información del usuario en la sesión de Flask
            session['user_id'] = user_obj.id
            session['user_email'] = user_obj.email # El email ya viene desencriptado del repositorio
            session['user_name'] = user_obj.name if user_obj.name else user_obj.email.split('@')[0]
            # Retornar un diccionario simple con info para la respuesta API
            return user_obj.to_dict() # to_dict() ya está definido en el modelo User
        else:
            logger.warning(f"Intento de inicio de sesión fallido para '{email}': credenciales inválidas.")
            return None

    def handle_google_callback(self, code: str) -> dict | None:
        """
        Maneja el callback de autenticación de Google utilizando el código de autorización.

        Args:
            code (str): El código de autorización recibido de Google.

        Returns:
            dict | None: Un diccionario con la información del usuario si el inicio de sesión
                         con Google es exitoso, o None en caso de error.
        """
        try:
            # Configura el flujo de OAuth 2.0
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                self.google_client_secret_file,
                scopes=['openid', 'email', 'profile']
            )
            flow.redirect_uri = self.google_redirect_uri

            # Completa el intercambio de código por tokens
            # Flask usa `request.url` para obtener la URL completa de la solicitud
            # Si el frontend envía el code en el body de un POST, `flow.fetch_token`
            # también puede tomar `request.get_data().decode('utf-8')`
            # pero dado que auth_routes.py lo lee de `request.args` o `request.form`,
            # lo mejor es reconstruir la URL de autorización para `flow.fetch_token`.
            authorization_response = f'{self.google_redirect_uri}?code={code}'
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials

            # Verifica el token de ID (este es el JWT dentro de las credenciales)
            request_obj = requests.Request()
            id_info = id_token.verify_oauth2_token(credentials.id_token, request_obj, self.google_client_id)

            # Valida el emisor del token
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.error(f"Emisor de token de Google inválido: {id_info.get('iss')}")
                raise ValueError('Wrong issuer.')

            google_id = id_info.get('sub')
            email = id_info.get('email')
            name = id_info.get('name', email.split('@')[0])
            profile_picture_url = id_info.get('picture')

            logger.info(f"Callback de Google procesado para email: {email}, ID: {google_id}")

            # 1. Buscar usuario por Google ID
            user_obj: User = self.user_repo.find_user_by_google_id(google_id)

            if user_obj:
                logger.info(f"Usuario de Google existente '{email}' ha iniciado sesión.")
                # Actualizar el nombre y la foto de perfil si vienen de Google y no están
                updated_fields = {}
                if not user_obj.name and name:
                    updated_fields['name'] = name
                if not user_obj.profile_picture_url and profile_picture_url:
                    updated_fields['profile_picture_url'] = profile_picture_url
                
                # Solo actualizar si hay campos nuevos
                if updated_fields:
                    self.user_repo.update_user(user_obj.id, updated_fields) 
                    # Una vez actualizado en el repo, el objeto user_obj ya tendrá esos campos
                    # o podemos recargarlo para asegurar: user_obj = self.user_repo.get_user_by_id(user_obj.id)
                    # O simplemente actualizar el objeto en memoria:
                    user_obj.name = updated_fields.get('name', user_obj.name)
                    user_obj.profile_picture_url = updated_fields.get('profile_picture_url', user_obj.profile_picture_url)


                session['user_id'] = user_obj.id
                session['user_email'] = user_obj.email 
                session['user_name'] = user_obj.name if user_obj.name else user_obj.email.split('@')[0]
                return user_obj.to_dict()
            else:
                # 2. Si el usuario NO existe por Google ID, intentar buscar por email.
                user_obj_by_email: User = self.user_repo.find_user_by_email(email)

                if user_obj_by_email:
                    logger.info(f"Usuario existente '{email}' encontrado por email. Vinculando cuenta de Google.")
                    # Si existe por email, asociar el google_id a esta cuenta existente y actualizar otros campos
                    updated_fields = {'google_id': google_id}
                    if not user_obj_by_email.name and name:
                        updated_fields['name'] = name
                    if not user_obj_by_email.profile_picture_url and profile_picture_url:
                        updated_fields['profile_picture_url'] = profile_picture_url
                    
                    updated_user: User = self.user_repo.update_user(user_obj_by_email.id, updated_fields)
                    
                    if updated_user:
                        session['user_id'] = updated_user.id
                        session['user_email'] = updated_user.email
                        session['user_name'] = updated_user.name if updated_user.name else updated_user.email.split('@')[0]
                        return updated_user.to_dict()
                    else:
                        logger.error(f"Fallo al actualizar usuario existente con Google ID: {email}")
                        return None
                else:
                    # 3. Si no existe ni por Google ID ni por email, crear un nuevo usuario de Google
                    new_google_user = User(
                        id=None, # El ID se asignará en el repositorio
                        email=email,
                        name=name,
                        profile_picture_url=profile_picture_url,
                        google_id=google_id 
                    )
                    user_created: User = self.user_repo.add_user(new_google_user)

                    if user_created:
                        logger.info(f"Nuevo usuario de Google '{email}' registrado y ha iniciado sesión. ID: {user_created.id}")
                        session['user_id'] = user_created.id
                        session['user_email'] = user_created.email
                        session['user_name'] = user_created.name if user_created.name else user_created.email.split('@')[0]
                        return user_created.to_dict()
                    else:
                        logger.error(f"Fallo al registrar un nuevo usuario de Google: {email}.")
                        return None

        except ValueError as ve:
            logger.error(f"Token de Google inválido o malformado: {ve}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Error inesperado al manejar el callback de Google para code: {code[:10]}... : {e}", exc_info=True)
            return None