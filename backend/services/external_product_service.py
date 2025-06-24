# backend/services/external_product_service.py
import requests
import logging
from typing import List, Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class ExternalProductService:
    """
    Servicio para interactuar con la API externa de productos (ahora solo DummyJSON.com).
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
                         limit: int = 10, skip: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """
        Obtiene productos de DummyJSON.com con soporte de búsqueda, categoría y paginación.
        Returns:
            Tuple[List[Dict[str, Any]], int]: Una tupla con la lista de diccionarios de productos
                                               y el total de productos disponibles.
        """
        params = {'limit': limit, 'skip': skip}
        
        if query:
            endpoint = f"products/search"
            params['q'] = query
        elif category:
            endpoint = f"products/category/{category}"
        else:
            endpoint = "products"
        
        data = self._make_request(endpoint, params)
        if data:
            return data.get('products', []), data.get('total', 0)
        return [], 0

    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        endpoint = f"products/{product_id}"
        return self._make_request(endpoint)

    def get_categories(self) -> Optional[List[str]]:
        endpoint = "products/categories"
        return self._make_request(endpoint)