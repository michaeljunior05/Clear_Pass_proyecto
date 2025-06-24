# backend/repositories/user_repository.py
from .base_repository import BaseRepository 
from backend.models.user import User
from backend.repositories.json_storage import JSONStorage
import os
import bcrypt 
from cryptography.fernet import Fernet 
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository):
    """
    Gestiona la persistencia de objetos User utilizando JSONStorage.
    """
    def __init__(self, storage: JSONStorage):
        super().__init__() # Llama al __init__ de BaseRepository (que es object.__init__ en este caso)
        self.storage = storage
        self.entity_type = "users" 
        self.fernet = self._load_fernet_key_from_file()
        logger.info("Clave Fernet cargada desde archivo en UserRepository.")

    def _load_fernet_key_from_file(self) -> Fernet:
        """
        Carga la clave Fernet desde el archivo 'backend/email.key' o la genera si no existe.
        """
        key_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 
            'email.key' 
        )

        if not os.path.exists(key_file_path):
            logger.error(f"¡ERROR CRÍTICO! La clave Fernet no se encontró en: {key_file_path}")
            logger.error("Asegúrate de que el archivo 'email.key' existe en la carpeta 'backend/' y contiene la clave.")
            try:
                key = Fernet.generate_key()
                with open(key_file_path, "wb") as key_file:
                    key_file.write(key)
                logger.warning(f"Nueva clave Fernet generada y guardada en: {key_file_path}. ¡NO USAR EN PRODUCCIÓN SIN GESTIÓN DE CLAVES!")
            except IOError as e:
                logger.critical(f"No se pudo generar ni guardar la clave Fernet: {e}")
                raise FileNotFoundError(f"Clave Fernet no encontrada y no se pudo generar en {key_file_path}. No se puede iniciar la aplicación.")
            except Exception as e:
                logger.critical(f"Error inesperado al generar clave Fernet: {e}")
                raise 
        else:
            with open(key_file_path, "rb") as key_file:
                key = key_file.read()
            logger.info(f"Clave Fernet cargada exitosamente desde: {key_file_path}")
        
        return Fernet(key)

    def _encrypt_email(self, email: str) -> str:
        """Encripta un email."""
        return self.fernet.encrypt(email.encode()).decode()

    def _decrypt_email(self, encrypted_email: str) -> Optional[str]:
        """Desencripta un email."""
        try:
            if not encrypted_email:
                return None
            return self.fernet.decrypt(encrypted_email.encode()).decode()
        except Exception as e:
            logger.error(f"Error al desencriptar email: {e}")
            return None 

    def get_all_users(self) -> list[User]:
        """
        Recupera todos los usuarios y los convierte a objetos User.
        """
        all_users_data = self.storage.get_all(self.entity_type)
        users = []
        for user_data in all_users_data:
            try:
                if 'email' in user_data and user_data['email']:
                    decrypted_email = self._decrypt_email(user_data['email'])
                    if decrypted_email: 
                        user_data_copy = user_data.copy() 
                        user_data_copy['email'] = decrypted_email
                        users.append(User.from_dict(user_data_copy))
                    else:
                        logger.warning(f"No se pudo desencriptar el email para el usuario ID: {user_data.get('id', 'N/A')}. Se omite.")
                else:
                    users.append(User.from_dict(user_data)) 
            except Exception as e:
                logger.error(f"Error al cargar usuario de datos crudos: {user_data.get('id', 'N/A')}. Error: {e}")
        return users
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Busca un usuario por su ID.
        """
        user_data = self.storage.get_by_id(self.entity_type, user_id)
        if user_data:
            if 'email' in user_data and user_data['email']:
                decrypted_email = self._decrypt_email(user_data['email'])
                if decrypted_email:
                    user_data['email'] = decrypted_email
                else:
                    logger.warning(f"No se pudo desencriptar el email para el usuario ID: {user_id}. El email puede ser None o incorrecto en el objeto User.")
                    user_data['email'] = None 
            return User.from_dict(user_data)
        return None
    
    def find_user_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por su dirección de correo electrónico (desencriptando los almacenados).
        Retorna un objeto User.
        """
        all_users_data = self.storage.get_all(self.entity_type) 
        logger.info(f"Obtenidos {len(all_users_data)} usuarios en formato dict para buscar por email.") 

        for user_data in all_users_data: 
            stored_encrypted_email = user_data.get('email')
            
            if stored_encrypted_email:
                try:
                    decrypted_stored_email = self._decrypt_email(stored_encrypted_email)
                    if decrypted_stored_email == email:
                        user_obj = User.from_dict(user_data)
                        user_obj.email = decrypted_stored_email 
                        logger.info(f"Usuario con email '{email}' encontrado y desencriptado.")
                        return user_obj
                except Exception as e:
                    logger.warning(f"Error al desencriptar email '{stored_encrypted_email}' para búsqueda: {e}")
                    continue 
        logger.info(f"Usuario con email '{email}' no encontrado después de revisar todos los usuarios.") 
        return None
    
    def add_user(self, user: User) -> Optional[User]:
        """
        Añade un nuevo objeto User, encriptando su email y hasheando su contraseña.
        Retorna el objeto User con los datos ya procesados (ID, hasheo, encriptación).
        """
        logger.info(f"Intentando añadir usuario: {user.email}")

        if self.find_user_by_email(user.email): 
            logger.warning(f"Intento de registro con email existente: {user.email}")
            return None

        logger.info("Email no encontrado en el repositorio. Procediendo con el registro.") 

        if user.password and not user.password.startswith('$2b$'): 
            logger.info("Hasheando contraseña...") 
            try:
                hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                user.password = hashed_password
                logger.info("Contraseña hasheada exitosamente.") 
            except Exception as e:
                logger.error(f"Error al hashear la contraseña: {e}")
                return None 
        elif user.password:
            logger.info("Contraseña ya hasheada o no proporcionada.")
        else:
            logger.info("No se proporcionó contraseña (posiblemente registro por Google).")

        if user.email and not ('email' in user.to_dict() and self._is_encrypted(user.email)): 
            logger.info("Encriptando email...") 
            try:
                encrypted_email = self._encrypt_email(user.email)
                user.email = encrypted_email
                logger.info("Email encriptado exitosamente.") 
            except Exception as e:
                logger.error(f"Error al encriptar el email: {e}")
                return None 
        elif user.email:
            logger.info("Email ya encriptado o no se encriptará de nuevo.")
        else:
            logger.info("No se proporcionó email para encriptar.") 

        logger.info("Convirtiendo objeto User a diccionario para guardar...") 
        user_data = user.to_dict()
        logger.info("Objeto User convertido a diccionario. Procediendo a guardar en JSONStorage.") 

        try:
            saved_data = self.storage.save_entity(self.entity_type, user_data)
            logger.info("save_entity en JSONStorage completado.") 
        except Exception as e:
            logger.error(f"ERROR CRÍTICO: Fallo en self.storage.save_entity: {e}") 
            return None

        if saved_data:
            logger.info(f"Usuario {saved_data.get('email', '[email encriptado]')} añadido al repositorio. Desencriptando para retorno.")
            saved_user_obj = User.from_dict(saved_data)
            saved_user_obj.email = self._decrypt_email(saved_user_obj.email) 
            logger.info(f"Usuario {saved_user_obj.email} guardado y desencriptado para retorno.")
            return saved_user_obj
        else:
            logger.error(f"Fallo al guardar el usuario {user.email}.")
            return None
        
    def _is_encrypted(self, text: str) -> bool:
        """Heurística para intentar determinar si un texto podría ser un email encriptado por Fernet."""
        return len(text) > 30 and '-' in text and '=' in text
        
    def find_user_by_email_and_password(self, email: str, password: str) -> Optional[User]:
        """
        Busca un usuario por email y contraseña, desencriptando el email y verificando la contraseña.
        Retorna un objeto User si la autenticación es exitosa.
        """
        user_obj = self.find_user_by_email(email) 
        
        if user_obj and user_obj.password: 
            try:
                if bcrypt.checkpw(password.encode('utf-8'), user_obj.password.encode('utf-8')):
                    logger.info(f"Usuario {email} encontrado y autenticado.")
                    return user_obj
            except ValueError: 
                logger.warning(f"Contraseña almacenada para {email} no es un hash bcrypt válido.")
            except Exception as e:
                logger.error(f"Error al verificar contraseña para {email}: {e}")

        logger.warning(f"Fallo de autenticación para el email: {email}")
        return None
        

    def find_user_by_google_id(self, google_id: str) -> Optional[User]:
        """
        Busca un usuario por su ID de Google.
        Retorna un objeto User.
        """
        users_data = self.storage.find_by_attribute(self.entity_type, "google_id", google_id)
        if users_data:
            user_data = users_data[0] 
            logger.info(f"Usuario de Google con ID {google_id} encontrado.")
            user_obj = User.from_dict(user_data)
            
            if 'email' in user_data and user_data.get('email'):
                decrypted_email = self._decrypt_email(user_data['email'])
                if decrypted_email:
                    user_obj.email = decrypted_email
            return user_obj
        logger.warning(f"Usuario de Google con ID {google_id} no encontrado.")
        return None
        

    def update_user(self, user_id: str, new_data: dict) -> Optional[User]:
        """
        Actualiza un usuario existente. Si el email o la contraseña se actualizan,
        se encriptan/hashean de nuevo.
        Retorna el objeto User actualizado.
        """
        existing_user_data = self.storage.get_by_id(self.entity_type, user_id)
        if not existing_user_data:
            logger.warning(f"No se encontró el usuario con ID {user_id} para actualizar.")
            return None
        
        user_obj = User.from_dict(existing_user_data)

        if 'email' in new_data and new_data['email'] != user_obj.email: 
            current_decrypted_email = self._decrypt_email(user_obj.email)
            if current_decrypted_email != new_data['email']: 
                existing_user_with_new_email = self.find_user_by_email(new_data['email'])
                if existing_user_with_new_email and existing_user_with_new_email.id != user_id:
                    logger.warning(f"Intento de actualizar a un email ya existente para otro usuario: {new_data['email']}")
                    return None
                user_obj.email = self._encrypt_email(new_data['email']) 
            else: 
                logger.info("El nuevo email es el mismo que el actual; no se actualiza.")


        if 'password' in new_data and new_data['password'] and not new_data['password'].startswith('$2b$'):
            logger.info("Hasheando nueva contraseña para actualización...")
            user_obj.password = bcrypt.hashpw(new_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if 'name' in new_data:
            user_obj.name = new_data['name']
        if 'phone_number' in new_data:
            user_obj.phone_number = new_data['phone_number']
        if 'dni' in new_data:
            user_obj.dni = new_data['dni']
        if 'profile_picture_url' in new_data:
            user_obj.profile_picture_url = new_data['profile_picture_url']
        if 'google_id' in new_data: 
            user_obj.google_id = new_data['google_id']

        updated_user_data = user_obj.to_dict()
        
        saved_data = self.storage.save_entity(self.entity_type, updated_user_data)
        if saved_data:
            logger.info(f"Usuario con ID {user_id} actualizado.")
            updated_user_obj = User.from_dict(saved_data)
            updated_user_obj.email = self._decrypt_email(updated_user_obj.email) 
            return updated_user_obj
        else:
            logger.error(f"Fallo al guardar la actualización del usuario con ID {user_id}.")
            return None
        
    def delete_user(self, user_id: str) -> bool:
        """
        Elimina un usuario por su ID.
        """
        return self.storage.delete_entity(self.entity_type, user_id)
        
    