import logging
from typing import List, Dict, Any, Tuple, Optional
from backend.repositories.product_repository import ProductRepository
from backend.models.product import Product # Asegurarse de importar Product
import time 

logger = logging.getLogger(__name__)

class ProductController:
    """
    Controlador para la lógica de negocio relacionada con productos.
    Gestiona la recuperación, filtrado y paginación de productos.
    """
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        logger.info("ProductController inicializado.")

    def get_paginated_products(self, query: str = "", category: str = "", page: int = 1, limit: int = 10) -> Tuple[List[Dict[str, Any]], int]:
        """
        Recupera productos paginados, aplicando filtros de búsqueda y categoría.
        """
        start_time = time.time()
        logger.info(f"Iniciando get_paginated_products con query='{query}', category='{category}', page={page}, limit={limit}")

        all_products: List[Product] = self.product_repository.get_all_products() # Ahora devuelve objetos Product
        logger.info(f"Total de productos recuperados del repositorio (antes de filtrar): {len(all_products)}")

        filtered_products = all_products

        # Aplicar filtro por categoría si se proporciona
        if category:
            logger.info(f"Aplicando filtro por categoría: {category}")
            # Accede a 'category' como un atributo del objeto Product
            filtered_products = [
                p for p in filtered_products if p.category.lower() == category.lower()
            ]
            logger.info(f"Productos después de filtrar por categoría: {len(filtered_products)}")

        # Aplicar filtro de búsqueda si se proporciona (case-insensitive)
        if query:
            logger.info(f"Aplicando filtro por query: {query}")
            query_lower = query.lower()
            # Accede a 'name' y 'description' como atributos del objeto Product
            filtered_products = [
                p for p in filtered_products 
                if query_lower in p.name.lower() or 
                   query_lower in p.description.lower()
            ]
            logger.info(f"Productos después de filtrar por query: {len(filtered_products)}")

        total_products = len(filtered_products)
        total_pages = (total_products + limit - 1) // limit

        # Calcular el rango para la paginación
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_products_objs = filtered_products[start_index:end_index]
        
        # CONVERTIR OBJETOS PRODUCT A DICCIONARIOS ANTES DE DEVOLVER
        paginated_products = [p.to_dict() for p in paginated_products_objs]
        
        end_time = time.time()
        duration = (end_time - start_time) * 1000
        logger.info(f"get_paginated_products completado en {duration:.2f} ms. Devolviendo {len(paginated_products)} productos en la página {page}.")

        return paginated_products, total_pages

    def get_categories(self) -> List[str]:
        """
        Recupera una lista de todas las categorías únicas de productos.
        """
        logger.info("Recuperando categorías únicas de productos.")
        all_products: List[Product] = self.product_repository.get_all_products() # Devuelve objetos Product
        # Accede a 'category' como un atributo del objeto Product
        categories = sorted(list(set(p.category for p in all_products if p.category)))
        logger.info(f"Categorías únicas encontradas: {len(categories)}")
        return categories

    def get_product_detail(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Recupera los detalles de un producto específico por su ID.
        """
        logger.info(f"Recuperando detalles para el producto ID: {product_id}")
        product_obj: Optional[Product] = self.product_repository.get_product_by_id(product_id) # Devuelve objeto Product
        if product_obj:
            logger.info(f"Detalles del producto {product_id} encontrados.")
            return product_obj.to_dict() # CONVERTIR A DICCIONARIO ANTES DE DEVOLVER
        else:
            logger.warning(f"Producto con ID {product_id} no encontrado.")
            return None
