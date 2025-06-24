import pytest
from flask import json, session
from backend.routes.auth_routes import init_auth_routes
from backend.models.user import User # Importa el modelo User

# Asegúrate de que las fixtures de conftest.py estén disponibles
# app, client, auth_controller_mock

@pytest.fixture(autouse=True)
def setup_auth_routes(app, auth_controller_mock):
    """Inicializa las rutas de autenticación con el controlador mockeado antes de cada test."""
    with app.app_context(): # Es importante estar dentro del contexto de la aplicación
        init_auth_routes(auth_controller_mock)

def test_register_success(client, auth_controller_mock):
    """Verifica que el registro de usuario es exitoso."""
    auth_controller_mock.register_user.return_value = {'message': 'Registro exitoso. Ahora puedes iniciar sesión.'}
    
    response = client.post(
        '/api/register',
        data={
            'email': 'test@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Registro exitoso. Ahora puedes iniciar sesión.'
    auth_controller_mock.register_user.assert_called_once_with('test@example.com', 'Password123')

def test_register_passwords_mismatch(client, auth_controller_mock):
    """Verifica que el registro falla si las contraseñas no coinciden."""
    response = client.post(
        '/api/register',
        data={
            'email': 'test@example.com',
            'password': 'Password123',
            'confirm_password': 'MismatchPass'
        }
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == 'Las contraseñas no coinciden.'
    auth_controller_mock.register_user.assert_not_called() # Asegura que el controlador no fue llamado

def test_register_email_already_exists(client, auth_controller_mock):
    """Verifica que el registro falla si el email ya está registrado."""
    auth_controller_mock.register_user.return_value = {'message': 'El email ya está registrado.'}
    
    response = client.post(
        '/api/register',
        data={
            'email': 'existing@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }
    )
    
    assert response.status_code == 409 # Conflicto
    data = json.loads(response.data)
    assert data['message'] == 'El email ya está registrado.'
    auth_controller_mock.register_user.assert_called_once()

def test_login_success(client, auth_controller_mock, app):
    """Verifica que el inicio de sesión es exitoso."""
    # Simular un usuario retornado por el repositorio, que es lo que el controlador espera
    mock_user = User(_id="user123", email="test@example.com", name="Test User")
    auth_controller_mock.login_user.return_value = {'message': 'Inicio de sesión exitoso.'} # El controlador retorna un dict
    
    response = client.post(
        '/api/login',
        data={'email': 'test@example.com', 'password': 'Password123'}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Inicio de sesión exitoso.'
    auth_controller_mock.login_user.assert_called_once_with('test@example.com', 'Password123')
    
    # Después de un login exitoso, la sesión debería contener el user_id.
    # Necesitamos acceder a la sesión para verificarlo.
    with client.session_transaction() as sess:
        # Nota: el controlador de auth que mockeamos no pone el user_id en la sesión.
        # Si quisiéramos probar eso, tendríamos que mockear el controlador para que lo haga,
        # o probar el AuthController directamente en su propio test.
        # Por ahora, solo verificamos que la ruta devuelve 200.
        pass # La verificación de sesión se hará en test_auth_controller.py


def test_login_invalid_credentials(client, auth_controller_mock):
    """Verifica que el inicio de sesión falla con credenciales inválidas."""
    auth_controller_mock.login_user.return_value = {'message': 'Email o contraseña incorrectos.'}
    
    response = client.post(
        '/api/login',
        data={'email': 'wrong@example.com', 'password': 'WrongPass'}
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['message'] == 'Email o contraseña incorrectos.'
    auth_controller_mock.login_user.assert_called_once()
