# app.py
from flask import Flask, render_template, url_for, session, redirect, jsonify, request 
import os
from flask_session import Session
import logging
from datetime import timedelta
from flask_cors import CORS

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importar la clase de configuración
from config import Config
# Importar la clase de servicios
from backend.services.external_product_service import ExternalProductService

# Importar las clases de repositorios y controladores
from backend.repositories.json_storage import JSONStorage 
from backend.repositories.user_repository import UserRepository
from backend.repositories.product_repository import ProductRepository 

from backend.controllers.auth_controller import AuthController
from backend.controllers.product_controller import ProductController

# Importar el blueprint y la función de inicialización de rutas para Auth y Product
from backend.routes.auth_routes import auth_bp, init_auth_routes
from backend.routes.product_routes import product_bp, init_product_routes

def create_app():
    """
    Función de fábrica de aplicaciones para Flask.
    Configura la aplicación, inicializa las dependencias
    y registra los Blueprints.
    """
    app = Flask(
        __name__,
        static_folder=os.path.join('frontend', 'static'),
        template_folder=os.path.join('frontend', 'templates')
    )

    app.config.from_object(Config)

    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_TYPE"] = "filesystem"
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    Session(app)

    CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"]) 

    # --- Inicialización de Repositorios y Controladores (Inyección de Dependencias) ---

    json_storage = JSONStorage(data_file='data.json')
    logger.info("JSONStorage inicializado.")
    
    external_product_service = ExternalProductService(app.config['EXTERNAL_PRODUCTS_API_BASE_URL'])
    logger.info(f"ExternalProductService instanciado con base_url: {external_product_service.base_url}")

    user_repository = UserRepository(storage=json_storage)
    
    # IMPORTANTE: La inyección de dependencias ahora es directa, sin circularidad
    # Primero se inicializa ProductRepository (que no depende de ProductController)
    product_repository = ProductRepository(external_product_service=external_product_service)
    # Luego se inicializa ProductController, pasándole el ProductRepository
    product_controller = ProductController(product_repository=product_repository)
    
    auth_controller = AuthController(user_repository=user_repository, config=Config)
    logger.info("AuthController y ProductController instanciados.")


    # --- Registro de Blueprints y Inyección de Controladores ---

    # Rutas de productos (API)
    init_product_routes(product_controller)
    app.register_blueprint(product_bp) 
    logger.info("Blueprint 'product_bp' registrado con prefijo '/api'.")
    
    # Rutas de autenticación (API)
    init_auth_routes(auth_controller)
    app.register_blueprint(auth_bp, url_prefix= '/api') 
    logger.info("Blueprint 'auth_bp' registrado con prefijo '/api'.")

    # --- Rutas para renderizar las páginas HTML del Frontend ---
    
    @app.route('/')
    def index():
        user_name = session.get('user_name')
        logged_in = 'user_id' in session 
        return render_template('home.html', logged_in=logged_in, user_name=user_name)

    @app.route('/register', methods=['GET'])
    def show_register_form():
        return render_template('register.html')
    
    @app.route('/login', methods=['GET'])
    def show_login_form():
        if 'user_id' in session:
            return redirect(url_for('productos_page')) 
        return render_template('login.html')

    @app.route('/productos') 
    def productos_page():
        logged_in = 'user_id' in session
        user_name = session.get('user_name', 'Usuario')
        initial_search_query = request.args.get('query', '')
        return render_template('productos.html', 
                               logged_in=logged_in, 
                               user_name=user_name, 
                               initial_search_query=initial_search_query) 

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        session.pop('user_name', None)
        session.pop('user_email', None)
        return redirect(url_for('index'))

    @app.route('/test-session')
    def test_session():
        user_id = session.get('user_id')
        user_email = session.get('user_email')
        if user_id:
            return jsonify({'message': f'Usuario en sesión: {user_email} (ID: {user_id})'}), 200
        return jsonify({'message': 'No hay usuario en sesión'}), 401

    @app.route('/product/<int:product_id>')
    def product_detail_page(product_id):
        logged_in = 'user_id' in session
        user_name = session.get('user_name', 'Usuario')
        return render_template('product_detail.html', product_id=product_id, logged_in=logged_in, user_name=user_name)


    return app

# Bloque de ejecución principal
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
