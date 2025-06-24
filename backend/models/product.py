# backend/models/product.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class Product:
    """
    Representa un producto, mapeando datos de la API externa (DummyJSON) a una estructura consistente.
    """
    id: str # ID interno, que será el ID de DummyJSON
    name: str
    description: str
    price: float
    category: str
    image_url: str 
    rating: float 
    rating_count: int 
    
    external_id: Optional[Any] = None # En este caso, será el mismo que 'id'
    source_api: Optional[str] = "dummyjson" # Ya sabemos que la fuente es DummyJSON

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto Product a un diccionario."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "image_url": self.image_url,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "external_id": self.external_id,
            "source_api": self.source_api
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        """
        Crea un objeto Product desde un diccionario de datos.
        Adapta los nombres de campos de DummyJSON.com.
        """
        product_id = str(data.get("id"))
        
        name = data.get("title")
        description = data.get("description", "")
        price = float(data.get("price", 0.0))
        category = data.get("category", "")
        
        image_url = data.get("thumbnail") 
        if not image_url:
            images_list = data.get("images")
            if isinstance(images_list, list) and len(images_list) > 0:
                image_url = images_list[0] 
        
        if not image_url:
            image_url = "https://placehold.co/300x300/e0e0e0/000000?text=No+Image"
            
        # === INICIO DE LA CORRECCIÓN ===
        rating_raw = data.get("rating", 0.0) # Obtener el valor de 'rating', puede ser un float o un dict
        
        rating = 0.0
        rating_count = 0

        if isinstance(rating_raw, dict):
            # Si es un diccionario (formato {"rate": X, "count": Y})
            rating = float(rating_raw.get("rate", 0.0))
            rating_count = int(rating_raw.get("count", 0))
        else:
            # Si es un float directamente (formato X.X)
            rating = float(rating_raw)
            rating_count = 0 # No hay un 'count' explícito en este caso
        # === FIN DE LA CORRECCIÓN ===

        return Product(
            id=product_id,
            name=name,
            description=description,
            price=price,
            category=category,
            image_url=image_url,
            rating=rating,
            rating_count=rating_count,
            external_id=product_id,
            source_api="dummyjson"
        )
