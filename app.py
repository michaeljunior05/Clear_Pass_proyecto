# app.py
from flask import Flask, render_template, url_for, session, redirect, jsonify # Añadir jsonify
import os
from flask_session import Session
import logging
from datetime import timedelta # Necesario para SESSION_PERMANENT_LIFETIME
from flask_cors import CORS # Necesario para CORS

# Configuración del logging para ver mensajes de depuración
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Instancia de logger para app.py

# Importar la clase de configuración
from config import Config
# Importar la clase de servicios
from backend.services.external_product_service import ExternalProductService


# Importar las clases de repositorios y controladores
from backend.repositories.json_storage import JSONStorage
from backend.repositories.user_repository import UserRepository
from backend.repositories.product_repository import ProductRepository
# from backend.repositories.shopping_cart_repository import ShoppingCartRepository
# from backend.repositories.order_repository import OrderRepository
# from backend.repositories.payment_method_repository import PaymentMethodRepository

from backend.controllers.auth_controller import AuthController
from backend.controllers.product_controller import ProductController
# from backend.controllers.cart_controller import CartController
# from backend.controllers.order_controller import OrderController
# from backend.controllers.payment_controller import PaymentController

# Importar el blueprint y la función de inicialización de rutas para Auth
from backend.routes.auth_routes import auth_bp, init_auth_routes
from backend.routes.product_routes import product_bp, init_product_routes
# from backend.routes.cart_routes import cart_bp, init_cart_routes
# from backend.routes.order_routes import order_bp, init_order_routes


def create_app():
    """
    Función de fábrica de aplicaciones para Flask.
    Configura la aplicación, inicializa las dependencias
    y registra los Blueprints.
    """
    # Asegúrate de que las rutas estáticas y de plantillas sean correctas
    # relative to the project root
    app = Flask(
        __name__,
        static_folder=os.path.join('frontend', 'static'),
        template_folder=os.path.join('frontend', 'templates')
    )

    # Cargar la configuración desde la clase Config
    app.config.from_object(Config)


    # Configurar Flask-Session (consolidando lo que ya teníamos en Config)
    # Estas líneas se pueden eliminar si ya están en Config, pero si no, es bueno tenerlas aquí
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_TYPE"] = "filesystem"
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24) # Desde Config
    Session(app)

    # Configurar CORS para permitir solicitudes desde el frontend
    # Asegúrate que "origins" coincida con la URL de desarrollo de tu frontend (ej. Vite)
    CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"]) 

    # --- Inicialización de Repositorios y Controladores (Inyección de Dependencias) ---

    # Repositorio de almacenamiento base (JSONStorage)
    json_storage = JSONStorage(data_file=app.config['JSON_DATABASE_PATH'])
    logger.info("JSONStorage inicializado.")
    # Cliente para APIs externas
    # 1. Instanciar ExternalProductService
    # Eliminar api_client = APIClient(...) y sus imports. Ya no se usa.
    external_product_service = ExternalProductService(app.config['EXTERNAL_PRODUCTS_API_BASE_URL'])
    logger.info(f"ExternalProductService instanciado con base_url: {external_product_service.base_url}")
    # Repositorios específicos
    user_repository = UserRepository(storage=json_storage)
    product_repository = ProductRepository(external_product_service=external_product_service)
    logger.info("AuthController y ProductController instanciados.")
    # shopping_cart_repository = ShoppingCartRepository(storage=json_storage, product_repo=product_repository) # Comentado
    # order_repository = OrderRepository(storage=json_storage) # Comentado
    # payment_method_repository = PaymentMethodRepository(storage=json_storage) # Comentado

    # Controladores
    # El AuthController ahora requiere UserRepository y Config
    auth_controller = AuthController(user_repository=user_repository, config=Config)
    product_controller = ProductController(product_repository=product_repository)
    logger.info("AuthController y ProductController instanciados.")

    # cart_controller = CartController(cart_repo=shopping_cart_repository, product_repo=product_repository) # Comentado
    # payment_controller = PaymentController(method_repo=payment_method_repository) # Comentado
    # order_controller = OrderController(order_repo=order_repository, cart_repo=shopping_cart_repository, payment_controller=payment_controller) # Comentado


    # --- Registro de Blueprints y Inyección de Controladores ---


    # Rutas de autenticación
    init_auth_routes(auth_controller)
    app.register_blueprint(auth_bp, url_prefix='/auth') # Mantener /auth como prefijo para auth_bp
    logger.info("Blueprint 'auth_bp' registrado con prefijo '/auth'.")


    # Rutas de productos
    init_product_routes(product_controller)
    # Registrar product_bp.route con url_prefix='/api' para que las rutas sean /api/products, etc.
    app.register_blueprint(product_bp) # product_bp ya tiene url_prefix='/api' definido internamente
    logger.info("Blueprint 'product_bp' registrado con prefijo '/api'.")




    # Rutas que no requieren controladores específicos por ahora (o se moverán después)
    @app.route('/')
    def index(): # Renombrada de 'home_page' a 'index' para consistencia con lo que ya teníamos
        """
        Ruta principal que renderiza la página de inicio.
        Pasa información de sesión para personalizar la vista (ej. mostrar enlaces de login/logout).
        """
        user_name = session.get('user_name') # Obtener el nombre de usuario de la sesión
        # logged_in es una bandera simple para el frontend
        logged_in = 'user_id' in session 
        
        # Pasa estas variables a la plantilla home.html
        return render_template('home.html', logged_in=logged_in, user_name=user_name)







    

    @app.route('/register', methods=['GET']) # Mantenemos esta ruta HTML
    def show_register_form():
        return render_template('register.html')
    

    @app.route('/login', methods=['GET'])
    def show_login_form():
        """
        Ruta para mostrar el formulario de inicio de sesión.
        """
        if 'user_id' in session:
            return redirect(url_for('productos')) # Redirigir si ya está logueado
        return render_template('login.html')

    @app.route('/productos') # Mantenemos esta ruta HTML, se conectará a ProductController después
    def productos():
        return render_template('productos.html')
    
    # Ruta de logout
    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        session.pop('user_name', None)
        session.pop('user_email', None) # Asegúrate de limpiar todos los datos de sesión relevantes
        return redirect(url_for('index'))

    return app


    @app.route('/test-session')
    def test_session():
        user_id = session.get('user_id')
        user_email = session.get('user_email')
        if user_id:
            return jsonify({'message': f'Usuario en sesión: {user_email} (ID: {user_id})'}), 200
        return jsonify({'message': 'No hay usuario en sesión'}), 401


    return ap





# Bloque de ejecución principal
if __name__ == '__main__':
    # Asegúrate de que las dependencias estén instaladas:
    # pip install Flask Flask-Session Flask-Bcrypt google-auth-oauthlib google-api-python-client requests
    app = create_app()
    app.run(debug=True)
