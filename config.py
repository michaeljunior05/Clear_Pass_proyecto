# config.py
import os

class Config:
    """
    Clase de configuración para la aplicación Flask.
    Contiene variables de entorno y constantes necesarias para el funcionamiento.
    """
    # Clave secreta para la seguridad de la sesión de Flask.
    # Es crucial que esta clave sea fuerte y no se exponga públicamente.
    # En producción, se recomienda obtenerla de una variable de entorno.
    SECRET_KEY = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui_CAMBIAR_EN_PRODUCCION_!') # ¡CAMBIA ESTO EN PRODUCCIÓN!

    # Configuración de Google OAuth 2.0
    # El ID del cliente de Google de tu aplicación web (obtenido de Google Cloud Console)
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '222270840199-pcntooj9dsvmsn79j11glth1fueaurij.apps.googleusercontent.com')
    # La ruta al archivo JSON de secretos del cliente de Google (descargado de Google Cloud Console)
    # AJUSTA ESTA RUTA: Asume que 'client_secret.json' está en la raíz de tu proyecto.
    # Si está en 'Clear_Pass_proyecto/credentials/client_secret.json', la ruta sería 'credentials/client_secret.json'.
    OOGLE_CLIENT_SECRET_FILE = os.environ.get('GOOGLE_CLIENT_SECRET_FILE', 'credentials/client_secret.json')
    # La URI de redirección configurada en Google Cloud Console para tu aplicación.
    # Debe coincidir exactamente.
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://127.0.0.1:5000/auth/google/callback')


    # URL base para la API externa de productos (ej. FakeStoreAPI, RapidAPI, etc.)
    EXTERNAL_PRODUCTS_API_BASE_URL = os.environ.get('EXTERNAL_PRODUCTS_API_BASE_URL', 'https://fakestoreapi.com')
    # Clave de API para la API externa de productos (si es requerida)
    EXTERNAL_PRODUCTS_API_KEY = os.environ.get('EXTERNAL_PRODUCTS_API_KEY', '') # Dejar vacío si no se usa API Key


    # Ruta al archivo de la base de datos JSON (relativa a la raíz del proyecto)
    JSON_DATABASE_PATH = 'database/data.json'