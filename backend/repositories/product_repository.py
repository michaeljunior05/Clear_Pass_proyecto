# backend/repositories/product_repository.py
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from backend.services.external_product_service import ExternalProductService 
from backend.models.product import Product

logger = logging.getLogger(__name__)

# NOTA IMPORTANTE: Esta clase ya NO hereda de BaseRepository
class ProductRepository: 
    """
    Gestiona la persistencia y acceso a los datos de productos, incluyendo
    una caché en memoria y la interacción con la API de productos externa única (DummyJSON).
    """
    def __init__(self, external_product_service: ExternalProductService):
        # No se llama a super().__init__() porque no hereda de BaseRepository,
        # solo se inicializa object directamente si no hay otra herencia.
        self.external_product_service = external_product_service
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self.cache_duration = timedelta(minutes=5)
        # self.entity_type = "products" # No es estrictamente necesario aquí si no usa JSONStorage para productos
        logger.info("ProductRepository inicializado.")

    def _get_cache_key(self, query: Optional[str] = None, category: Optional[str] = None, 
                       page: int = 1, limit: int = 10) -> str:
        query_str = query if query is not None else ""
        category_str = category if category is not None else ""
        return f"products_q{query_str}_cat{category_str}_p{page}_l{limit}"

    def get_all_products(self, query: Optional[str] = None, category: Optional[str] = None, 
                         page: int = 1, limit: int = 10) -> Tuple[List[Product], int]:
        cache_key = self._get_cache_key(query, category, page, limit)

        if cache_key in self._cache and (datetime.now() - self._cache_timestamp[cache_key]) < self.cache_duration:
            logger.info(f"Devolviendo productos desde caché para clave: {cache_key}")
            cached_data = self._cache[cache_key]
            return list(cached_data['products']), cached_data['total_products']

        logger.info(f"Obteniendo productos de la API externa (DummyJSON) para clave: {cache_key}")
        
        skip = (page - 1) * limit
        
        products_data_raw, total_products = self.external_product_service.get_all_products(
            query=query, category=category, limit=limit, skip=skip
        )

        if not products_data_raw: 
            logger.warning("No se pudieron obtener productos de la API externa o la lista está vacía.")
            return [], 0

        products = [Product.from_dict(item) for item in products_data_raw]

        self._cache[cache_key] = {'products': products, 'total_products': total_products}
        self._cache_timestamp[cache_key] = datetime.now()
        logger.info(f"Productos guardados en caché para clave: {cache_key}")

        return products, total_products

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        cache_key = f"product_detail_{product_id}"

        if cache_key in self._cache and (datetime.now() - self._cache_timestamp[cache_key]) < self.cache_duration:
            logger.info(f"Devolviendo detalle de producto desde caché para ID: {product_id}")
            return self._cache[cache_key]

        logger.info(f"Obteniendo detalle de producto de la API externa para ID: {product_id}")
        product_data_raw = self.external_product_service.get_product_by_id(product_id)

        if product_data_raw is None:
            logger.warning(f"Producto con ID {product_id} no encontrado en la API externa.")
            return None
        
        product = Product.from_dict(product_data_raw)
        
        self._cache[cache_key] = product
        self._cache_timestamp[cache_key] = datetime.now()
        logger.info(f"Detalle de producto guardado en caché para ID: {product_id}")

        return product

    def get_categories(self) -> List[str]:
        cache_key = "product_categories_dummyjson" 

        if cache_key in self._cache and (datetime.now() - self._cache_timestamp[cache_key]) < self.cache_duration:
            logger.info("Devolviendo categorías de DummyJSON desde caché.")
            return list(self._cache[cache_key])

        logger.info("Obteniendo categorías de la API externa (DummyJSON).")
        categories = self.external_product_service.get_categories()

        if categories is None:
            logger.error("No se pudieron obtener categorías de DummyJSON.")
            return []
        
        self._cache[cache_key] = categories
        self._cache_timestamp[cache_key] = datetime.now()
        logger.info("Categorías de DummyJSON guardadas en caché.")

        return categories
