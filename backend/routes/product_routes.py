import logging
from flask import Blueprint, jsonify, request
from backend.controllers.product_controller import ProductController

logger = logging.getLogger(__name__)

# Crear un Blueprint para las rutas de productos
product_bp = Blueprint('product_bp', __name__, url_prefix='/api')

_product_controller: ProductController = None # Type hint para asegurar el tipo del controlador

def init_product_routes(controller: ProductController):
    """
    Inicializa las rutas de productos con el controlador de productos.
    Esta función es llamada una vez al iniciar la aplicación para inyectar el controlador.
    """
    global _product_controller
    _product_controller = controller
    logger.info("Rutas de productos inicializadas con el controlador.")

@product_bp.route('/products', methods=['GET'])
def get_products():
    """
    Ruta para obtener productos con paginación, búsqueda y filtrado por categoría.
    Parámetros de query:
    - query (str): Término de búsqueda en nombre o descripción.
    - category (str): Categoría de productos.
    - page (int): Número de página (por defecto 1).
    - limit (int): Cantidad de productos por página (por defecto 10).
    """
    if not _product_controller:
        logger.error("ProductController no está inicializado en product_routes.")
        return jsonify({"message": "Servicio de productos no disponible."}), 500

    query = request.args.get('query', '')
    category = request.args.get('category', '')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    logger.info(f"Petición recibida en /api/products con query='{query}', category='{category}', page={page}, limit={limit}")
    
    # CORREGIDO: Llamar a get_paginated_products
    products, total_pages = _product_controller.get_paginated_products(query=query, category=category, page=page, limit=limit)

    return jsonify({
        "products": products,
        "total_pages": total_pages,
        "current_page": page,
        "limit": limit
    }), 200

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product_detail(product_id):
    """
    Ruta para obtener los detalles de un producto específico por su ID.
    """
    if not _product_controller:
        logger.error("ProductController no está inicializado en product_routes.")
        return jsonify({"message": "Servicio de productos no disponible."}), 500
    
    logger.info(f"Petición recibida en /api/products/{product_id}")
    product = _product_controller.get_product_detail(product_id)

    if product:
        return jsonify(product), 200
    else:
        logger.warning(f"Producto con ID {product_id} no encontrado.")
        return jsonify({"message": "Producto no encontrado o no disponible."}), 404

@product_bp.route('/products/categories', methods=['GET'])
def get_product_categories():
    """
    Ruta para obtener todas las categorías únicas de productos.
    """
    if not _product_controller:
        logger.error("ProductController no está inicializado en product_routes.")
        return jsonify({"message": "Servicio de productos no disponible."}), 500
    
    logger.info("Petición recibida en /api/products/categories")
    # CORREGIDO: Llamar a get_categories
    categories = _product_controller.get_categories()

    return jsonify(categories), 200
