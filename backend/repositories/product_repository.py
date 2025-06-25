# backend/repositories/product_repository.py
import logging
from typing import List, Optional, Dict, Any, Tuple
from backend.models.product import Product
from backend.services.external_product_service import ExternalProductService

logger = logging.getLogger(__name__)

class ProductRepository:
    """
    Repositorio que maneja el almacenamiento y la recuperación de productos.
    Actúa como una capa de abstracción entre la fuente de datos externa 
    y el resto de la aplicación, incluyendo un caché para los datos.
    """
    def __init__(self, external_product_service: ExternalProductService):
        self.external_product_service = external_product_service
        # Caché para almacenar todos los productos obtenidos de la API externa
        # Se guarda como un diccionario para fácil acceso por ID
        self._cache: Dict[str, Product] = {}
        # Lista completa de productos para facilitar la paginación y filtros
        self._all_products_list: List[Product] = [] 
        # Almacena el total de productos reportado por la API externa
        self._total_products_from_api: int = 0
        self._cache_is_loaded = False
        logger.info("ProductRepository inicializado.")

    def _load_cache(self) -> None:
        """
        Carga todos los productos desde el servicio externo al caché.
        Esta operación solo debería realizarse una vez o cuando los datos necesiten ser refrescados.
        """
        if self._cache_is_loaded and self._all_products_list: # Solo cargar si no está cargado o si la lista está vacía
            return

        logger.info("Cargando todos los productos desde la API externa al caché...")
        # El servicio externo ahora se encarga de realizar múltiples llamadas
        # para obtener todos los productos base. Se pide un límite alto para asegurar la recolección inicial.
        all_products_data, total_from_api = self.external_product_service.get_all_products(limit=100) # Un limit=100 a la API base debería traer la primera tanda completa. El servicio luego hace más si es necesario.
        
        self._cache = {}
        self._all_products_list = []
        for product_data in all_products_data:
            try:
                product = Product.from_dict(product_data)
                self._cache[product.id] = product
                self._all_products_list.append(product)
            except Exception as e:
                logger.error(f"Error al procesar producto {product_data.get('id')}: {e}")
        
        self._total_products_from_api = total_from_api 
        self._cache_is_loaded = True
        logger.info(f"Caché de productos cargado. Total de productos en caché: {len(self._all_products_list)}.")
        logger.info(f"Total reportado por la API externa: {self._total_products_from_api}.")


    def get_all_products(self, query: Optional[str] = None, category: Optional[str] = None, 
                             page: int = 1, limit: int = 10) -> Tuple[List[Product], int]:
        """
        Obtiene productos paginados, aplicando filtros de búsqueda y categoría.
        La paginación se realiza localmente sobre la lista completa de productos en caché.
        
        Args:
            query (str, optional): Término de búsqueda.
            category (str, optional): Categoría a filtrar (en formato DummyJSON).
            page (int): Número de página (base 1).
            limit (int): Cantidad de productos por página.

        Returns:
            Tuple[List[Product], int]: Una tupla con la lista de objetos Product para la página actual
                                        y el total de productos *filtrados* disponibles.
        """
        self._load_cache() # Asegura que el caché esté cargado

        filtered_products: List[Product] = []

        # Aplicar filtros
        for product in self._all_products_list:
            matches_query = True
            matches_category = True

            if query:
                # Búsqueda insensible a mayúsculas y minúsculas en nombre y descripción
                if not (query.lower() in product.name.lower() or 
                        (product.description and query.lower() in product.description.lower())):
                    matches_query = False

            if category and category.lower() != "todas las categorias": # Asegurarse de no filtrar si es "todas"
                # Filtrar por categoría
                if product.category.lower() != category.lower():
                    matches_category = False
            
            if matches_query and matches_category:
                filtered_products.append(product)
        
        total_filtered_products = len(filtered_products) # Total después de aplicar los filtros

        # Aplicar paginación LOCALMENTE sobre la lista filtrada
        start_index = (page - 1) * limit
        end_index = start_index + limit
        
        # Asegurarse de que los índices no se salgan de los límites de la lista
        paginated_products = filtered_products[start_index:end_index]

        logger.info(f"Repositorio: Total filtrados: {total_filtered_products}, Paginación (start: {start_index}, end: {end_index}), Productos devueltos: {len(paginated_products)}")

        return paginated_products, total_filtered_products # Devolver la lista paginada y el total filtrado

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """
        Obtiene un producto por su ID.
        Si el producto no está en caché, intenta obtenerlo directamente del servicio externo.
        """
        self._load_cache() # Asegura que el caché esté cargado

        product = self._cache.get(product_id)
        if product:
            logger.info(f"Producto {product_id} encontrado en caché.")
            return product
        
        # Si no está en caché, intentar obtenerlo del servicio externo directamente
        logger.info(f"Producto {product_id} no encontrado en caché, intentando obtener del servicio externo.")
        product_data = self.external_product_service.get_product_by_id(product_id)
        if product_data:
            try:
                product = Product.from_dict(product_data)
                self._cache[product.id] = product
                self._all_products_list.append(product) # Añadirlo a la lista completa también
                logger.info(f"Producto {product_id} obtenido del servicio externo y añadido al caché.")
                return product
            except Exception as e:
                logger.error(f"Error al procesar producto {product_id} obtenido del servicio externo: {e}")
                return None
        logger.warning(f"Producto con ID {product_id} no encontrado ni en caché ni en servicio externo.")
        return None

