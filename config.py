import os
from datetime import timedelta

class Config:
    """
    Clase de configuración para la aplicación Flask.
    Gestiona variables de entorno, claves secretas y configuraciones de servicios.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_super_secret_key_if_not_set')
    
    # Configuración de Google OAuth
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '967793497246-m78gm3m77u9ebqgpev7h10op0lbpqepg.apps.googleusercontent.com')
    # ¡IMPORTANTE! Esta URI debe coincidir EXACTAMENTE con la configurada en Google Cloud Console Y AHORA DEBE SER HTTPS
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'https://127.0.0.1:5000/api/auth/google/callback')
    # Ruta al archivo JSON de secretos del cliente de Google.
    # Asegúrate de que este archivo exista en la ruta especificada.
    GOOGLE_CLIENT_SECRET_FILE = os.environ.get('GOOGLE_CLIENT_SECRET_FILE', 'credentials/client_secret.json') 

    # Configuración de la API externa de productos (ej. FakeStoreAPI)
    EXTERNAL_PRODUCTS_API_BASE_URL = os.environ.get('EXTERNAL_PRODUCTS_API_BASE_URL', 'https://dummyjson.com')
    EXTERNAL_PRODUCTS_API_KEY = os.environ.get('EXTERNAL_PRODUCTS_API_KEY', 'your_external_api_key_if_needed') 

    # Configuración de la base de datos JSON (para JSONStorage)
    JSON_DATABASE_PATH = os.environ.get('JSON_DATABASE_PATH', 'data.json')

    # Configuración de sesión (por defecto para Flask-Session)
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24) 

    # Categorías consideradas como "tecnología" para el filtrado de productos
    TECHNOLOGY_CATEGORIES = ['electronics'] 
    
