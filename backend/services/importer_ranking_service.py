# backend/services/importer_ranking_service.py
from backend.repositories.importer_repository import ImporterRepository
from backend.models.importer import Importer # Necesario para convertir a objetos Importer
from typing import List, Dict, Any

# Datos de importadores chinos mockeados para demostración
# Estos datos cumplen con la estructura del modelo Importer.
MOCKED_CHINESE_IMPORTERS_DATA = [
    {
        "id": "mock_imp_cn_1",
        "company_name": "Dragon Trade Solutions",
        "ruc": "RUC12345678901",
        "country_of_origin": "China",
        "contact_email": "contact@dragontech.com",
        "contact_phone": "+86-10-12345678",
        "fiscal_address": "123 Jinmao Tower, Shanghai",
        "specialty_products": ["Electronics", "Gadgets"],
        "registration_date": "2010-01-15",
        "import_volume_usd": 30000000,
        "years_in_business": 15,
        "successful_imports": 2800,
        "client_satisfaction_rating": 4.9
    },
    {
        "id": "mock_imp_cn_2",
        "company_name": "Silk Road Imports Ltd.",
        "ruc": "RUC12345678902",
        "country_of_origin": "China",
        "contact_email": "info@silkroad.com",
        "contact_phone": "+86-21-87654321",
        "fiscal_address": "456 Bund Center, Shanghai",
        "specialty_products": ["Textiles", "Apparel"],
        "registration_date": "2008-05-20",
        "import_volume_usd": 28000000,
        "years_in_business": 17,
        "successful_imports": 2500,
        "client_satisfaction_rating": 4.8
    },
    {
        "id": "mock_imp_cn_3",
        "company_name": "Great Wall Sourcing",
        "ruc": "RUC12345678903",
        "country_of_origin": "China",
        "contact_email": "sales@greatwall.com",
        "contact_phone": "+86-755-11223344",
        "fiscal_address": "789 Futian District, Shenzhen",
        "specialty_products": ["Machinery", "Industrial Goods"],
        "registration_date": "2012-11-01",
        "import_volume_usd": 26000000,
        "years_in_business": 13,
        "successful_imports": 2200,
        "client_satisfaction_rating": 4.7
    },
    {
        "id": "mock_imp_cn_4",
        "company_name": "Pearl River Logistics",
        "ruc": "RUC12345678904",
        "country_of_origin": "China",
        "contact_email": "support@pearlriver.com",
        "contact_phone": "+86-20-55667788",
        "fiscal_address": "101 Tianhe Road, Guangzhou",
        "specialty_products": ["Consumer Goods", "Home Appliances"],
        "registration_date": "2011-03-25",
        "import_volume_usd": 24000000,
        "years_in_business": 14,
        "successful_imports": 2100,
        "client_satisfaction_rating": 4.6
    },
    {
        "id": "mock_imp_cn_5",
        "company_name": "Panda Global Trade",
        "ruc": "RUC12345678905",
        "country_of_origin": "China",
        "contact_email": "admin@pandaglobal.com",
        "contact_phone": "+86-28-99887766",
        "fiscal_address": "222 Chengdu Street, Chengdu",
        "specialty_products": ["Toys", "Sporting Goods"],
        "registration_date": "2014-07-10",
        "import_volume_usd": 22000000,
        "years_in_business": 11,
        "successful_imports": 1900,
        "client_satisfaction_rating": 4.5
    },
    {
        "id": "mock_imp_cn_6",
        "company_name": "Yellow River Sourcing",
        "ruc": "RUC12345678906",
        "country_of_origin": "China",
        "contact_email": "contact@yellowriver.com",
        "contact_phone": "+86-371-11223355",
        "fiscal_address": "333 Zhengzhou Avenue, Zhengzhou",
        "specialty_products": ["Agricultural Products", "Raw Materials"],
        "registration_date": "2009-09-01",
        "import_volume_usd": 20000000,
        "years_in_business": 16,
        "successful_imports": 1700,
        "client_satisfaction_rating": 4.4
    },
    {
        "id": "mock_imp_cn_7",
        "company_name": "Phoenix Rising Imports",
        "ruc": "RUC12345678907",
        "country_of_origin": "China",
        "contact_email": "info@phoeniximports.com",
        "contact_phone": "+86-25-88990011",
        "fiscal_address": "444 Nanjing Road, Nanjing",
        "specialty_products": ["Construction Materials", "Chemicals"],
        "registration_date": "2013-04-18",
        "import_volume_usd": 18000000,
        "years_in_business": 12,
        "successful_imports": 1600,
        "client_satisfaction_rating": 4.3
    },
    {
        "id": "mock_imp_cn_8",
        "company_name": "Yangtze Trade Bridge",
        "ruc": "RUC12345678908",
        "country_of_origin": "China",
        "contact_email": "bridge@yangtze.com",
        "contact_phone": "+86-27-22334455",
        "fiscal_address": "555 Wuhan Blvd, Wuhan",
        "specialty_products": ["Automotive Parts", "Heavy Equipment"],
        "registration_date": "2015-08-05",
        "import_volume_usd": 16000000,
        "years_in_business": 10,
        "successful_imports": 1400,
        "client_satisfaction_rating": 4.2
    },
    {
        "id": "mock_imp_cn_9",
        "company_name": "Cloud Dragon Exports",
        "ruc": "RUC12345678909",
        "country_of_origin": "China",
        "contact_email": "export@clouddragon.com",
        "contact_phone": "+86-23-66778899",
        "fiscal_address": "666 Jiefangbei, Chongqing",
        "specialty_products": ["IT Hardware", "Software Services"],
        "registration_date": "2016-10-10",
        "import_volume_usd": 14000000,
        "years_in_business": 9,
        "successful_imports": 1200,
        "client_satisfaction_rating": 4.1
    },
    {
        "id": "mock_imp_cn_10",
        "company_name": "Mandarin Supply Chain",
        "ruc": "RUC12345678910",
        "country_of_origin": "China",
        "contact_email": "supply@mandarin.com",
        "contact_phone": "+86-571-33445566",
        "fiscal_address": "777 West Lake District, Hangzhou",
        "specialty_products": ["Medical Devices", "Pharmaceuticals"],
        "registration_date": "2017-12-01",
        "import_volume_usd": 12000000,
        "years_in_business": 8,
        "successful_imports": 1000,
        "client_satisfaction_rating": 4.0
    }
]

