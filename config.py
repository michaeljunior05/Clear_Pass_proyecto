import os
from datetime import timedelta

class Config:
    """
    Clase de configuración para la aplicación Flask.
    Gestiona variables de entorno, claves secretas y configuraciones de servicios.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_super_secret_key_if_not_set')
    
    # Configuración de Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '222270840199-pcntooj9dsvmsn79j11glth1fueaurij.apps.googleusercontent.com')
    # ¡IMPORTANTE! Esta URI debe coincidir EXACTAMENTE con la configurada en Google Cloud Console.
    # Además, debe coincidir con la ruta real en tu aplicación Flask (incluyendo el prefijo /api).
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5000/api/auth/google/callback')
    # Ruta al archivo JSON de secretos del cliente de Google.
    # Asegúrate de que este archivo exista en la ruta especificada.
    GOOGLE_CLIENT_SECRET_FILE = os.environ.get('GOOGLE_CLIENT_SECRET_FILE', 'credentials/client_secret.json') # Asegúrate de que esta ruta es correcta

    # Configuración de la API externa de productos (ej. FakeStoreAPI)
    EXTERNAL_PRODUCTS_API_BASE_URL = os.environ.get('EXTERNAL_PRODUCTS_API_BASE_URL', 'https://fakestoreapi.com')
    EXTERNAL_PRODUCTS_API_KEY = os.environ.get('EXTERNAL_PRODUCTS_API_KEY', 'your_external_api_key_if_needed') # Si la API externa requiere una clave

    # Configuración de la base de datos JSON (para JSONStorage)
    JSON_DATABASE_PATH = os.environ.get('JSON_DATABASE_PATH', 'data.json')

    # Configuración de sesión (por defecto para Flask-Session)
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24) # Duración de la sesión

    # Categorías consideradas como "tecnología" para el filtrado de productos
    # CENTRALIZADO AQUÍ PARA EVITAR DEPENDENCIAS CIRCULARES
    TECHNOLOGY_CATEGORIES = ['electronics'] 
    
