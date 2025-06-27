# backend/routes/product_routes.py
from flask import Blueprint, jsonify, request, render_template
import logging

product_bp = Blueprint('product_bp', __name__)
logger = logging.getLogger(__name__)

# Variable para almacenar la instancia del controlador que será inyectada
_product_controller_instance = None 

def init_product_routes(product_controller):
    global _product_controller_instance
    _product_controller_instance = product_controller
    logger.info("product_routes: Controlador de productos inyectado.")

@product_bp.route('/productos')
def show_products():
    """Renders the products page."""
    initial_search_query = request.args.get('query', '')
    return render_template('products.html', initial_search_query=initial_search_query)

@product_bp.route('/product/<int:product_id>') # Ya debería estar así
def show_product_detail(product_id):
    """Renders the product detail page."""
    return render_template('product_detail.html', product_id=product_id)


@product_bp.route('/api/products', methods=['GET'])
def get_products_api():
    """API endpoint para obtener productos paginados y filtrados."""
    if not _product_controller_instance:
        logger.error("ProductController no ha sido inyectado en product_routes.")
        return jsonify({"error": "Servicio de productos no disponible."}), 500

    query = request.args.get('query')
    category = request.args.get('category')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))

    logger.info(f"API Request: get_products_api - Query: {query}, Category: {category}, Page: {page}, Limit: {limit}")
    
    products_data, total_filtered_products = _product_controller_instance.get_products(
        query=query, user_category=category, page=page, limit=limit
    )
    
    total_pages = 0
    if limit > 0:
        total_pages = (total_filtered_products + limit - 1) // limit 
    if total_pages == 0 and total_filtered_products > 0: 
        total_pages = 1

    return jsonify({
        'products': products_data,
        'total_products': total_filtered_products, 
        'total_pages': total_pages,
        'current_page': page,
        'products_on_page': len(products_data) 
    })

# --- ¡NUEVA RUTA API PARA OBTENER UN PRODUCTO POR ID CON <int:product_id>! ---
@product_bp.route('/api/products/<int:product_id>', methods=['GET']) # <--- CAMBIO CLAVE AQUÍ: <int:product_id>
def get_product_by_id_api(product_id):
    """API endpoint para obtener un producto por su ID."""
    if not _product_controller_instance:
        logger.error("ProductController no ha sido inyectado en product_routes.")
        return jsonify({"error": "Servicio de productos no disponible."}), 500
    
    logger.info(f"API Request: get_product_by_id_api - ID: {product_id} (Tipo: {type(product_id)})")
    
    # Llama al método del controlador para obtener el producto
    product_data = _product_controller_instance.get_product_by_id(product_id) 
    
    if product_data:
        return jsonify(product_data), 200
    else:
        logger.warning(f"Producto con ID {product_id} no encontrado.")
        return jsonify({"error": "Producto no encontrado."}), 404

@product_bp.route('/api/categories', methods=['GET'])
def get_categories_api():
    """API endpoint para obtener las categorías de productos disponibles."""
    if not _product_controller_instance:
        logger.error("ProductController no ha sido inyectado en product_routes.")
        return jsonify({"error": "Servicio de categorías no disponible."}), 500

    logger.info("API Request: get_categories_api")
    categories = _product_controller_instance.get_categories()
    return jsonify(categories)
