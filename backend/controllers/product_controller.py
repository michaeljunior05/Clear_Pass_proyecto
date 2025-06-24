# backend/controllers/product_controller.py
import logging
import math
from typing import List, Optional, Tuple, Dict, Any

from backend.services.external_product_service import ExternalProductService 
from backend.repositories.product_repository import ProductRepository
from backend.models.product import Product 

logger = logging.getLogger(__name__)

# Mapeo de tus categorías en español a las categorías reales de DummyJSON
USER_CATEGORY_MAPPING = {
    "todas las categorias": None, # No hay filtro de categoría para "todas"
    "telefonos moviles": "smartphones",
    "camaras digitales": None, # DummyJSON no tiene esta categoría específica
    "televisores": None, # DummyJSON no tiene esta categoría específica
    "impresoras": None, # DummyJSON no tiene esta categoría específica
    "consolas y accesorios": None, # DummyJSON no tiene esta categoría específica
    "tablets": "laptops", # Las tablets suelen agruparse con laptops en DummyJSON
    "computadoras": "laptops",
    "notebooks": "laptops",
    "electrodomesticos": "home-decoration" # Usamos una categoría genérica si no hay una perfecta
}

# Puedes definir aquí las categorías que se presentarán al frontend en español
# Estas son las que tu frontend debería mostrar como opciones
FRONTEND_DISPLAY_CATEGORIES = list(USER_CATEGORY_MAPPING.keys())

class ProductController:
    """
    Controlador para gestionar la lógica de negocio relacionada con productos.
    Interactúa con el repositorio de productos para obtener datos.
    """
    def __init__(self, external_product_service: ExternalProductService):
        self.product_repository = ProductRepository(external_product_service)
        logger.info("ProductController inicializado.")

    def get_products(self, query: Optional[str] = None, user_category: Optional[str] = None, 
                     page: int = 1, limit: int = 10) -> Tuple[List[Dict[str, Any]], int]:
        logger.info(f"Solicitando productos - Query: '{query}', Categoría de Usuario: '{user_category}', Página: {page}, Límite: {limit}")
        
        # Mapear la categoría de usuario a la categoría de la API de DummyJSON
        api_category = None
        if user_category and user_category.lower() in USER_CATEGORY_MAPPING:
            api_category = USER_CATEGORY_MAPPING[user_category.lower()]
            logger.info(f"Mapeando categoría de usuario '{user_category}' a API category: '{api_category}'")
        elif user_category:
            logger.warning(f"Categoría de usuario '{user_category}' no reconocida, no se aplicará filtro de categoría.")

        products_list, total_products = self.product_repository.get_all_products(
            query=query, category=api_category, page=page, limit=limit
        )

        total_pages = 0
        if limit > 0:
            total_pages = math.ceil(total_products / limit)
        if total_pages == 0 and len(products_list) > 0:
            total_pages = 1 # Si hay productos, al menos hay 1 página

        return [product.to_dict() for product in products_list], total_pages

    def get_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        logger.info(f"Solicitando detalle de producto para ID: {product_id}")
        product = self.product_repository.get_product_by_id(product_id)
        if product:
            return product.to_dict()
        return None

    def get_categories(self) -> List[str]:
        """
        Devuelve la lista de categorías personalizadas en español para el frontend.
        """
        logger.info("Solicitando categorías de productos personalizadas para el frontend.")
        return FRONTEND_DISPLAY_CATEGORIES