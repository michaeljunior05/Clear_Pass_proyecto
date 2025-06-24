import pytest
from backend.repositories.product_repository import ProductRepository
from backend.models.product import Product
from datetime import datetime, timedelta
from unittest.mock import MagicMock 

# Datos de productos simulados para el ExternalProductService Mock
MOCK_PRODUCTS_DATA_FROM_API = [
    {
        "id": 1,
        "title": "Smartphone X",
        "price": 799.99,
        "description": "Un potente smartphone con cámara avanzada.",
        "category": "electronics",
        "image": "http://example.com/phone.jpg",
        "rating": {"rate": 4.5, "count": 100}
    },
    {
        "id": 2,
        "title": "Laptop Pro",
        "price": 1200.00,
        "description": "Laptop ultraligera para profesionales.",
        "category": "electronics",
        "image": "http://example.com/laptop.jpg",
        "rating": {"rate": 4.8, "count": 75}
    },
    {
        "id": 3,
        "title": "Gold Ring",
        "price": 250.00,
        "description": "Anillo de oro de 18k con incrustaciones.",
        "category": "jewelery",
        "image": "http://example.com/ring.jpg",
        "rating": {"rate": 3.9, "count": 50}
    }
]

@pytest.fixture
def product_repo(external_product_service_mock):
    """Fixture que proporciona una instancia de ProductRepository con un ExternalProductService mockeado."""
    return ProductRepository(external_product_service=external_product_service_mock)

def test_get_all_products_fetches_from_service(product_repo, external_product_service_mock):
    """Verifica que get_all_products llama al servicio externo y devuelve productos mapeados."""
    external_product_service_mock.get_all_products.return_value = MOCK_PRODUCTS_DATA_FROM_API
    
    products = product_repo.get_all_products()
    
    external_product_service_mock.get_all_products.assert_called_once() 
    assert len(products) == len(MOCK_PRODUCTS_DATA_FROM_API)
    assert isinstance(products[0], Product)
    assert products[0].name == "Smartphone X"
    assert products[0].image_url == "http://example.com/phone.jpg" 
    assert products[0].external_id == 1 

def test_get_all_products_with_category_filter(product_repo, external_product_service_mock):
    """Verifica que get_all_products filtra por categoría correctamente a través del servicio."""
    external_product_service_mock.get_products_by_category.return_value = [MOCK_PRODUCTS_DATA_FROM_API[0], MOCK_PRODUCTS_DATA_FROM_API[1]]
    
    products = product_repo.get_all_products(category="electronics")
    
    external_product_service_mock.get_products_by_category.assert_called_once_with("electronics")
    assert len(products) == 2
    assert all(p.category == "electronics" for p in products)

def test_get_all_products_with_query_filter_in_memory(product_repo, external_product_service_mock):
    """Verifica que get_all_products filtra por término de búsqueda en memoria."""
    external_product_service_mock.get_all_products.return_value = MOCK_PRODUCTS_DATA_FROM_API
    
    products = product_repo.get_all_products(query="smartphone")
    
    external_product_service_mock.get_all_products.assert_called_once() 
    assert external_product_service_mock.get_products_by_category.call_count == 0 
    assert len(products) == 1
    assert products[0].name == "Smartphone X"

def test_get_all_products_with_limit(product_repo, external_product_service_mock):
    """Verifica que get_all_products aplica el límite de resultados después del mapeo."""
    external_product_service_mock.get_all_products.return_value = MOCK_PRODUCTS_DATA_FROM_API
    
    products = product_repo.get_all_products(limit=2)
    
    assert len(products) == 2
    assert products[0].name == "Smartphone X"
    assert products[1].name == "Laptop Pro"

def test_get_all_products_returns_empty_list_on_no_data(product_repo, external_product_service_mock):
    """Verifica que devuelve una lista vacía si el servicio no tiene datos."""
    external_product_service_mock.get_all_products.return_value = []
    
    products = product_repo.get_all_products()
    
    assert products == []

def test_get_product_by_id(product_repo, external_product_service_mock):
    """Verifica que get_product_by_id obtiene y mapea un producto específico."""
    external_product_service_mock.get_product_by_id.return_value = MOCK_PRODUCTS_DATA_FROM_API[0]
    
    product = product_repo.get_product_by_id("1")
    
    external_product_service_mock.get_product_by_id.assert_called_once_with("1")
    assert product is not None
    assert product.external_id == 1
    assert product.name == "Smartphone X"

def test_get_product_by_id_not_found(product_repo, external_product_service_mock):
    """Verifica que devuelve None si el producto no se encuentra por ID."""
    external_product_service_mock.get_product_by_id.return_value = None
    
    product = product_repo.get_product_by_id("999")
    
    assert product is None

def test_product_cache_general_products(product_repo, external_product_service_mock, monkeypatch, mocker): # <-- CAMBIO CLAVE: AÑADIR MOCKER
    """Verifica que la caché funciona para get_all_products sin filtros."""
    external_product_service_mock.get_all_products.return_value = MOCK_PRODUCTS_DATA_FROM_API

    mock_datetime = MagicMock(spec=datetime)
    mock_datetime.now.return_value = datetime(2025, 1, 1, 10, 0, 0)
    monkeypatch.setattr("backend.repositories.product_repository.datetime", mock_datetime)

    products1 = product_repo.get_all_products()
    external_product_service_mock.get_all_products.assert_called_once()
    assert len(products1) == 3

    products2 = product_repo.get_all_products()
    external_product_service_mock.get_all_products.assert_called_once() 
    assert len(products2) == 3
    assert products1 is products2 

    mock_datetime.now.return_value = datetime(2025, 1, 1, 10, 6, 0) 
    
    external_product_service_mock.get_all_products.reset_mock() 
    products3 = product_repo.get_all_products()
    external_product_service_mock.get_all_products.assert_called_once() 
    assert len(products3) == 3

def test_product_cache_with_different_keys(product_repo, external_product_service_mock, monkeypatch, mocker): # <-- CAMBIO CLAVE: AÑADIR MOCKER
    """Verifica que la caché maneja diferentes claves (query, category) de forma independiente."""
    external_product_service_mock.get_products_by_category.side_effect = lambda cat: [MOCK_PRODUCTS_DATA_FROM_API[0]] if cat == "electronics" else []
    external_product_service_mock.get_all_products.return_value = MOCK_PRODUCTS_DATA_FROM_API 

    mock_datetime = MagicMock(spec=datetime)
    mock_datetime.now.return_value = datetime(2025, 1, 1, 10, 0, 0)
    monkeypatch.setattr("backend.repositories.product_repository.datetime", mock_datetime)

    products_all_1 = product_repo.get_all_products()
    external_product_service_mock.get_all_products.assert_called_once()
    assert len(products_all_1) == 3

    products_electronics_1 = product_repo.get_all_products(category="electronics")
    external_product_service_mock.get_products_by_category.assert_called_once_with("electronics")
    assert len(products_electronics_1) == 1

    external_product_service_mock.get_all_products.reset_mock()
    products_all_2 = product_repo.get_all_products()
    external_product_service_mock.get_all_products.assert_not_called()
    assert len(products_all_2) == 3

    external_product_service_mock.get_products_by_category.reset_mock()
    products_electronics_2 = product_repo.get_all_products(category="electronics")
    external_product_service_mock.get_products_by_category.assert_not_called()
    assert len(products_electronics_2) == 1

    assert products_all_1 is products_all_2 
    assert products_electronics_1 is products_electronics_2 
    assert products_all_1 is not products_electronics_1 
