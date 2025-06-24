# backend/routes/importer_routes.py
from flask import Blueprint, jsonify, request, session
import logging

# Se importarán después con la función de inicialización
# from backend.repositories.importer_repository import ImporterRepository
# from backend.services.importer_ranking_service import ImporterRankingService
# from backend.repositories.user_repository import UserRepository # Para verificar premium

logger = logging.getLogger(__name__)

importer_bp = Blueprint('importer_bp', __name__)

_importer_ranking_service = None
_user_repository = None # Guardaremos el repositorio de usuarios aquí

def init_importer_routes(ranking_service, user_repo):
    """
    Inicializa las rutas de importadores con sus dependencias.
    Esta función debe ser llamada desde app.py.
    """
    global _importer_ranking_service, _user_repository
    _importer_ranking_service = ranking_service
    _user_repository = user_repo
    logger.info("Rutas de importadores inicializadas con el servicio de ranking y repositorio de usuarios.")

# Función auxiliar para verificar si el usuario es premium
def is_premium_user_check():
    user_id = session.get('user_id')
    if not user_id:
        logger.warning("Intento de acceso a funcionalidad premium sin usuario en sesión.")
        return False
    
    if not _user_repository:
        logger.error("UserRepository no inicializado en rutas de importadores. Fallo en verificación premium.")
        return False

    user = _user_repository.get_user_by_id(user_id)
    if user and user.is_premium:
        logger.info(f"Usuario {user_id} ({user.email}) es premium. Acceso concedido.")
        return True
    
    logger.warning(f"Usuario {user_id} no es premium o no encontrado. Acceso denegado.")
    return False

@importer_bp.route('/api/importers/ranking', methods=['GET'])
def get_importers_ranking():
    """
    Endpoint para obtener el ranking de importadores.
    Acepta un parámetro de query 'criteria' y 'country' para especificar el criterio de ranking y filtro.
    """
    criteria = request.args.get('criteria', 'import_volume_usd')
    country = request.args.get('country') 

    if not _importer_ranking_service:
        logger.error("ImporterRankingService no inicializado.")
        return jsonify({"error": "Servicio de ranking no disponible"}), 500

    ranked_importers = _importer_ranking_service.get_ranked_importers(criteria=criteria, country=country)
    return jsonify(ranked_importers), 200

@importer_bp.route('/api/importers/topN', methods=['GET'])
def get_top_n_importers():
    """
    Endpoint para obtener los N mejores importadores.
    Acepta parámetros de query 'n' (cantidad), 'criteria' (criterio de ranking) y 'country'.
    Esta es una característica premium.
    """
    if not is_premium_user_check():
        return jsonify({"message": "Acceso denegado. Esta característica es solo para suscriptores premium."}), 403

    try:
        n = int(request.args.get('n', 10)) 
    except ValueError:
        return jsonify({"error": "El parámetro 'n' debe ser un número entero."}), 400

    criteria = request.args.get('criteria', 'import_volume_usd')
    country = request.args.get('country')

    if not _importer_ranking_service:
        logger.error("ImporterRankingService no inicializado.")
        return jsonify({"error": "Servicio de ranking no disponible"}), 500

    top_importers = _importer_ranking_service.get_top_n_importers(n=n, criteria=criteria, country=country)
    return jsonify(top_importers), 200

@importer_bp.route('/api/importers/chinese/top10', methods=['GET'])
def get_top_10_chinese_importers():
    """
    Endpoint específico para los 10 mejores importadores chinos.
    Esta es la funcionalidad "estrella" y debe ser premium.
    """
    if not is_premium_user_check():
        return jsonify({"message": "Acceso denegado. El ranking de los 10 mejores importadores chinos es exclusivo para suscriptores premium."}), 403

    criteria = request.args.get('criteria', 'import_volume_usd') 

    if not _importer_ranking_service:
        logger.error("ImporterRankingService no inicializado.")
        return jsonify({"error": "Servicio de ranking no disponible"}), 500

    top_10_importers = _importer_ranking_service.get_top_10_chinese_importers(criteria=criteria)
    return jsonify(top_10_importers), 200

@importer_bp.route('/api/importers', methods=['GET'])
def get_all_importers_api():
    """
    Endpoint para obtener todos los importadores sin ranking ni filtro,
    accesible para todos.
    """
    if not _importer_ranking_service or not _importer_ranking_service.importer_repo:
        logger.error("ImporterRepository no inicializado.")
        return jsonify({"error": "Repositorio de importadores no disponible"}), 500

    importers = _importer_ranking_service.importer_repo.get_all_importers() # Accede al repo a través del servicio
    return jsonify([imp.to_dict() for imp in importers]), 200 # Asegura que se devuelven diccionarios

