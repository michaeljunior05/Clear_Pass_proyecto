# backend/repositories/user_repository.py
from backend.models.user import User
from backend.repositories.json_storage import JSONStorage
import os

import bcrypt # Importar bcrypt
from cryptography.fernet import Fernet # Importar Fernet
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Gestiona la persistencia de objetos User utilizando JSONStorage.
    Actúa como una capa de abstracción entre los controladores y la base de datos (JSON).
    """
    def __init__(self, storage: JSONStorage):
        """
        Inicializa el UserRepository.

        Args:
            storage (JSONStorage): Una instancia de JSONStorage para el acceso a datos.
        """
        self.storage = storage
        self.entity_type = "users" # Define la clave bajo la cual se guardarán los usuarios en el JSON
        self.fernet = self._load_fernet_key_from_file()
        logger.info("Clave Fernet cargada desde archivo en UserRepository.")

    def _load_fernet_key_from_file(self):
        """
        Carga la clave Fernet desde el archivo 'backend/email.key'.
        """
        # Ruta absoluta de la clave: /path/to/Clear_Pass_proyecto/backend/email.key
        # os.path.dirname(os.path.abspath(__file__)) es /path/to/Clear_Pass_proyecto/backend/repositories
        # os.path.join(..., '..') sube un nivel a /path/to/Clear_Pass_proyecto/backend
        key_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', # Sube de 'repositories' a 'backend'
            'email.key' # Nombre del archivo de la clave
        )

        if not os.path.exists(key_file_path):
            logger.error(f"¡ERROR CRÍTICO! La clave Fernet no se encontró en: {key_file_path}")
            logger.error("Asegúrate de que el archivo 'email.key' existe en la carpeta 'backend/' y contiene la clave.")
            raise FileNotFoundError(f"Clave Fernet no encontrada en {key_file_path}. No se puede iniciar la aplicación.")
        else:
            with open(key_file_path, "rb") as key_file:
                key = key_file.read()
            logger.info(f"Clave Fernet cargada exitosamente desde: {key_file_path}")
        
        return Fernet(key)

    def _encrypt_email(self, email: str) -> str:
        """Encripta un email."""
        return self.fernet.encrypt(email.encode()).decode()

    def _decrypt_email(self, encrypted_email: str) -> str:
        """Desencripta un email."""
        try:
            return self.fernet.decrypt(encrypted_email.encode()).decode()
        except Exception as e:
            logger.error(f"Error al desencriptar email: {e}")
            return None # Retornar None o manejar el error adecuadamente



    def get_all_users(self) -> list[User]:
        """
        Recupera todos los usuarios y los convierte a objetos User.
        """
        all_users_data = self.storage.get_all(self.entity_type)
        return [User.from_dict(data) for data in all_users_data]
    
    def get_user_by_id(self, user_id: str) -> User | None:
        """
        Busca un usuario por su ID.
        """
        user_data = self.storage.get_by_id(self.entity_type, user_id)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def find_user_by_email(self, email: str) -> User | None:
        """
        Busca un usuario por su dirección de correo electrónico (desencriptando los almacenados).
        Retorna un objeto User.
        """
        all_users = self.get_all_users() # Obtiene todos los usuarios como objetos User
        for user in all_users:
            if user.email: # Asegurarse de que el objeto User tenga un email
                try:
                    # Si el email ya está encriptado en el objeto User (porque así se guardó)
                    # Necesitamos desencriptarlo para comparar con el email en texto plano
                    # recibido.
                    # Asumiendo que `User.from_dict` te entrega el email tal cual del JSON.
                    # Si el email en el JSON está encriptado, este es el lugar para desencriptarlo.
                    
                    # Vamos a modificar User.from_dict para que el email siempre llegue desencriptado
                    # O bien, desencriptar aquí:
                    stored_email_data = self.storage.find_by_attribute(self.entity_type, 'id', user.id)
                    if stored_email_data and stored_email_data[0].get('email'):
                        decrypted_stored_email = self._decrypt_email(stored_email_data[0]['email'])
                        if decrypted_stored_email == email:
                            # Reemplaza el email encriptado del objeto User con el desencriptado
                            user.email = decrypted_stored_email 
                            return user
                except Exception as e:
                    logger.warning(f"Error al desencriptar email para buscar: {e}")
                    continue # Ignorar usuarios con emails que no se pueden desencriptar
        return None
    
    def add_user(self, user: User) -> User | None:
        """
        Añade un nuevo objeto User, encriptando su email y hasheando su contraseña.
        Retorna el objeto User con los datos ya procesados (ID, hasheo, encriptación).
        """
        logger.info(f"Intentando añadir usuario: {user.email}")
        
        # Verificar si el email ya existe
        # Nota: find_user_by_email ahora desencripta para la comparación
        if self.find_user_by_email(user.email):
            logger.warning(f"Intento de registro con email existente: {user.email}")
            return None # El email ya está en uso

        # Hash de la contraseña si se proporciona
        if user.password:
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user.password = hashed_password
        
        # Encriptar el email
        if user.email:
            encrypted_email = self._encrypt_email(user.email)
            user.email = encrypted_email # Actualiza el email del objeto User a su versión encriptada

        # Guardar en JSONStorage a través de save_entity, que asigna ID si es nuevo
        user_data = user.to_dict() # Convertir el objeto User a dict (con email encriptado y pass hasheada)
        saved_data = self.storage.save_entity(self.entity_type, user_data)
        
        if saved_data:
            logger.info(f"Usuario {saved_data.get('email', '[email encriptado]')} añadido al repositorio.")
            # Retorna el objeto User recién creado, con el ID asignado y el email desencriptado para el controlador
            saved_user_obj = User.from_dict(saved_data)
            saved_user_obj.email = self._decrypt_email(saved_user_obj.email) # Desencriptar para devolver al controlador
            return saved_user_obj
        else:
            logger.error(f"Fallo al guardar el usuario {user.email}.")
            return None
        

    
    def find_user_by_email_and_password(self, email: str, password: str) -> User | None:
        """
        Busca un usuario por email y contraseña, desencriptando el email y verificando la contraseña.
        Retorna un objeto User si la autenticación es exitosa.
        """
        all_users = self.get_all_users() # Obtiene todos los usuarios como objetos User
        for user_obj in all_users:
            # Los datos del objeto User aquí pueden tener el email ya encriptado.
            # Necesitamos el email encriptado tal cual está en el JSON para desencriptarlo.
            # Accedemos directamente a los datos guardados si el user_obj.email es la versión encriptada.
            stored_email_data = self.storage.find_by_attribute(self.entity_type, 'id', user_obj.id)
            stored_email_encrypted = stored_email_data[0].get('email') if stored_email_data else None
            stored_password_hashed = user_obj.password # La password está hasheada en el objeto User

            if stored_email_encrypted and stored_password_hashed:
                try:
                    decrypted_stored_email = self._decrypt_email(stored_email_encrypted)
                    # Compara el email desencriptado con el email en texto plano proporcionado
                    if decrypted_stored_email == email:
                        # Verifica la contraseña hasheada
                        if bcrypt.checkpw(password.encode('utf-8'), stored_password_hashed.encode('utf-8')):
                            logger.info(f"Usuario {email} encontrado y autenticado.")
                            # Retorna el objeto User, asegurando que el email sea la versión desencriptada
                            user_obj.email = decrypted_stored_email
                            return user_obj
                except Exception as e:
                    logger.warning(f"Error procesando usuario para login: {e}")
                    continue # Ignorar usuarios con emails que no se pueden desencriptar

        logger.warning(f"Fallo de autenticación para el email: {email}")
        return None
    

    def find_user_by_google_id(self, google_id: str) -> User | None:
        """
        Busca un usuario por su ID de Google.
        Retorna un objeto User.
        """
        # find_by_attribute devuelve una lista de diccionarios, tomamos el primero si existe
        users_data = self.storage.find_by_attribute(self.entity_type, "google_id", google_id)
        if users_data:
            user_data = users_data[0] # Asumimos que google_id es único
            logger.info(f"Usuario de Google con ID {google_id} encontrado.")
            user_obj = User.from_dict(user_data)
            
            # Desencriptar el email si es un usuario con email encriptado
            if 'email' in user_data and user_data.get('email') and self.fernet:
                try:
                    user_obj.email = self._decrypt_email(user_data['email'])
                except Exception:
                    pass # Si falla la desencriptación, dejamos el email como estaba
            return user_obj
        logger.warning(f"Usuario de Google con ID {google_id} no encontrado.")
        return None
    

    def update_user(self, user_id: str, new_data: dict) -> User | None:
        """
        Actualiza un usuario existente. Si el email o la contraseña se actualizan,
        se encriptan/hashean de nuevo.
        Retorna el objeto User actualizado.
        """
        existing_user_data = self.storage.get_by_id(self.entity_type, user_id)
        if not existing_user_data:
            logger.warning(f"No se encontró el usuario con ID {user_id} para actualizar.")
            return None
        
        # Convertir a objeto User para manejar fácilmente
        user_obj = User.from_dict(existing_user_data)

        # Aplicar las actualizaciones a la data del usuario (antes de convertir de nuevo a dict)
        if 'email' in new_data:
            # Primero, aseguramos que el nuevo email no exista para otro usuario
            # Y luego encriptamos el nuevo email
            if self.find_user_by_email(new_data['email']): # Esto buscará el email desencriptado
                # Si el email existe y no es el email actual del usuario, es un conflicto
                if self._decrypt_email(user_obj.email) != new_data['email']:
                    logger.warning(f"Intento de actualizar a un email ya existente: {new_data['email']}")
                    return None
            user_obj.email = self._encrypt_email(new_data['email'])
        
        if 'password' in new_data:
            user_obj.password = bcrypt.hashpw(new_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Actualizar otros campos (name, etc.)
        if 'name' in new_data:
            user_obj.name = new_data['name']
        if 'google_id' in new_data: # Permite actualizar o agregar google_id
            user_obj.google_id = new_data['google_id']

        # Convertir de nuevo a diccionario para guardar
        updated_user_data = user_obj.to_dict()
        
        saved_data = self.storage.save_entity(self.entity_type, updated_user_data)
        if saved_data:
            logger.info(f"Usuario con ID {user_id} actualizado.")
            # Retorna el objeto User actualizado con el email desencriptado
            updated_user_obj = User.from_dict(saved_data)
            updated_user_obj.email = self._decrypt_email(updated_user_obj.email)
            return updated_user_obj
        else:
            logger.error(f"Fallo al guardar la actualización del usuario con ID {user_id}.")
            return None
    
    


    

    def get_user_by_id(self, user_id: str) -> User | None:
        """
        Busca un usuario por su ID.

        Args:
            user_id (str): El ID del usuario a buscar.

        Returns:
            User | None: El objeto User si se encuentra, o None si no.
        """
        user_data = self.storage.get_by_id(self.entity_type, user_id)
        if user_data:
            return User.from_dict(user_data)
        return None

    def delete_user(self, user_id: str) -> bool:
        """
        Elimina un usuario por su ID.

        Args:
            user_id (str): El ID del usuario a eliminar.

        Returns:
            bool: True si el usuario fue eliminado, False si no se encontró.
        """
        return self.storage.delete_entity(self.entity_type, user_id)
    