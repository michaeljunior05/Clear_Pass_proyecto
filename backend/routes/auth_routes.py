# backend/routes/auth_routes.py
from flask import Blueprint, jsonify, request, session, url_for, redirect
import logging
import google_auth_oauthlib.flow # Asegúrate de que esta importación esté presente si usas OAuth

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth_bp', __name__)

_auth_controller = None 

def init_auth_routes(controller):
    """
    Inicializa las rutas de autenticación con el controlador inyectado.
    Esta función debe ser llamada desde app.py.
    """
    global _auth_controller
    _auth_controller = controller
    logger.info("Rutas de autenticación inicializadas con el controlador.")

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Ruta para el registro de nuevos usuarios.
    Extrae datos de request.form y los pasa al AuthController.
    """
    logger.info("Petición POST recibida en /api/register (form-urlencoded)")
    if not _auth_controller:
        logger.error("AuthController no inicializado.")
        return jsonify({"message": "Servicio de autenticación no disponible"}), 500
    
    # Usar request.form.get() como en tu versión actual
    email = request.form.get('email')
    password = request.form.get('password')
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    dni = request.form.get('dni')

    # El controlador ahora devuelve la tupla (jsonify_obj, status_code)
    json_response_obj, status_code = _auth_controller.register_user(
        email=email, password=password, name=name, phone_number=phone_number, dni=dni
    ) 
    
    # Si el registro fue exitoso, el controlador ya debería haber gestionado la sesión.
    # El jsonify_obj ya es un objeto Flask.jsonify, solo lo devolvemos junto con el status_code.
    return json_response_obj, status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Ruta para el inicio de sesión de usuarios.
    Extrae datos de request.form y los pasa al AuthController.
    """
    logger.info("Petición POST recibida en /api/login (form-urlencoded)")
    if not _auth_controller:
        logger.error("AuthController no inicializado.")
        return jsonify({"message": "Servicio de autenticación no disponible"}), 500
    
    # Usar request.form.get() como en tu versión actual
    email = request.form.get('email')
    password = request.form.get('password')

    # El controlador ahora devuelve la tupla (jsonify_obj, status_code)
    json_response_obj, status_code = _auth_controller.login_user(email=email, password=password)
    return json_response_obj, status_code

@auth_bp.route('/auth/google-login', methods=['POST'])
def google_login_api():
    """
    Ruta para manejar el inicio de sesión/registro con Google (GSI).
    Sigue esperando el JWT en el cuerpo JSON (manejado por el controlador).
    """
    logger.info("Petición POST recibida en /api/auth/google-login (JSON)")
    if not _auth_controller:
        logger.error("AuthController no inicializado.")
        return jsonify({"message": "Servicio de autenticación no disponible"}), 500
    
    # El controlador ahora devuelve la tupla (jsonify_obj, status_code)
    json_response_obj, status_code = _auth_controller.google_login()
    return json_response_obj, status_code

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Ruta para cerrar la sesión del usuario.
    """
    logger.info("Petición POST recibida en /api/logout")
    if not _auth_controller:
        logger.error("AuthController no inicializado.")
        return jsonify({"message": "Servicio de autenticación no disponible"}), 500
    
    # El controlador ahora devuelve la tupla (jsonify_obj, status_code)
    json_response_obj, status_code = _auth_controller.logout_user()
    return json_response_obj, status_code

@auth_bp.route('/session', methods=['GET'])
def get_session():
    """
    Ruta para obtener información de la sesión actual.
    """
    logger.info("Petición GET recibida en /api/session")
    if not _auth_controller:
        logger.error("AuthController no inicializado.")
        return jsonify({"message": "Servicio de autenticación no disponible"}), 500
    
    # El controlador ahora devuelve la tupla (jsonify_obj, status_code)
    json_response_obj, status_code = _auth_controller.get_session_info()
    return json_response_obj, status_code

@auth_bp.route('/profile/update', methods=['PUT'])
def update_profile():
    """
    Ruta para actualizar el perfil del usuario.
    Sigue esperando JSON.
    """
    logger.info("Petición PUT recibida en /api/profile/update (JSON)")
    if not _auth_controller:
        logger.error("AuthController no inicializado.")
        return jsonify({"message": "Servicio de autenticación no disponible"}), 500
    
    # El controlador ahora devuelve la tupla (jsonify_obj, status_code)
    json_response_obj, status_code = _auth_controller.update_user_profile()
    return json_response_obj, status_code

# Oauth Flow (si lo estás usando, también ajustar si es necesario, pero este flujo suele ser de redirección)
@auth_bp.route('/auth/google-oauth-init') 
def google_oauth_init():
    """
    Inicia el flujo de autorización de Google OAuth 2.0 (NO GSI).
    """
    if not _auth_controller:
        return jsonify({"message": "Servicio de autenticación no disponible"}), 500

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        _auth_controller.config.GOOGLE_CLIENT_SECRET_FILE,
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid'],
        redirect_uri=_auth_controller.config.GOOGLE_REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['oauth_state'] = state
    return redirect(authorization_url)

@auth_bp.route('/auth/google-oauth-callback')
def google_oauth_callback():
    """
    Maneja el callback de Google OAuth 2.0 (NO GSI).
    """
    if not _auth_controller:
        return jsonify({"message": "Servicio de autenticación no disponible"}), 500

    state = session.pop('oauth_state', None)
    if not state or state != request.args.get('state'):
        logger.error("Estado de OAuth inválido o faltante.")
        return jsonify({"message": "Estado de la solicitud inválido."}), 400

    code = request.args.get('code')
    if not code:
        logger.warning("No se recibió el código de autorización de Google.")
        return jsonify({"message": "Código de autorización no proporcionado."}), 400

    # === CAMBIO CLAVE AQUÍ: Llama al método del controlador y maneja su resultado ===
    json_response_obj, status_code = _auth_controller.handle_google_callback(code)

    # El controlador ahora es responsable de manejar la sesión y la redirección interna
    # Aquí solo verificamos el resultado y devolvemos la respuesta JSON
    if status_code == 200: # Si es exitoso, el controlador ya debió haber gestionado la sesión
        # No redirigimos aquí, el controlador ya lo hizo o devolvemos JSON
        return json_response_obj, status_code
    else:
        return json_response_obj, status_code # Devuelve el error JSON y el código de estado
