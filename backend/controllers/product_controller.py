import logging
from typing import List, Dict, Optional, Any
# from backend.repositories.product_repository import ProductRepository # ELIMINADO: Ya no es necesaria aquí para evitar circularidad
from backend.models.product import Product 
from config import Config # AÑADIDO: Para acceder a las categorías de tecnología

logger = logging.getLogger(__name__)

class ProductController:
    """
    Controlador encargado de la lógica de negocio relacionada con los productos.
    Actúa como intermediario entre las rutas (routes) y el repositorio (repository).
    Implementa los filtros de negocio (ej. tecnología, importadores chinos) y la paginación.
    """
    def __init__(self, product_repository): # Type hint ProductRepository se puede añadir si la importación no causa problemas
        """
        Inicializa el ProductController.

        Args:
            product_repository: Instancia del repositorio de productos.
        """
        self.product_repository = product_repository
        logger.info("ProductController inicializado.")

        # self.technology_categories = ['electronics'] # ELIMINADO: Ahora se obtiene de Config
        logger.info(f"Categorías de tecnología configuradas (desde Config): {Config.TECHNOLOGY_CATEGORIES}")

    def get_products(self, query: Optional[str] = None, category: Optional[str] = None, 
                     page: int = 1, limit: int = 10) -> Dict[str, Any] | None:
        """
        Obtiene productos aplicando filtros de búsqueda, categoría y paginación.
        Los productos ya están pre-filtrados por "tecnología" en el repositorio.

        Args:
            query (str, optional): Término de búsqueda para filtrar por nombre o descripción.
            category (str, optional): Categoría específica para filtrar.
            page (int): Número de página a recuperar (por defecto 1).
            limit (int): Cantidad de productos por página (por defecto 10).

        Returns:
            Dict[str, Any] | None: Un diccionario que contiene:
                                    - 'products': Una lista de objetos Product mapeados.
                                    - 'total_pages': El número total de páginas.
                                    Retorna un diccionario vacío con lista de productos y 0 páginas si ocurre un error.
        """
        logger.info(f"Obteniendo productos con query='{query}', category='{category}', page={page}, limit={limit}")
        
        all_products_objects = self.product_repository.get_all_products()

        if all_products_objects is None:
            logger.error("No se pudieron obtener productos del repositorio (error en la capa de datos).")
            return {'products': [], 'total_pages': 0}

        filtered_by_query_products = []
        if query:
            query_lower = query.lower()
            filtered_by_query_products = [
                p for p in all_products_objects
                if (p.name and query_lower in p.name.lower()) or 
                   (p.description and query_lower in p.description.lower())
            ]
            logger.info(f"Después del filtro de búsqueda '{query}', quedan {len(filtered_by_query_products)} productos.")
        else:
            filtered_by_query_products = all_products_objects 

        final_filtered_products = []
        if category:
            category_lower = category.lower()
            final_filtered_products = [
                p for p in filtered_by_query_products
                if p.category and p.category.lower() == category_lower
            ]
            logger.info(f"Después del filtro de categoría '{category}', quedan {len(final_filtered_products)} productos.")
        else:
            final_filtered_products = filtered_by_query_products

        total_products_count = len(final_filtered_products)
        total_pages = (total_products_count + limit - 1) // limit if total_products_count > 0 else 1
        
        adjusted_page = max(1, page) 
        start_index = (adjusted_page - 1) * limit
        end_index = start_index + limit
        paginated_products = final_filtered_products[start_index:end_index]

        logger.info(f"Mostrando {len(paginated_products)} productos para la página {adjusted_page} de {total_pages}. Total de productos filtrados: {total_products_count}")
        
        products_as_dict = [p.to_dict() for p in paginated_products]

        return {'products': products_as_dict, 'total_pages': total_pages}

    def get_product_details(self, product_id: str) -> Product | None:
        """
        Obtiene los detalles de un producto específico por su ID.
        El repositorio ya se encarga de obtener y validar el producto como "tecnología".

        Args:
            product_id (str): El ID del producto a buscar.

        Returns:
            Product | None: Objeto Product si se encuentra y cumple los criterios de tecnología, o None si no.
        """
        logger.info(f"Obteniendo detalles para el producto ID: {product_id}")
        product_obj = self.product_repository.get_product_by_id(product_id)

        if product_obj:
            logger.info(f"Detalles del producto ID {product_id} obtenidos exitosamente (ya procesado por repo).")
            return product_obj
        else:
            logger.warning(f"No se encontraron datos para el producto ID: {product_id} o no es una categoría tecnológica válida.")
            return None

    def get_product_categories(self) -> List[str]:
        """
        Obtiene una lista de todas las categorías de productos disponibles.
        Utiliza los productos ya pre-filtrados por tecnología del repositorio.

        Returns:
            List[str]: Una lista de cadenas con los nombres de las categorías únicas, ordenadas alfabéticamente.
        """
        logger.info("Solicitando todas las categorías de productos (desde productos ya filtrados por tecnología).")
        all_products_objects = self.product_repository.get_all_products()
        
        if all_products_objects is None:
            logger.error("No se pudieron obtener productos para extraer categorías.")
            return []

        categories = set()
        for product_obj in all_products_objects:
            # Ahora usamos Config.TECHNOLOGY_CATEGORIES aquí también si fuera necesario filtrar.
            # En este caso, get_all_products del repo ya filtra por tecnología.
            if product_obj.category:
                categories.add(product_obj.category.lower()) 

        sorted_categories = sorted(list(categories))
        logger.info(f"Categorías de tecnología disponibles: {sorted_categories}")
        return sorted_categories

    def clear_product_cache(self):
        """
        Llama al método del repositorio para invalidar la caché de productos.
        """
        logger.info("Solicitando invalidación de la caché de productos al repositorio.")
        self.product_repository.clear_cache()
