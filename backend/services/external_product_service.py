# backend/services/external_product_service.py
import requests
import logging
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class ExternalProductService:
    """
    Servicio encargado de interactuar con la API externa de productos (storerestapi.com).
    Encapsula la lógica de las llamadas HTTP y maneja las respuestas.
    """
    def __init__(self, base_url: str):
        """
        Inicializa el ExternalProductService.

        Args:
            base_url (str): La URL base de la API externa de productos.
        """
        if not base_url:
            raise ValueError("La URL base para el ExternalProductService no puede estar vacía.")
        self.base_url = base_url
        logger.info(f"ExternalProductService inicializado con base_url: {self.base_url}")

    def get_all_products(self) -> List[Dict[str, Any]] | None:
        """
        Obtiene todos los productos de la API externa.

        Returns:
            List[Dict] | None: Una lista de diccionarios, donde cada diccionario representa un producto,
                               o None si ocurre un error.
        """
        endpoint = f"{self.base_url}/products"
        logger.info(f"Intentando obtener todos los productos de: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # --- CAMBIO CLAVE AQUÍ: Esperamos una LISTA directamente ---
            if isinstance(data, list):
                logger.info(f"Productos obtenidos de {endpoint}. Cantidad: {len(data)}")
                return data 
            else:
                logger.error(f"Formato de respuesta inesperado al obtener productos de {endpoint}. "
                             f"Se esperaba una lista de productos directamente. "
                             f"Respuesta recibida (tipo: {type(data)}): {data}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Tiempo de espera agotado al obtener productos de: {endpoint}. La API no respondió a tiempo.")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión al intentar acceder a {endpoint}. La API podría estar inaccesible, la URL es incorrecta o hay un problema de red.")
            return None
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Error HTTP al obtener productos de {endpoint}: {http_err} - Código de estado: {response.status_code} - Respuesta: {response.text}")
            return None
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Error general de solicitud al obtener productos de {endpoint}: {req_err}")
            return None
        except ValueError as json_err:
            logger.error(f"Error al decodificar la respuesta JSON de {endpoint}: {json_err} - Contenido: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener productos de {endpoint}: {e}", exc_info=True)
            return None

    def get_product_by_id(self, product_id: str) -> Dict[str, Any] | None:
        """
        Obtiene un producto específico de la API externa por su ID.

        Args:
            product_id (str): El ID del producto a buscar.

        Returns:
            Dict | None: Un diccionario con la información del producto, o None si no se encuentra
                         o si ocurre un error.
        """
        endpoint = f"{self.base_url}/products/{product_id}"
        logger.info(f"Intentando obtener producto ID {product_id} de: {endpoint}")
        try:
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # --- CAMBIO CLAVE AQUÍ: Esperamos un DICCIONARIO directamente ---
            if isinstance(data, dict) and data:
                logger.info(f"Producto ID {product_id} obtenido de {endpoint}.")
                return data
            else:
                logger.warning(f"Producto ID {product_id} no encontrado o formato de respuesta inesperado de {endpoint}. "
                               f"Se esperaba un diccionario. Respuesta recibida (tipo: {type(data)}): {data}")
                return None
        except requests.exceptions.Timeout:
            logger.error(f"Tiempo de espera agotado al obtener producto ID {product_id} de: {endpoint}. La API no respondió a tiempo.")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión al intentar acceder a {endpoint}. La API podría estar inaccesible, la URL es incorrecta o hay un problema de red.")
            return None
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"Error HTTP al obtener producto ID {product_id} de {endpoint}: {http_err} - Código de estado: {response.status_code} - Respuesta: {response.text}")
            if response.status_code == 404:
                return None
            return None
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Error general de solicitud al obtener producto ID {product_id} de {endpoint}: {req_err}")
            return None
        except ValueError as json_err:
            logger.error(f"Error al decodificar la respuesta JSON de {endpoint}: {json_err} - Contenido: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener producto ID {product_id} de {endpoint}: {e}", exc_info=True)
            return None


            