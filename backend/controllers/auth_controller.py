# backend/controllers/auth_controller.py
import bcrypt
import google_auth_oauthlib.flow
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import session
import logging
import os # Necesario para verificar la existencia del archivo de secretos

# Importamos nuestra clase User y UserRepository
from backend.models.user import User 
from backend.repositories.user_repository import UserRepository 
from config import Config # Importamos la clase de configuración

logger = logging.getLogger(__name__) # Inicializamos el logger para este módulo

class AuthController:
    """
    Controlador encargado de la lógica de negocio relacionada con la autenticación de usuarios.
    Depende de UserRepository para la persistencia de usuarios y de Config para las credenciales de OAuth.
    Sigue el principio de Responsabilidad Única (SRP) al delegar la persistencia al repositorio.
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
        self.google_client_id = config.GOOGLE_CLIENT_ID
        
        # La URI de redirección debe coincidir con la configurada en Google Cloud Console
        # y también con la ruta real en tu aplicación Flask (incluyendo el prefijo /api)
        self.google_redirect_uri = config.GOOGLE_REDIRECT_URI 

        # Si estás usando el flujo de código (flow.from_client_secrets_file),
        # entonces GOOGLE_CLIENT_SECRET_FILE es necesario.
        # En tu caso, el frontend envía el 'code', por lo que el backend necesita este archivo.
        self.google_client_secret_file = config.GOOGLE_CLIENT_SECRET_FILE 

        # Validación de configuración esencial
        if not self.google_client_id:
            logger.error("ERROR: GOOGLE_CLIENT_ID no configurado en config.py")
            raise ValueError("GOOGLE_CLIENT_ID no configurado en config.py")
        
        # Verificar que el archivo de secretos de cliente de Google exista
        if not os.path.exists(self.google_client_secret_file):
            logger.critical(f"ERROR CRÍTICO: Archivo de secretos de cliente de Google no encontrado en: {self.google_client_secret_file}")
            logger.critical("Asegúrate de que 'client_secret.json' está en la ruta correcta y que GOOGLE_CLIENT_SECRET_FILE en config.py apunta a él.")
            raise FileNotFoundError(f"Archivo de secretos de cliente de Google no encontrado en {self.google_client_secret_file}. No se puede iniciar la autenticación de Google.")


    def register_user(self, email: str, password: str) -> dict | None:
        """
        Registra un nuevo usuario en el sistema.
        Delega el hasheo de la contraseña y la encriptación del email al UserRepository.

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
        # Se sigue el principio de Inversión de Dependencias (DIP) al depender de la abstracción User.
        new_user_obj = User(_id=None, email=email, password=password, name=email.split('@')[0])

        # 2. Guardar el usuario utilizando el repositorio.
        # user_repo.add_user se encarga de verificar email existente, hashear contraseña,
        # encriptar email y guardar. Retorna el User objeto con el email desencriptado.
        # Esto demuestra alta cohesión y bajo acoplamiento.
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
        Intenta iniciar sesión a un usuario con credenciales de email y contraseña.

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
        Intercambia el código por tokens y verifica la identidad del usuario con Google.
        Crea o actualiza el usuario en el repositorio.

        Args:
            code (str): El código de autorización recibido de Google.

        Returns:
            dict | None: Un diccionario con la información del usuario si el inicio de sesión
                         con Google es exitoso, o None en caso de error.
        """
        logger.info(f"Iniciando manejo de callback de Google para código: {code[:10]}...") # Log parcial del código por seguridad
        try:
            # Configura el flujo de OAuth 2.0 usando el archivo de secretos de cliente
            # Este es el flujo de autorización de código, donde el backend intercambia el código.
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                self.google_client_secret_file,
                scopes=['openid', 'email', 'profile'] # Scopes solicitados a Google
            )
            # La URI de redirección debe coincidir exactamente con la configurada en Google Cloud Console
            # y con la URL real de tu endpoint de callback en Flask.
            flow.redirect_uri = self.google_redirect_uri

            # Completa el intercambio de código por tokens
            # Reconstruimos la URL de autorización que Google usaría para redirigir
            # Esto es necesario para flow.fetch_token cuando el 'code' viene en el body de un POST.
            authorization_response = f'{self.google_redirect_uri}?code={code}'
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials # Contiene access_token, refresh_token, id_token

            # Verifica el token de ID (JWT) para obtener la información del usuario
            # Esto valida que el token es auténtico y fue emitido por Google para tu cliente.
            request_obj = requests.Request()
            id_info = id_token.verify_oauth2_token(credentials.id_token, request_obj, self.google_client_id)

            # Valida el emisor del token para mayor seguridad
            if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.error(f"Emisor de token de Google inválido: {id_info.get('iss')}")
                raise ValueError('Emisor de token inválido.')

            # Extrae la información del usuario del token de ID
            google_id = id_info.get('sub') # 'sub' es el ID único de Google para el usuario
            email = id_info.get('email')
            name = id_info.get('name', email.split('@')[0]) # Usa el nombre de Google o deriva del email
            profile_picture_url = id_info.get('picture')

            logger.info(f"Información de Google obtenida para email: {email}, Google ID: {google_id}")

            # 1. Buscar usuario por Google ID
            user_obj: User = self.user_repo.find_user_by_google_id(google_id)

            if user_obj:
                logger.info(f"Usuario de Google existente '{email}' ha iniciado sesión.")
                # Actualizar el nombre y la foto de perfil si vienen de Google y no están en nuestra DB
                updated_fields = {}
                if not user_obj.name and name:
                    updated_fields['name'] = name
                if not user_obj.profile_picture_url and profile_picture_url:
                    updated_fields['profile_picture_url'] = profile_picture_url
                
                # Solo actualizar si hay campos nuevos para evitar escrituras innecesarias
                if updated_fields:
                    # El repositorio se encarga de la persistencia
                    self.user_repo.update_user(user_obj.id, updated_fields) 
                    # Actualizar el objeto en memoria para la sesión actual
                    user_obj.name = updated_fields.get('name', user_obj.name)
                    user_obj.profile_picture_url = updated_fields.get('profile_picture_url', user_obj.profile_picture_url)

                # Establecer la sesión de Flask para el usuario logueado
                session['user_id'] = user_obj.id
                session['user_email'] = user_obj.email 
                session['user_name'] = user_obj.name if user_obj.name else user_obj.email.split('@')[0]
                return user_obj.to_dict()
            else:
                # 2. Si el usuario NO existe por Google ID, intentar buscar por email.
                # Esto es para vincular cuentas si un usuario ya se registró con email/pass y luego usa Google.
                user_obj_by_email: User = self.user_repo.find_user_by_email(email)

                if user_obj_by_email:
                    logger.info(f"Usuario existente '{email}' encontrado por email. Vinculando cuenta de Google.")
                    # Si existe por email, asociar el google_id a esta cuenta existente y actualizar otros campos
                    updated_fields = {'google_id': google_id} # Campo principal a actualizar
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
                    logger.info(f"Creando nuevo usuario de Google para email: {email}.")
                    new_google_user = User(
                        _id=None, # El ID se asignará en el repositorio
                        email=email,
                        name=name,
                        profile_picture_url=profile_picture_url,
                        google_id=google_id 
                    )
                    # El repositorio se encarga de añadir el usuario
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
