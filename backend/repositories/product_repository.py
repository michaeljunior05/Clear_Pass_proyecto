# backend/repositories/product_repository.py
import logging
from typing import List, Dict, Any, Optional
from backend.services.external_product_service import ExternalProductService
from backend.models.product import Product # Importar la clase Product

logger = logging.getLogger(__name__)

class ProductRepository:
    """
    Repositorio para gestionar la obtención y almacenamiento (caché) de productos.
    Interactúa con ExternalProductService para obtener datos y los almacena en caché.
    """
    def __init__(self, external_product_service: ExternalProductService):
        self.external_product_service = external_product_service
        self.cache: Dict[int, Product] = {} # Caché en memoria para objetos Product
        logger.info("ProductRepository inicializado con caché en memoria (almacenará objetos Product filtrados).")

    def get_all_products(self) -> List[Product]: # Tipo de retorno cambiado a List[Product]
        """
        Recupera todos los productos de la API externa o de la caché.
        Devuelve una lista de objetos Product.
        """
        if not self.cache: # Si la caché está vacía, cargar desde la API externa
            logger.info("Caché de productos vacía. Obteniendo productos de la API externa.")
            raw_products_data = self.external_product_service.get_all_products()
            # Convertir los diccionarios raw a objetos Product y poblar la caché
            for item in raw_products_data:
                product_obj = Product.from_dict(item) # Usa from_dict para crear objeto Product
                self.cache[product_obj.id] = product_obj
            logger.info(f"Caché de productos poblada con {len(self.cache)} productos.")
        else:
            logger.info(f"Productos obtenidos desde la caché. Total: {len(self.cache)}")
        
        return list(self.cache.values()) # Devolver una lista de objetos Product


    def get_product_by_id(self, product_id: int) -> Optional[Product]: # Tipo de retorno cambiado a Optional[Product]
        """
        Recupera un producto por su ID de la API externa o de la caché.
        Devuelve un objeto Product.
        """
        product_obj = self.cache.get(product_id)
        if product_obj:
            logger.info(f"Producto con ID {product_id} encontrado en caché.")
            return product_obj
        else:
            logger.info(f"Producto con ID {product_id} no encontrado en caché. Obteniendo de la API externa.")
            raw_product_data = self.external_product_service.get_product_by_id(product_id)
            if raw_product_data:
                product_obj = Product.from_dict(raw_product_data) # Usa from_dict para crear objeto Product
                self.cache[product_obj.id] = product_obj # Añadir a la caché
                logger.info(f"Producto con ID {product_id} obtenido de la API externa y añadido a caché.")
                return product_obj
            logger.warning(f"Producto con ID {product_id} no encontrado en la API externa.")
            return None
