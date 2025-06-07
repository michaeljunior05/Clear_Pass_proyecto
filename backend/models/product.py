# backend/models/product.py
import uuid
from datetime import datetime
from typing import Dict, Any, Optional # Importaciones adicionales para typing

class Product:
    """
    Modelo de datos para un producto.
    """
    def __init__(self, _id=None, name: str = None, price: float = None,
                 description: str = None, category: str = None,
                 image_url: str = None, rating: dict = None, external_id: str = None):
        """
        Inicializa una instancia de Product.

        Args:
            _id (str, optional): ID interno del producto. Si es None, se genera un UUID.
            name (str): Nombre del producto.
            price (float): Precio del producto.
            description (str): Descripción del producto.
            category (str): Categoría del producto.
            image_url (str): URL de la imagen del producto.
            rating (dict): Diccionario con la calificación (ej. {'rate': 3.9, 'count': 120}).
            external_id (str, optional): ID del producto en la API externa, si aplica.
        """
        self._id = str(uuid.uuid4()) if _id is None else _id
        self._name = name
        self._price = price
        self._description = description
        self._category = category
        self._image_url = image_url
        self._rating = rating if rating is not None else {'rate': 0.0, 'count': 0}
        self._external_id = external_id # ID del producto en la API externa
        self._created_at = datetime.now().isoformat()
        self._updated_at = datetime.now().isoformat()

    @property
    def id(self):
        return self._id

    @property
    def external_id(self):
        return self._external_id

    @external_id.setter
    def external_id(self, value):
        self._external_id = value
        self._updated_at = datetime.now().isoformat()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._updated_at = datetime.now().isoformat()

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value
        self._updated_at = datetime.now().isoformat()

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value
        self._updated_at = datetime.now().isoformat()

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value
        self._updated_at = datetime.now().isoformat()

    @property
    def image_url(self):
        return self._image_url

    @image_url.setter
    def image_url(self, value):
        self._image_url = value
        self._updated_at = datetime.now().isoformat()

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = value
        self._updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]: # Añadido tipo de retorno
        """
        Convierte el objeto Product a un diccionario.
        """
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "category": self.category,
            "image_url": self.image_url, # Usar image_url aquí
            "rating": self.rating,
            "external_id": self.external_id,
            "created_at": self._created_at,
            "updated_at": self._updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]): # Añadido tipo de argumento
        """
        Crea una instancia de Product a partir de un diccionario (ej. de una API externa).
        Mapea los nombres de campo de la API a los atributos del modelo.
        """
        # Mapeo de campos de la API externa (ej. FakeStoreAPI o storerestapi.com) a nuestros atributos
        # Asegurarse de que los campos existan y mapearlos correctamente
        _id = data.get("id") 
        name = data.get("title") # La API usa 'title' para el nombre
        price = data.get("price")
        description = data.get("description")
        category = data.get("category")
        image_url = data.get("image") # La API usa 'image' para la URL de la imagen
        rating = data.get("rating")

        # --- VALIDACIÓN CLAVE AQUÍ ---
        # Lista de campos esenciales que deben estar presentes y no ser None
        essential_fields = {
            "id": _id,
            "name": name,
            "price": price,
            "description": description,
            "category": category,
            "image_url": image_url
        }

        for field_name, field_value in essential_fields.items():
            if field_value is None:
                raise ValueError(f"Datos incompletos para crear un producto. Falta el campo esencial '{field_name}'. Datos originales: {data}")
        
        # Convertir price a float de forma segura
        try:
            price = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"El precio del producto no es un número válido: '{price}'. Datos originales: {data}")

        # Manejar el rating: si no es un diccionario o es None, usar el valor por defecto
        if not isinstance(rating, dict) or rating is None:
            rating = {'rate': 0.0, 'count': 0}
        else:
            # Asegurarse de que 'rate' y 'count' son los tipos correctos dentro de rating
            try:
                rating['rate'] = float(rating.get('rate', 0.0))
                rating['count'] = int(rating.get('count', 0))
            except (ValueError, TypeError):
                # Si el formato del rating es incorrecto, usar el valor por defecto
                rating = {'rate': 0.0, 'count': 0}


        # Crear la instancia de Product usando los nombres de argumento del constructor
        return cls(
            _id=str(_id), # Asegurarse de que el ID es un string
            name=name,
            price=price,
            description=description,
            category=category,
            image_url=image_url, 
            rating=rating,
            external_id=str(_id) # Usar el mismo ID como external_id si no hay otro específico
        )

    def __repr__(self):
        return f"<Product {self.name} (ID: {self.id})>"