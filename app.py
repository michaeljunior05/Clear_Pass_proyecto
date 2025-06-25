# app.py
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # ¡MANTENER ESTA LÍNEA POR AHORA! Aunque usemos HTTPS, a veces oauthlib puede ser caprichosa.

from flask import Flask, render_template, url_for, session, redirect, jsonify, request 
from flask_session import Session
import logging
from datetime import timedelta
from flask_cors import CORS

# Configuración del logging
# Mantenemos INFO para producción, pero puedes cambiar a DEBUG si necesitas más detalles en la consola
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

# --- NUEVAS IMPORTACIONES PARA IMPORTADORES ---
from backend.models.importer import Importer # Aunque no se instancie directamente, es buena práctica si se usa en typings
from backend.repositories.importer_repository import ImporterRepository
from backend.services.importer_ranking_service import ImporterRankingService
from backend.controllers.auth_controller import AuthController
from backend.controllers.product_controller import ProductController
# --- FIN NUEVAS IMPORTACIONES ---
# --- NUEVA IMPORTACIÓN PARA RUTAS DE IMPORTADORES ---
from backend.routes.importer_routes import importer_bp, init_importer_routes

def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join('frontend', 'static'),
        template_folder=os.path.join('frontend', 'templates')
    )

    app.config.from_object(Config)

    app.config["SESSION_PERMANENT"] = Config.SESSION_PERMANENT # <-- Usa Config aquí
    app.config["SESSION_TYPE"] = Config.SESSION_TYPE # <-- Usa Config aquí
    app.config['PERMANENT_SESSION_LIFETIME'] = Config.PERMANENT_SESSION_LIFETIME # <-- Usa Config aquí
    Session(app)

    # --- CORRECCIÓN CLAVE: AÑADIR LA URL DE TU REPLIT A LOS ORÍGENES PERMITIDOS EN CORS ---
    # Esto es CRÍTICO para que el frontend en Replit pueda hacer fetch al backend.
    # Se añade la URL de tu Replit, más los orígenes locales de desarrollo.
    CORS(app, supports_credentials=True, 
         origins=[
             "http://localhost:5173",       # Para desarrollo con Vite (si aplica)
             "http://127.0.0.1:5173",       # Para desarrollo con Vite (si aplica)
             "https://127.0.0.1:5000",      # Para tu servidor Flask local con HTTPS
             "https://7ae08de5-5e6b-413e-8ffa-8d687bce8c2b-00-2i3kzc743oqsk.riker.replit.dev" # ¡TU URL ESPECÍFICA DE REPLIT!
         ]) 

    # --- Inicialización de Repositorios y Controladores (Inyección de Dependencias) ---
    json_storage = JSONStorage(data_file=Config.JSON_DATABASE_PATH) # <-- Usa Config aquí
    logger.info("JSONStorage inicializado.")
    
    external_product_service = ExternalProductService(Config.EXTERNAL_PRODUCTS_API_BASE_URL) # <-- Usa Config aquí
    logger.info(f"ExternalProductService instanciado con base_url: {external_product_service.base_url}")
    user_repository = UserRepository(storage=json_storage)
    # --- INICIALIZACIÓN DE IMPORTADORES ---
    importer_repository = ImporterRepository(storage=json_storage)
    importer_ranking_service = ImporterRankingService(importer_repository)
    logger.info("ImporterRepository e ImporterRankingService inicializados.")
    # --- FIN INICIALIZACIÓN IMPORTADORES ---
    
    auth_controller = AuthController(user_repository=user_repository, config=Config)
    # <-- CORRECCIÓN CLAVE: Pasa external_product_service, no product_repository
    product_controller = ProductController(external_product_service=external_product_service) 
    logger.info("AuthController y ProductController instanciados.")

    # --- Registro de Blueprints y Inyección de Controladores ---
    init_product_routes(product_controller)
    app.register_blueprint(product_bp) 
    logger.info("Blueprint 'product_bp' registrado con prefijo '/api'.")
    
    init_auth_routes(auth_controller)
    app.register_blueprint(auth_bp, url_prefix= '/api') 
    logger.info("Blueprint 'auth_bp' registrado con prefijo '/api'.")

    # --- REGISTRO DE BLUEPRINT DE IMPORTADORES ---
    init_importer_routes(importer_ranking_service, user_repository) # Pasar el servicio y el repo de usuarios
    app.register_blueprint(importer_bp, url_prefix='/api') # Usar /api para consistencia
    logger.info("Blueprint 'importer_bp' registrado con prefijo '/api'.")
    # --- FIN REGISTRO IMPORTADORES ---


    # --- Rutas para renderizar las páginas HTML del Frontend ---
    
    @app.route('/')
    def index():
        user_name = session.get('user_name')
        logged_in = 'user_id' in session 
        return render_template('home.html', logged_in=logged_in, user_name=user_name)

    @app.route('/register', methods=['GET'])
    def show_register_form():
        # ¡IMPORTANTE! Pasa el google_client_id a la plantilla de registro
        google_client_id = Config.GOOGLE_CLIENT_ID 
        return render_template('register.html', google_client_id=google_client_id)
    
    @app.route('/login', methods=['GET'])
    def show_login_form():
        if 'user_id' in session:
            return redirect(url_for('productos_page')) 
        # ¡IMPORTANTE! Pasa el google_client_id a la plantilla de login
        google_client_id = Config.GOOGLE_CLIENT_ID 
        return render_template('login.html', google_client_id=google_client_id)

    @app.route('/productos') 
    def productos_page():
        logged_in = 'user_id' in session
        user_name = session.get('user_name', 'Usuario')
        initial_search_query = request.args.get('query', '')
        return render_template('products.html', 
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

    @app.route('/perfil')
    def profile_page():
        logged_in = 'user_id' in session 
        user_name = session.get('user_name', 'Invitado') 
        return render_template('profile.html', logged_in=logged_in, user_name=user_name)


    return app

app = create_app()
if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))
