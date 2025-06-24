# backend/models/user.py
import uuid
from datetime import datetime
import bcrypt
from typing import Optional, Dict, Any # <--- ¡IMPORTAR Dict y Any AQUÍ!

class User:
    """
    Representa un usuario en el sistema.
    """
    def __init__(self, _id: Optional[str] = None, email: Optional[str] = None, 
                 password: Optional[str] = None, name: Optional[str] = None, 
                 profile_picture_url: Optional[str] = None, google_id: Optional[str] = None,
                 phone_number: Optional[str] = None, dni: Optional[str] = None, # <--- ¡AÑADIDOS AQUÍ!
                 is_premium: bool = False, # <--- ¡AÑADIDO AQUÍ!
                 created_at: Optional[str] = None, updated_at: Optional[str] = None):
        
        self._id = str(uuid.uuid4()) if _id is None else _id
        self._email = email
        self._password = password
        self._name = name
        self._profile_picture_url = profile_picture_url
        self._google_id = google_id 
        self._phone_number = phone_number # <--- Asignar
        self._dni = dni # <--- Asignar
        self._is_premium = is_premium # <--- Asignar
        self._created_at = created_at if created_at else datetime.now().isoformat()
        self._updated_at = updated_at if updated_at else datetime.now().isoformat()


    @property
    def id(self) -> str:
        return self._id

    @property
    def email(self) -> Optional[str]:
        return self._email

    @email.setter
    def email(self, value: Optional[str]):
        self._email = value
        self._updated_at = datetime.now().isoformat()

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: Optional[str]):
        self._name = value
        self._updated_at = datetime.now().isoformat()

    @property
    def profile_picture_url(self) -> Optional[str]:
        return self._profile_picture_url

    @profile_picture_url.setter
    def profile_picture_url(self, value: Optional[str]):
        self._profile_picture_url = value
        self._updated_at = datetime.now().isoformat()

    @property
    def password(self) -> Optional[str]:
        return self._password

    @password.setter
    def password(self, value: Optional[str]):
        self._password = value
        self._updated_at = datetime.now().isoformat()

    @property
    def google_id(self) -> Optional[str]: 
        return self._google_id

    @google_id.setter 
    def google_id(self, value: Optional[str]):
        self._google_id = value
        self._updated_at = datetime.now().isoformat()

    @property
    def phone_number(self) -> Optional[str]: 
        return self._phone_number

    @phone_number.setter 
    def phone_number(self, value: Optional[str]):
        self._phone_number = value
        self._updated_at = datetime.now().isoformat()

    @property
    def dni(self) -> Optional[str]: 
        return self._dni

    @dni.setter 
    def dni(self, value: Optional[str]):
        self._dni = value
        self._updated_at = datetime.now().isoformat()

    @property
    def is_premium(self) -> bool: 
        return self._is_premium

    @is_premium.setter 
    def is_premium(self, value: bool):
        self._is_premium = value
        self._updated_at = datetime.now().isoformat()

    def set_password(self, password: str):
        self._password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self._updated_at = datetime.now().isoformat()

    def check_password(self, password: str) -> bool:
        if not self._password: 
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self._password.encode('utf-8'))

    def to_dict(self) -> Dict[str, Any]: # <--- Usa Dict y Any
        """Convierte el objeto User a un diccionario para almacenamiento o respuesta API."""
        return {
            "id": self.id,
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "profile_picture_url": self.profile_picture_url,
            "google_id": self.google_id,
            "phone_number": self.phone_number, 
            "dni": self.dni, 
            "is_premium": self.is_premium, 
            "created_at": self._created_at,
            "updated_at": self._updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]): # <--- Usa Dict y Any
        """Crea un objeto User desde un diccionario de datos."""
        email_val = data.get("email")
        if email_val is None:
            raise ValueError("Email is required to create a User object from dictionary.")

        user = cls(
            _id=data.get("id"),
            email=email_val,
            password=data.get("password"),
            name=data.get("name"),
            profile_picture_url=data.get("profile_picture_url"),
            google_id=data.get("google_id"),
            phone_number=data.get("phone_number"), 
            dni=data.get("dni"), 
            is_premium=data.get("is_premium", False), 
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        return user

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', name='{self.name}', google_id='{self.google_id}')>"
