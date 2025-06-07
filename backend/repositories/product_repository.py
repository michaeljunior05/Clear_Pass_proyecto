import logging
from typing import List, Dict, Optional, Any
import time 

from backend.models.product import Product 
from config import Config # AÑADIDO: Para acceder a las categorías de tecnología
# from backend.controllers.product_controller import ProductController # ELIMINADO: Ya no es necesaria aquí para evitar circularidad

logger = logging.getLogger(__name__)

class ProductRepository:
    """
    Repositorio para acceder a los datos de productos.
    Actúa como una capa de abstracción entre el controlador y la fuente de datos (ExternalProductService).
    Implementa un mecanismo de caché en memoria para reducir las llamadas a la API externa.
    La caché almacena objetos Product ya pre-filtrados por categorías de tecnología.
    """
    def __init__(self, external_product_service): # ELIMINADO: product_controller ya no es un parámetro
        """
        Inicializa ProductRepository.

        Args:
            external_product_service: Instancia de ExternalProductService.
        """
        self.external_product_service = external_product_service
        # self.product_controller = product_controller # ELIMINADO
        
        self._product_cache: List[Product] | None = None 
        self._cache_timestamp: float | None = None
        self._cache_duration: int = 300  
        logger.info("ProductRepository inicializado con caché en memoria (almacenará objetos Product filtrados).")

    def get_all_products(self) -> List[Product] | None: 
        """
        Obtiene todos los productos de la fuente externa, utilizando una caché en memoria.
        Si la caché está fresca, devuelve los datos de la caché; de lo contrario,
        hace una nueva llamada a la API externa, los filtra por tecnología, los mapea a objetos Product
        y actualiza la caché.

        Returns:
            List[Product] | None: Una lista de objetos Product (ya filtrados por tecnología),
                                  o None si no se pudieron obtener los datos.
        """
        if self._product_cache is not None and self._cache_timestamp is not None:
            if (time.time() - self._cache_timestamp) < self._cache_duration:
                logger.info("Devolviendo productos desde la caché en memoria (ya filtrados y mapeados).")
                return self._product_cache
            else:
                logger.info("Caché de productos expirada. Refrescando...")
        else:
            logger.info("Caché de productos vacía o no inicializada. Cargando y procesando productos.")

        raw_products_data = self.external_product_service.get_all_products()
        
        if raw_products_data is None:
            logger.warning("ExternalProductService no pudo obtener productos crudos. Caché no actualizada.")
            return None 

        processed_products: List[Product] = []
        for product_data in raw_products_data:
            try:
                product_obj = Product.from_dict(product_data)
                # AHORA USAMOS Config.TECHNOLOGY_CATEGORIES
                if product_obj.category and product_obj.category.lower() in Config.TECHNOLOGY_CATEGORIES:
                    product_obj.origin = "China" 
                    processed_products.append(product_obj)
            except ValueError as ve:
                logger.warning(f"Producto inválido saltado durante el llenado de caché: ID {product_data.get('id')} - Error: {ve}")
                continue 
            except Exception as e:
                logger.error(f"Error inesperado al procesar producto para caché ID {product_data.get('id')}: {e}", exc_info=True)
                continue

        self._product_cache = processed_products
        self._cache_timestamp = time.time()
        logger.info(f"Caché de productos actualizada con {len(processed_products)} objetos Product (filtrados por tecnología).")
        return self._product_cache

    def get_product_by_id(self, product_id: str) -> Product | None: 
        """
        Obtiene un producto específico por su ID.
        Primero intenta buscar en la caché de todos los productos (ya filtrados y mapeados).
        Si no lo encuentra, llama directamente al servicio externo y lo procesa.

        Args:
            product_id (str): El ID del producto.

        Returns:
            Product | None: Objeto Product si se encuentra, o None si no se encontró
                            o si ocurrió un error.
        """
        logger.info(f"Solicitando producto ID {product_id}.")
        
        if self._product_cache:
            for product_obj in self._product_cache:
                if str(product_obj.id) == str(product_id):
                    logger.info(f"Producto ID {product_id} encontrado en la caché (objeto Product).")
                    return product_obj
        
        logger.info(f"Producto ID {product_id} no encontrado en caché. Llamando a servicio externo para un solo producto.")
        product_data = self.external_product_service.get_product_by_id(product_id)
        
        if product_data is None:
            logger.warning(f"ExternalProductService no encontró producto ID {product_id} o hubo un error.")
            return None
        
        try:
            product_obj = Product.from_dict(product_data)
            # AHORA USAMOS Config.TECHNOLOGY_CATEGORIES
            if product_obj.category and product_obj.category.lower() in Config.TECHNOLOGY_CATEGORIES:
                product_obj.origin = "China" 
                logger.info(f"ProductRepository recibió y procesó el producto ID {product_id} del servicio externo.")
                return product_obj
            else:
                logger.warning(f"Producto ID {product_id} obtenido de API externa no es de categoría tecnológica. Ignorado.")
                return None
        except ValueError as ve:
            logger.error(f"Error al mapear datos del producto {product_id} a objeto Product desde API externa: {ve}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al procesar producto ID {product_id} de API externa: {e}", exc_info=True)
            return None

    def clear_cache(self):
        """
        Invalida la caché de productos en memoria, forzando un refresco desde la API externa
        en la próxima solicitud de productos.
        """
        self._product_cache = None
        self._cache_timestamp = None
        logger.info("Caché de productos invalidada manualmente.")

