# backend/services/external_product_service.py
import requests
import logging
import time # Importar la librería time

logger = logging.getLogger(__name__)

class ExternalProductService:
    """
    Servicio para interactuar con una API externa de productos (ej. FakeStoreAPI).
    """
    def __init__(self, base_url: str):
        self.base_url = base_url
        logger.info(f"ExternalProductService inicializado con base_url: {self.base_url}")

    def get_all_products(self) -> list[dict]:
        """
        Recupera todos los productos de la API externa.
        """
        start_time = time.time() # Iniciar el contador de tiempo
        logger.info(f"Iniciando solicitud a API externa: {self.base_url}/products")
        try:
            response = requests.get(f"{self.base_url}/products")
            response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
            products = response.json()
            end_time = time.time() # Finalizar el contador de tiempo
            duration = (end_time - start_time) * 1000 # Duración en milisegundos
            logger.info(f"Solicitud a API externa /products completada en {duration:.2f} ms. Productos recibidos: {len(products)}")
            return products
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener productos de la API externa: {e}")
            return []

    def get_product_by_id(self, product_id: int) -> dict | None:
        """
        Recupera un producto específico por su ID de la API externa.
        """
        start_time = time.time() # Iniciar el contador de tiempo
        logger.info(f"Iniciando solicitud a API externa: {self.base_url}/products/{product_id}")
        try:
            response = requests.get(f"{self.base_url}/products/{product_id}")
            response.raise_for_status()
            product = response.json()
            end_time = time.time() # Finalizar el contador de tiempo
            duration = (end_time - start_time) * 1000 # Duración en milisegundos
            logger.info(f"Solicitud a API externa /products/{product_id} completada en {duration:.2f} ms.")
            return product
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener el producto {product_id} de la API externa: {e}")
            return None
