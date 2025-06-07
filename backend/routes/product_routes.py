from flask import Blueprint, request, jsonify
import logging
from backend.controllers.product_controller import ProductController

logger = logging.getLogger(__name__)

product_bp = Blueprint('product_api', __name__, url_prefix='/api')

_product_controller: ProductController = None

def init_product_routes(controller: ProductController):
    """
    Función para inicializar las rutas de productos con el controlador adecuado.
    """
    global _product_controller
    _product_controller = controller
    logger.info("Rutas de productos inicializadas con el controlador.")

@product_bp.route('/products', methods=['GET'])
def get_products():
    """
    Endpoint de la API para obtener productos con filtros de búsqueda, categoría y paginación.
    """
    logger.info("Petición GET recibida en /api/products")
    if not _product_controller:
        logger.error("ProductController no inicializado para las rutas de productos.")
        return jsonify({'message': 'Error interno del servidor: controlador no inicializado'}), 500

    query = request.args.get('query')
    category = request.args.get('category')
    
    limit_str = request.args.get('limit', '10') 
    page_str = request.args.get('page', '1')   

    try:
        limit = int(limit_str)
        page = int(page_str)
        if limit <= 0 or page <= 0:
            logger.warning(f"Parámetros de paginación inválidos: limit={limit_str}, page={page_str}. Deben ser números positivos.")
            return jsonify({'message': 'Limit y Page deben ser números positivos.'}), 400
        if limit > 100: 
            limit = 100
            logger.warning(f"El límite solicitado {limit_str} excede el máximo permitido. Se usará el límite de 100.")
    except ValueError:
        logger.warning(f"Parámetros de paginación no numéricos: limit='{limit_str}', page='{page_str}'")
        return jsonify({'message': 'Los parámetros limit y page deben ser números enteros.'}), 400

    result = _product_controller.get_products(query=query, category=category, page=page, limit=limit)
    
    if result is None:
        logger.error("El controlador de productos devolvió None al obtener productos.")
        return jsonify({'message': 'Error al obtener productos'}), 500 

    products_as_dict = result.get('products', [])
    total_pages = result.get('total_pages', 0)
    
    logger.info(f"Devolviendo {len(products_as_dict)} productos para la página {page} de {total_pages}. Consulta: query='{query}', category='{category}'.")
    return jsonify({'products': products_as_dict, 'total_pages': total_pages}), 200

@product_bp.route('/products/<string:product_id>', methods=['GET'])
def get_product_detail(product_id: str):
    """
    Endpoint de la API para obtener los detalles de un producto específico por su ID.
    """
    logger.info(f"Petición GET recibida en /api/products/{product_id}")
    if not _product_controller:
        logger.error("ProductController no inicializado para las rutas de productos.")
        return jsonify({'message': 'Error interno del servidor: controlador no inicializado'}), 500

    product = _product_controller.get_product_details(product_id)
    if product:
        logger.info(f"Detalles del producto ID {product_id} obtenidos exitosamente.")
        return jsonify(product.to_dict()), 200
    else:
        logger.warning(f"Producto con ID {product_id} no encontrado o no cumple los criterios de filtro de tecnología.")
        return jsonify({'message': f'Producto con ID {product_id} no encontrado o no es una categoría tecnológica válida.'}), 404

@product_bp.route('/products/categories', methods=['GET'])
def get_product_categories():
    """
    Endpoint de la API para obtener una lista de categorías de productos.
    """
    logger.info("Petición GET recibida en /api/products/categories")
    if not _product_controller:
        logger.error("ProductController no inicializado para las rutas de productos.")
        return jsonify({'message': 'Error interno del servidor: controlador no inicializado'}), 500

    categories = _product_controller.get_product_categories()
    
    if categories is None: 
        logger.error("El controlador de productos devolvió None al obtener categorías.")
        return jsonify({'message': 'Error al obtener categorías'}), 500
    
    logger.info(f"Devolviendo {len(categories)} categorías.")
    return jsonify(categories), 200

@product_bp.route('/products/clear-cache', methods=['POST']) # Usar POST para acciones de modificar estado
def clear_product_cache():
    """
    Endpoint para invalidar manualmente la caché de productos en el servidor.
    """
    logger.info("Petición POST recibida en /api/products/clear-cache para invalidar la caché.")
    if not _product_controller:
        logger.error("ProductController no inicializado para las rutas de productos.")
        return jsonify({'message': 'Error interno del servidor: controlador no inicializado'}), 500
    
    _product_controller.clear_product_cache()
    logger.info("Caché de productos invalidada exitosamente.")
    return jsonify({'message': 'Caché de productos invalidada exitosamente.'}), 200
