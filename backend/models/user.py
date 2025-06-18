# backend/models/user.py
import uuid
from datetime import datetime
import bcrypt

class User:
    def __init__(self, _id=None, email=None, password=None, name=None, profile_picture_url=None, google_id=None): # Añadir google_id
        self._id = str(uuid.uuid4()) if _id is None else _id
        self._email = email
        self._password = password
        self._name = name
        self._profile_picture_url = profile_picture_url
        self._google_id = google_id # Nuevo atributo para Google ID
        self._created_at = datetime.now().isoformat()
        self._updated_at = datetime.now().isoformat()




    @property
    def id(self):
        return self._id

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value
        self._updated_at = datetime.now().isoformat()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._updated_at = datetime.now().isoformat()

    @property
    def profile_picture_url(self):
        return self._profile_picture_url

    @profile_picture_url.setter
    def profile_picture_url(self, value):
        self._profile_picture_url = value
        self._updated_at = datetime.now().isoformat()

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = value
        self._updated_at = datetime.now().isoformat()

    @property
    def google_id(self): # Nuevo getter para google_id
        return self._google_id

    @google_id.setter # Nuevo setter para google_id
    def google_id(self, value):
        self._google_id = value
        self._updated_at = datetime.now().isoformat()

    def set_password(self, password):
        self._password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self._updated_at = datetime.now().isoformat()

    def check_password(self, password):
        if not self._password: # Usuario registrado con Google no tendrá password
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self._password.encode('utf-8'))

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "password": self.password,
            "name": self.name,
            "profile_picture_url": self.profile_picture_url,
            "google_id": self.google_id, # Incluir google_id en el diccionario
            "created_at": self._created_at,
            "updated_at": self._updated_at
        }

    @classmethod
    def from_dict(cls, data):
        user = cls(
            _id=data.get("id"),
            email=data.get("email"),
            password=data.get("password"),
            name=data.get("name"),
            profile_picture_url=data.get("profile_picture_url"),
            google_id=data.get("google_id") # Cargar google_id desde el diccionario
        )
        user._created_at = data.get("created_at", datetime.now().isoformat())
        user._updated_at = data.get("updated_at", datetime.now().isoformat())
        return user

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}', name='{self.name}', google_id='{self.google_id}')>"


