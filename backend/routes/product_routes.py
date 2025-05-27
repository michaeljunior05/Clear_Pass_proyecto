# backend/routes/product_routes.py
from flask import Blueprint, request, jsonify
import logging

# Importamos el controlador de productos
# from backend.controllers.product_controller import ProductController # No lo importamos directamente, sino que lo inyectamos

product_bp = Blueprint('product', __name__, url_prefix='/api') # Prefijo /api para todas las rutas de este blueprint

logger = logging.getLogger(__name__)

# Variable global para inyectar el controlador, similar a auth_routes
_product_controller = None

def init_product_routes(controller):
    """
    Función para inicializar las rutas de productos con el controlador adecuado.
    Esta función será llamada desde app.py.
    """
    global _product_controller
    _product_controller = controller
    logger.info("Rutas de productos inicializadas con el controlador.")

@product_bp.route('/products', methods=['GET'])
def get_products():
    """
    Endpoint para obtener todos los productos o filtrar por categoría/límite.
    Parámetros de consulta:
    - category: string (ej. 'electronics')
    - limit: int (ej. 10)
    - query: string (término de búsqueda, si la API externa lo soporta)
    """
    if not _product_controller:
        logger.error("ProductController no inicializado para las rutas de productos.")
        return jsonify({'message': 'Controlador de productos no inicializado'}), 500

    category = request.args.get('category')
    limit_str = request.args.get('limit')
    query = request.args.get('query') # Para futuras implementaciones de búsqueda
    
    limit = None
    if limit_str:
        try:
            limit = int(limit_str)
        except ValueError:
            return jsonify({'message': 'El parámetro limit debe ser un número entero'}), 400

    products = _product_controller.get_products(query=query, category=category, limit=limit)
    
    if products:
        return jsonify(products), 200
    else:
        # Puede ser que no haya productos o que la API haya fallado
        logger.warning("No se encontraron productos o hubo un error al obtenerlos.")
        return jsonify({'message': 'No se encontraron productos o hubo un problema al obtenerlos'}), 404


@product_bp.route('/products/<string:product_id>', methods=['GET'])
def get_product_detail(product_id: str):
    """
    Endpoint para obtener los detalles de un producto específico por su ID.
    """
    if not _product_controller:
        logger.error("ProductController no inicializado para las rutas de productos.")
        return jsonify({'message': 'Controlador de productos no inicializado'}), 500

    product = _product_controller.get_product_details(product_id)
    if product:
        return jsonify(product), 200
    else:
        logger.warning(f"Producto con ID {product_id} no encontrado.")
        return jsonify({'message': f'Producto con ID {product_id} no encontrado'}), 404