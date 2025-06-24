import pytest
from backend.models.user import User
from backend.controllers.auth_controller import AuthController 
from flask import session 
from config import Config 

@pytest.fixture
def auth_controller_instance(user_repository_mock, mocker):
    """Fixture para crear una instancia real de AuthController con dependencias mockeadas."""
    mock_config = mocker.Mock(spec=Config)
    mock_config.GOOGLE_CLIENT_ID = "test_client_id"
    mock_config.GOOGLE_REDIRECT_URI = "test_redirect_uri"
    mock_config.GOOGLE_CLIENT_SECRET_FILE = "test_secret_file.json"
    
    return AuthController(user_repository=user_repository_mock, config=mock_config)


def test_register_user_success(auth_controller_instance, user_repository_mock, app):
    """Verifica que register_user registra un nuevo usuario con éxito."""
    email = "newuser@example.com"
    password = "SecurePassword123"

    user_repository_mock.find_user_by_email.return_value = None 
    
    # CAMBIO CLAVE AQUÍ: Aseguramos que el mock devuelve el ID que vamos a asertar
    expected_user_id = "test_user_id_from_mock" # Definir un ID esperado
    mock_added_user = User(_id=expected_user_id, email=email, name=email.split('@')[0], password="hashed_pass")
    user_repository_mock.add_user.return_value = mock_added_user

    with app.test_request_context(): 
        result = auth_controller_instance.register_user(email, password)
        
        assert result == {'message': 'Registro exitoso. Ahora puedes iniciar sesión.'}
        user_repository_mock.find_user_by_email.assert_called_once_with(email)
        user_repository_mock.add_user.assert_called_once() 
        assert 'user_id' in session
        assert session['user_id'] == expected_user_id # Asegurar que el ID esperado es el que se asertó
        assert session['user_name'] == email.split('@')[0]
        assert session['user_email'] == email

def test_register_user_email_already_exists(auth_controller_instance, user_repository_mock, app):
    """Verifica que register_user falla si el email ya existe."""
    email = "existing@example.com"
    password = "Password123"

    user_repository_mock.find_user_by_email.return_value = User(_id="existing_id", email=email, name="Existing") 

    with app.test_request_context():
        result = auth_controller_instance.register_user(email, password)
        
        assert result == {'message': 'El email ya está registrado.'}
        user_repository_mock.find_user_by_email.assert_called_once_with(email)
        user_repository_mock.add_user.assert_not_called() 

def test_login_user_success(auth_controller_instance, user_repository_mock, app):
    """Verifica que login_user autentica un usuario con éxito."""
    email = "test@example.com"
    password = "CorrectPassword123"

    mock_logged_in_user = User(_id="user456", email=email, name="Logged In User", password="hashed_pass")
    user_repository_mock.find_user_by_email_and_password.return_value = mock_logged_in_user

    with app.test_request_context():
        result = auth_controller_instance.login_user(email, password)
        
        assert result == {'message': 'Inicio de sesión exitoso.'}
        user_repository_mock.find_user_by_email_and_password.assert_called_once_with(email, password)
        assert 'user_id' in session
        assert session['user_id'] == "user456"
        assert session['user_name'] == "Logged In User"
        assert session['user_email'] == email

def test_login_user_invalid_credentials(auth_controller_instance, user_repository_mock, app):
    """Verifica que login_user falla con credenciales incorrectas."""
    email = "wrong@example.com"
    password = "WrongPassword"

    user_repository_mock.find_user_by_email_and_password.return_value = None 

    with app.test_request_context():
        result = auth_controller_instance.login_user(email, password)
        
        assert result == {'message': 'Email o contraseña incorrectos.'}
        user_repository_mock.find_user_by_email_and_password.assert_called_once_with(email, password)
        assert 'user_id' not in session
