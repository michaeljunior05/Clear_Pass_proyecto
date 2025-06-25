# backend/controllers/product_controller.py
import logging
import math
from typing import List, Optional, Tuple, Dict, Any

from backend.services.external_product_service import ExternalProductService 
from backend.repositories.product_repository import ProductRepository
from backend.models.product import Product 

logger = logging.getLogger(__name__)

# Mapeo de tus categorías en español a las categorías reales de DummyJSON
# Nos centraremos en categorías tecnológicas que DummyJSON sí puede filtrar.
# Las que no tienen un equivalente directo se omiten del dropdown para evitar confusiones.
USER_CATEGORY_MAPPING = {
    "todas las categorias": None, # No hay filtro de categoría para "todas"
    "telefonos moviles": "smartphones",
    "computadoras y laptops": "laptops", # Unifica computadoras, notebooks, tablets
}

# Estas son las categorías que se presentarán al frontend en español para el dropdown.
# Deben corresponder a las claves de USER_CATEGORY_MAPPING.
# Esta lista será usada por el endpoint /api/categories
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
        
        api_category = None
        if user_category and user_category.lower() in USER_CATEGORY_MAPPING:
            api_category = USER_CATEGORY_MAPPING[user_category.lower()]
            logger.info(f"Mapeando categoría de usuario '{user_category}' a API category: '{api_category}'")
        elif user_category:
            logger.warning(f"Categoría de usuario '{user_category}' no reconocida en mapeo, no se aplicará filtro de categoría en API.")

        # product_repository.get_all_products ahora devuelve la lista paginada y el total filtrado
        products_list, total_filtered_products = self.product_repository.get_all_products(
            query=query, category=api_category, page=page, limit=limit
        )

        total_pages = 0
        if limit > 0:
            total_pages = math.ceil(total_filtered_products / limit)
        
        # Si hay productos pero total_pages es 0 (ej. total_filtered_products < limit), asegúrate de que sea 1 página.
        if total_pages == 0 and total_filtered_products > 0:
            total_pages = 1 

        logger.info(f"Total de productos filtrados/encontrados: {total_filtered_products}, Páginas calculadas: {total_pages}")
        
        # Devolvemos la lista paginada de productos y el total de productos filtrados (para la paginación del frontend)
        return [product.to_dict() for product in products_list], total_filtered_products

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
