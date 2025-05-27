# backend/services/external_product_service.py
import requests
import logging
from typing import List, Dict, Optional

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

    def get_all_products(self) -> List[Dict] | None:
        """
        Obtiene todos los productos de la API externa.

        Returns:
            List[Dict] | None: Una lista de diccionarios, donde cada diccionario representa un producto,
                               o None si ocurre un error.
        """
        endpoint = f"{self.base_url}/products"
        try:
            response = requests.get(endpoint, timeout=5) # Añadir timeout para evitar esperas infinitas
            response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
            data = response.json()
            logger.info(f"Productos obtenidos de {endpoint}. Cantidad: {len(data['data'])}")
            return data['data'] # La API devuelve los productos dentro de una clave 'data'
        except requests.exceptions.Timeout:
            logger.error(f"Tiempo de espera agotado al obtener productos de: {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener productos de {endpoint}: {e}")
            return None
        except KeyError:
            logger.error(f"Formato de respuesta inesperado al obtener productos de {endpoint}. Falta la clave 'data'.")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener productos de {endpoint}: {e}", exc_info=True)
            return None

    def get_product_by_id(self, product_id: str) -> Dict | None:
        """
        Obtiene un producto específico de la API externa por su ID.

        Args:
            product_id (str): El ID del producto a buscar.

        Returns:
            Dict | None: Un diccionario con la información del producto, o None si no se encuentra
                         o si ocurre un error.
        """
        endpoint = f"{self.base_url}/products/{product_id}"
        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data and data.get('data'):
                logger.info(f"Producto ID {product_id} obtenido de {endpoint}.")
                return data['data'] # La API devuelve el producto dentro de una clave 'data'
            else:
                logger.warning(f"Producto ID {product_id} no encontrado o respuesta vacía de {endpoint}.")
                return None
        except requests.exceptions.Timeout:
            logger.error(f"Tiempo de espera agotado al obtener producto ID {product_id} de: {endpoint}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener producto ID {product_id} de {endpoint}: {e}")
            # Si el error es 404 Not Found, la API devuelve 'Product not found', que es un caso de None
            if response.status_code == 404:
                return None
            return None
        except KeyError:
            logger.error(f"Formato de respuesta inesperado al obtener producto ID {product_id} de {endpoint}. Falta la clave 'data'.")
            return None
        except Exception as e:
            logger.error(f"Error inesperado al obtener producto ID {product_id} de {endpoint}: {e}", exc_info=True)
            return None


            