# backend/repositories/product_repository.py
import logging
from typing import List, Dict, Optional, Any

from backend.models.product import Product # Importamos nuestro modelo Product
from backend.services.external_product_service import ExternalProductService 

logger = logging.getLogger(__name__)

class ProductRepository:
    """
    Repositorio para gestionar la obtención y el mapeo de datos de productos
    desde una fuente externa (a través de ExternalProductService).
    Actúa como una capa de abstracción entre el ProductController y el ExternalProductService.
    """
    def __init__(self, external_product_service: ExternalProductService): # AHORA DEPENDE DEL SERVICIO
        """
        Inicializa el ProductRepository.

        Args:
            external_product_service (ExternalProductService): Una instancia del servicio para realizar solicitudes a la API externa.
        """
        self.external_product_service = external_product_service
        logger.info("ProductRepository inicializado.")

    def get_all_products(self, query: str = None, category: str = None, limit: int = None) -> List[Product]:
        """
        Obtiene productos de la API externa y los mapea a objetos Product.
        Soporta filtrado por categoría y limitación de resultados.

        Args:
            query (str, optional): Término de búsqueda (no soportado por FakeStoreAPI directamente en el listado).
            category (str, optional): Filtra productos por categoría.
            limit (int, optional): Limita el número de resultados.

        Returns:
            list[Product]: Una lista de objetos Product.
        """
        products_data = None
        if category:
            # Si hay categoría, usar el método específico del servicio
            products_data = self.external_product_service.get_products_by_category(category)
        else:
            # Si no hay categoría, obtener todos los productos
            products_data = self.external_product_service.get_all_products()

        products = []
        if products_data:
            # Aplicar limit si existe y si la API no lo hace (FakeStoreAPI sí lo hace en la URL pero en este modelo lo manejamos)
            if limit is not None and limit > 0:
                products_data = products_data[:limit] # Aplicar el límite a la lista de datos

            for item in products_data:
                try:
                    product = Product.from_dict(item)
                    products.append(product)
                except ValueError as ve:
                    logger.error(f"Error de mapeo en get_all_products: {ve}, datos originales: {item}")
                except Exception as e:
                    logger.error(f"Error inesperado al mapear un producto en get_all_products: {e}, datos: {item}", exc_info=True)
        
        logger.info(f"Se obtuvieron y mapearon {len(products)} productos.")
        return products

    def get_product_by_id(self, product_id: str) -> Product | None:
        """
        Obtiene un producto específico por su ID de la API externa y lo mapea a un objeto Product.

        Args:
            product_id (str): El ID del producto (el ID de la API externa).

        Returns:
            Product | None: Un objeto Product si se encuentra, o None si no.
        """
        try:
            # Convertir a int si es necesario para el servicio, aunque la ruta lo pase como str
            product_id_int = int(product_id) 
        except ValueError:
            logger.error(f"ID de producto inválido: {product_id}. Debe ser un número.")
            return None

        data = self.external_product_service.get_product_by_id(product_id_int) # Usar el servicio

        if data:
            try:
                product = Product.from_dict(data)
                logger.info(f"Producto con ID {product_id} obtenido y mapeado exitosamente.")
                return product
            except ValueError as ve:
                logger.error(f"Error de mapeo para el producto {product_id}: {ve}, datos: {data}")
            except Exception as e:
                logger.error(f"Error inesperado al mapear el producto {product_id}: {e}, datos: {data}", exc_info=True)
        logger.warning(f"No se encontró el producto con ID {product_id} en la API externa o hubo un problema.")
        return None