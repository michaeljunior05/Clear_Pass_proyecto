# backend/routes/product_routes.py
from flask import Blueprint, jsonify, request, session
import logging
from typing import Optional

logger = logging.getLogger(__name__)

product_bp = Blueprint('product_bp', __name__)

_product_controller = None 

def init_product_routes(controller):
    global _product_controller
    _product_controller = controller
    logger.info("Rutas de productos inicializadas con el controlador.")


@product_bp.route('/api/products', methods=['GET'])
def get_products():
    """
    Ruta para obtener todos los productos o productos por categoría/búsqueda, con paginación.

    Parámetros de consulta:
    - query (str, opcional): Término de búsqueda.
    - category (str, opcional): Categoría de productos personalizada (ej. "telefonos moviles").
    - page (int, opcional): Número de página (por defecto 1).
    - limit (int, opcional): Límite de productos por página (por defecto 10).
    """
    query = request.args.get('query')
    user_category = request.args.get('category') 
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    if not _product_controller:
        logger.error("ProductController no inicializado en rutas de productos.")
        return jsonify({"error": "Servicio de productos no disponible"}), 500

    products_data, total_pages = _product_controller.get_products(
        query=query, user_category=user_category, page=page, limit=limit
    )

    if products_data is not None:
        return jsonify({
            "products": products_data,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "total_products_on_page": len(products_data) 
        }), 200
    else:
        return jsonify({"error": "No se pudieron obtener los productos"}), 500


@product_bp.route('/api/products/<string:product_id>', methods=['GET']) 
def get_single_product(product_id: str): 
    """
    Ruta para obtener un producto específico por su ID.
    """
    if not _product_controller:
        logger.error("ProductController no inicializado en rutas de productos.")
        return jsonify({"error": "Servicio de productos no disponible"}), 500

    product_data = _product_controller.get_product_details(product_id)
    
    if product_data:
        return jsonify(product_data), 200
    else:
        return jsonify({"error": "Producto no encontrado"}), 404

@product_bp.route('/api/categories', methods=['GET'])
def get_categories_api():
    """
    Ruta para obtener todas las categorías de productos personalizadas en español.
    """
    if not _product_controller:
        logger.error("ProductController no inicializado en rutas de productos.")
        return jsonify({"error": "Servicio de productos no disponible"}), 500
    
    categories = _product_controller.get_categories()
    return jsonify(categories), 200