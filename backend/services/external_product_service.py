# backend/services/external_product_service.py
import requests
import logging
from typing import List, Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class ExternalProductService:
    """
    Servicio para interactuar con la API externa de productos (DummyJSON.com).
    Encapsula la lógica de las solicitudes HTTP y el manejo básico de errores.
    """
    def __init__(self, base_url: str):
        if not base_url:
            raise ValueError("The base URL for the ExternalProductService cannot be empty.")
        self.base_url = base_url.rstrip('/')
        logger.info(f"ExternalProductService initialized with base_url: {self.base_url}")

    def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Tiempo de espera agotado al conectar con {url} (params: {params}).")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión al intentar alcanzar {url}.")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"Error HTTP al obtener {url} (params: {params}): {e} - Respuesta: {response.text}")
            if response.status_code == 404 and "products/" in endpoint:
                return None
            if response.status_code == 404 and "category/" in endpoint:
                return {"products": [], "total": 0} 
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error inesperado al solicitar {url}: {e}")
            return None
        except ValueError as e: 
            logger.error(f"Error de decodificación JSON desde {url}: {e}")
            return None

    def get_all_products(self, query: Optional[str] = None, category: Optional[str] = None, 
                             limit: int = 0, skip: int = 0) -> Tuple[List[Dict[str, Any]], int]: # Limit y skip son ignorados si se va a traer todo
        """
        Obtiene *todos* los productos de DummyJSON.com que coincidan con la búsqueda/categoría.
        Realiza múltiples llamadas a la API si el total excede el límite de una sola petición (100).
        
        Args:
            query (str, optional): Término de búsqueda.
            category (str, optional): Categoría a filtrar (en formato DummyJSON).
            limit (int): Este parámetro es ignorado aquí, se usa un límite interno de 100 por API de DummyJSON.
            skip (int): Este parámetro es ignorado aquí, se gestiona internamente para las múltiples llamadas.

        Returns:
            Tuple[List[Dict[str, Any]], int]: Una tupla con la lista de diccionarios de productos
                                                y el total de productos *filtrados* disponibles por la API externa.
        """
        all_fetched_products = []
        current_skip = 0
        total_from_api = 0 
        single_request_limit = 100 # DummyJSON tiene un máximo de 100 productos por request.

        endpoint_base = "products"
        params_base = {}

        if query:
            endpoint_base = "products/search"
            params_base['q'] = query
        elif category:
            endpoint_base = f"products/category/{category}"
        
        # Bucle para obtener todas las páginas de resultados de la API externa
        # Se asegura de obtener todos los productos que cumplan la condición de búsqueda/categoría
        while True:
            params = {**params_base, 'limit': single_request_limit, 'skip': current_skip}
            data = self._make_request(endpoint_base, params)
            
            if data is None:
                logger.error(f"Fallo al obtener datos de la API externa para {endpoint_base} con params {params}. Interrumpiendo la carga de todos los productos.")
                break

            products_batch = data.get('products', [])
            total_current_query = data.get('total', 0)

            # Si es la primera iteración, establecemos el total de la API
            if current_skip == 0:
                total_from_api = total_current_query

            all_fetched_products.extend(products_batch)
            current_skip += single_request_limit

            # Si ya hemos obtenido todos los productos para la consulta o no hay más, salimos
            if current_skip >= total_from_api or not products_batch:
                break
        
        logger.info(f"ExternalProductService: Total de productos recolectados para query='{query}', category='{category}': {len(all_fetched_products)} de un total API de {total_from_api}.")
        return all_fetched_products, total_from_api


    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        endpoint = f"products/{product_id}"
        return self._make_request(endpoint)

    def get_categories(self) -> Optional[List[str]]:
        endpoint = "products/categories"
        return self._make_request(endpoint)
