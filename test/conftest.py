import pytest
import os
import json
from flask_session import Session
from datetime import timedelta
from unittest.mock import MagicMock 

# Importa las clases y módulos necesarios de tu aplicación
from app import create_app
from config import Config 
from backend.repositories.json_storage import JSONStorage
from backend.repositories.user_repository import UserRepository
from backend.repositories.product_repository import ProductRepository
from backend.services.external_product_service import ExternalProductService
from backend.controllers.auth_controller import AuthController
from backend.controllers.product_controller import ProductController
from backend.models.user import User 
from backend.models.product import Product 

@pytest.fixture
def app():
    """Crea y configura una instancia de la aplicación Flask para pruebas."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SESSION_TYPE": "filesystem", 
        "SECRET_KEY": "test_secret_key",
        "PERMANENT_SESSION_LIFETIME": timedelta(minutes=5),
        "JSON_DATABASE_PATH": "test_data.json" 
    })

    Session(app)

    test_data_path = app.config["JSON_DATABASE_PATH"]
    if os.path.exists(test_data_path):
        os.remove(test_data_path)
    with open(test_data_path, 'w') as f:
        json.dump({"users": [], "products": []}, f) 

    yield app

    if os.path.exists(test_data_path):
        os.remove(test_data_path)


@pytest.fixture
def client(app):
    """Crea un cliente de prueba Flask para hacer solicitudes HTTP simuladas."""
    return app.test_client()

@pytest.fixture
def json_storage_mock(mocker):
    """Mocks la clase JSONStorage."""
    mock = mocker.Mock(spec=JSONStorage)
    mock.get_all.return_value = [] 
    mock.get_by_id.return_value = None 
    mock.find_by_attribute.return_value = [] 
    mock.save_entity.side_effect = lambda entity_type, data: {**data, 'id': 'mock_id'} 
    mock.delete_entity.return_value = True 
    return mock

@pytest.fixture
def user_repository_mock(mocker):
    """Mocks la clase UserRepository."""
    mock = mocker.Mock(spec=UserRepository)
    mock.find_user_by_email.return_value = None 
    mock.find_user_by_email_and_password.return_value = None 
    
    # ELIMINADO EL side_effect de add_user AQUI
    # Para que cada test defina cómo add_user debe comportarse
    
    return mock

@pytest.fixture
def external_product_service_mock(mocker):
    """Mocks la clase ExternalProductService."""
    mock = mocker.Mock(spec=ExternalProductService)
    mock.get_all_products.return_value = [] 
    mock.get_products_by_category.return_value = []
    mock.get_product_by_id.return_value = None
    return mock

@pytest.fixture
def product_repository_mock(mocker):
    """Mocks la clase ProductRepository."""
    mock = mocker.Mock(spec=ProductRepository)
    mock.get_all_products.return_value = [] 
    mock.get_product_by_id.return_value = None
    return mock

@pytest.fixture
def auth_controller_mock(mocker, user_repository_mock):
    """Mocks la clase AuthController."""
    mock = mocker.patch('backend.controllers.auth_controller.AuthController', autospec=True).return_value 
    mock.user_repository = user_repository_mock
    
    mock.config = MagicMock(spec=Config)
    mock.config.GOOGLE_CLIENT_ID = "mock_client_id"
    mock.config.GOOGLE_REDIRECT_URI = "mock_redirect_uri"
    mock.config.GOOGLE_CLIENT_SECRET_FILE = "mock_secret_file.json"
    
    mock.register_user.return_value = {'message': 'Registro exitoso. Ahora puedes iniciar sesión.'}
    mock.login_user.return_value = {'message': 'Inicio de sesión exitoso.'}
    mock.handle_google_callback.return_value = {"id": "google_id", "email": "google@example.com"}

    return mock

@pytest.fixture
def product_controller_mock(mocker):
    """Mocks la clase ProductController."""
    mock = mocker.patch('backend.controllers.product_controller.ProductController', autospec=True).return_value
    mock.get_products.return_value = [] 
    mock.get_product_details.return_value = None
    return mock
