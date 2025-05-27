# backend/controllers/product_controller.py
import logging
from typing import List, Dict, Optional
from backend.repositories.product_repository import ProductRepository # AHORA DEPENDE DEL REPOSITORIO
from backend.models.product import Product # Para los tipos de retorno

logger = logging.getLogger(__name__)

class ProductController:
    """
    Controlador encargado de la lógica de negocio relacionada con los productos.
    Depende de ProductRepository para obtener datos de productos, manejando
    la abstracción de la fuente de datos.
    """
    def __init__(self, product_repository: ProductRepository): # AHORA RECIBE EL REPOSITORIO
        """
        Inicializa el ProductController.

        Args:
            product_repository (ProductRepository): Instancia del repositorio de productos.
        """
        self.product_repo = product_repository
        logger.info("ProductController inicializado.")

    def get_products(self, query: str = None, category: str = None, limit: int = None) -> List[Dict] | None:
        """
        Obtiene una lista de todos los productos disponibles, aplicando filtros.

        Args:
            query (str, optional): Término de búsqueda (manejo interno o no soportado por API).
            category (str, optional): Filtra productos por categoría.
            limit (int, optional): Limita el número de resultados.

        Returns:
            List[Dict] | None: Una lista de diccionarios que representan productos, o None si falla.
        """
        logger.info(f"Solicitando productos con categoría: {category}, límite: {limit}, query: {query}")
        # El repositorio ya maneja la lógica de category y limit para la API externa
        products: List[Product] = self.product_repo.get_all_products(query=query, category=category, limit=limit)
        
        if products:
            # Convertir objetos Product a diccionarios para la respuesta JSON
            return [p.to_dict() for p in products]
        else:
            logger.warning("No se pudieron obtener productos del repositorio.")
            return None

    def get_product_details(self, product_id: str) -> Dict | None: # La ruta pasa product_id como str
        """
        Obtiene un producto específico por su ID.

        Args:
            product_id (str): El ID del producto a buscar.

        Returns:
            Dict | None: Un diccionario que representa el producto, o None si no se encuentra.
        """
        logger.info(f"Solicitando detalles del producto con ID: {product_id} al ProductRepository.")
        product: Product = self.product_repo.get_product_by_id(product_id)
        
        if product:
            return product.to_dict()
        else:
            logger.warning(f"Producto con ID: {product_id} no encontrado o hubo un error.")
            return None
    # Métodos futuros para buscar por categoría, por nombre, etc.
    # def get_products_by_category(self, category: str) -> list[dict]:
    #     products = self.product_repo.get_all_products(category=category)
    #     return [p.to_dict() for p in products]