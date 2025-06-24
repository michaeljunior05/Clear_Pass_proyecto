import pytest
import requests # Importa la librería real requests para mockearla
from backend.services.external_product_service import ExternalProductService

# Datos de productos simulados de la API externa
MOCK_API_RESPONSE_ALL_PRODUCTS = [
    {"id": 1, "title": "Product A", "price": 10.0, "category": "electronics", "image": "url_a", "description": "Desc A", "rating": {"rate": 4.0, "count": 10}},
    {"id": 2, "title": "Product B", "price": 20.0, "category": "jewelery", "image": "url_b", "description": "Desc B", "rating": {"rate": 3.5, "count": 20}}
]

MOCK_API_RESPONSE_ELECTRONICS = [
    {"id": 1, "title": "Product A", "price": 10.0, "category": "electronics", "image": "url_a", "description": "Desc A", "rating": {"rate": 4.0, "count": 10}}
]

MOCK_API_RESPONSE_SINGLE_PRODUCT = {"id": 1, "title": "Product A", "price": 10.0, "category": "electronics", "image": "url_a", "description": "Desc A", "rating": {"rate": 4.0, "count": 10}}


@pytest.fixture
def external_product_service():
    """Fixture que proporciona una instancia de ExternalProductService."""
    return ExternalProductService(base_url="http://fakestoreapi.com")

def test_get_all_products_success(external_product_service, mocker):
    """Verifica que get_all_products obtiene todos los productos correctamente."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_API_RESPONSE_ALL_PRODUCTS
    mock_response.raise_for_status.return_value = None # Simula una respuesta HTTP exitosa

    mocker.patch('requests.get', return_value=mock_response) # Mockea requests.get

    products = external_product_service.get_all_products()

    assert len(products) == 2
    assert products[0]['title'] == "Product A"
    requests.get.assert_called_once_with("http://fakestoreapi.com/products", timeout=10)

def test_get_all_products_http_error(external_product_service, mocker):
    """Verifica que get_all_products maneja errores HTTP."""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError # Simula un error HTTP
    
    mocker.patch('requests.get', return_value=mock_response)

    products = external_product_service.get_all_products()

    assert products is None
    requests.get.assert_called_once()

def test_get_all_products_connection_error(external_product_service, mocker):
    """Verifica que get_all_products maneja errores de conexión."""
    mocker.patch('requests.get', side_effect=requests.exceptions.ConnectionError) # Simula error de conexión

    products = external_product_service.get_all_products()

    assert products is None
    requests.get.assert_called_once()

def test_get_products_by_category_success(external_product_service, mocker):
    """Verifica que get_products_by_category obtiene productos por categoría correctamente."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_API_RESPONSE_ELECTRONICS
    mock_response.raise_for_status.return_value = None

    mocker.patch('requests.get', return_value=mock_response)

    products = external_product_service.get_products_by_category("electronics")

    assert len(products) == 1
    assert products[0]['category'] == "electronics"
    requests.get.assert_called_once_with("http://fakestoreapi.com/products/category/electronics", timeout=10)

def test_get_products_by_category_404_returns_empty_list(external_product_service, mocker):
    """Verifica que 404 para categoría devuelve una lista vacía."""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = [] # Algunas APIs devuelven lista vacía con 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError # Raise for 404

    mocker.patch('requests.get', return_value=mock_response)

    products = external_product_service.get_products_by_category("nonexistent")

    assert products == [] # Debe devolver una lista vacía, no None
    requests.get.assert_called_once()


def test_get_product_by_id_success(external_product_service, mocker):
    """Verifica que get_product_by_id obtiene un solo producto correctamente."""
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_API_RESPONSE_SINGLE_PRODUCT
    mock_response.raise_for_status.return_value = None

    mocker.patch('requests.get', return_value=mock_response)

    product = external_product_service.get_product_by_id("1")

    assert product['title'] == "Product A"
    requests.get.assert_called_once_with("http://fakestoreapi.com/products/1", timeout=10)

def test_get_product_by_id_not_found(external_product_service, mocker):
    """Verifica que get_product_by_id devuelve None si no se encuentra el producto."""
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError # Simula 404
    
    mocker.patch('requests.get', return_value=mock_response)

    product = external_product_service.get_product_by_id("999")

    assert product is None
    requests.get.assert_called_once()

def test_external_product_service_init_no_base_url():
    """Verifica que el servicio lanza un error si la base_url está vacía."""
    with pytest.raises(ValueError, match="The base URL for the ExternalProductService cannot be empty."):
        ExternalProductService(base_url="")