class ImporterRankingService:
    """
    Contiene la lógica de negocio para generar el ranking de importadores.
    Bajo acoplamiento: Depende de la interfaz del repositorio, no de su implementación.
    """
    def __init__(self, importer_repository: ImporterRepository):
        self.importer_repo = importer_repository

    def get_ranked_importers(self, criteria='import_volume_usd', country=None) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de importadores y los clasifica según un criterio dado.
        Permite filtrar por país opcionalmente.
        Por defecto, clasifica por 'import_volume_usd' de mayor a menor.
        Retorna una lista de diccionarios (la representación to_dict de los importadores).
        """
        importers = self.importer_repo.get_all_importers()

        if not importers:
            return []

        # Filtrar por país si se especifica
        if country:
            # Aseguramos que la comparación sea insensible a mayúsculas/minúsculas
            importers = [imp for imp in importers if imp.country_of_origin.lower() == country.lower()]

        if not importers: # Si no quedan importadores después de filtrar por país
            return []

        # Validar el criterio de ranking
        valid_criteria = ['import_volume_usd', 'years_in_business', 'successful_imports', 'client_satisfaction_rating']
        if criteria not in valid_criteria:
            print(f"Advertencia: Criterio de ranking '{criteria}' no válido. Usando 'import_volume_usd'.")
            criteria = 'import_volume_usd'

        # Ordenar los importadores según el criterio.
        def get_sort_key(importer):
            return getattr(importer, criteria, 0) # 0 como valor por defecto si la clave no existe

        ranked_importers = sorted(importers, key=get_sort_key, reverse=True)

        return [imp.to_dict() for imp in ranked_importers]

    def get_top_n_importers(self, n=10, criteria='import_volume_usd', country=None) -> List[Dict[str, Any]]:
        """
        Obtiene los 'n' mejores importadores según el ranking, con filtro opcional por país.
        Este método es clave para la funcionalidad premium.
        Retorna una lista de diccionarios.
        """
        n = max(0, int(n))
        ranked_importers = self.get_ranked_importers(criteria, country)
        return ranked_importers[:n]

    def get_top_10_chinese_importers(self, criteria='import_volume_usd') -> List[Dict[str, Any]]:
        """
        Obtiene los 10 mejores importadores chinos según un criterio específico.
        Esta es la funcionalidad "estrella" para premium y ahora usa datos mockeados.
        """
        # Convertir los datos mockeados a objetos Importer para consistencia
        mocked_importers = [Importer.from_dict(data) for data in MOCKED_CHINESE_IMPORTERS_DATA]
        
        # Opcional: Podrías aplicar el criterio de ordenamiento a los mockeados si quieres que el "top 10" sea dinámico entre ellos
        # Forzamos que el criterio sea el que el usuario pida, y ordenamos los mocks
        valid_criteria = ['import_volume_usd', 'years_in_business', 'successful_imports', 'client_satisfaction_rating']
        if criteria not in valid_criteria:
            criteria = 'import_volume_usd' # Criterio por defecto si el dado no es válido
        
        def get_sort_key(importer):
            return getattr(importer, criteria, 0)

        sorted_mocked_importers = sorted(mocked_importers, key=get_sort_key, reverse=True)

        # Retornar los primeros 10 como diccionarios
        return [imp.to_dict() for imp in sorted_mocked_importers[:10]]

