# backend/models/importer.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import uuid

@dataclass
class Importer:
    """
    Representa una empresa importadora de productos.
    """
    company_name: str
    ruc: str # Número de identificación fiscal (ej. RUC en Perú/Ecuador, CUIT en Argentina)
    country_of_origin: str # País principal de los productos que importa
    contact_email: str
    contact_phone: str
    fiscal_address: str # Dirección fiscal completa
    registration_date: str # Formato ISO 8601, ej. "YYYY-MM-DD"
    
    # Mover los campos con valores por defecto al final
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    specialty_products: List[str] = field(default_factory=list) # Ej. ["electronics", "clothing"]


    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto Importer a un diccionario para almacenamiento."""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "ruc": self.ruc,
            "country_of_origin": self.country_of_origin,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "fiscal_address": self.fiscal_address,
            "specialty_products": self.specialty_products,
            "registration_date": self.registration_date,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        """Crea un objeto Importer desde un diccionario."""
        return Importer(
            company_name=data["company_name"],
            ruc=data["ruc"],
            country_of_origin=data["country_of_origin"],
            contact_email=data["contact_email"],
            contact_phone=data["contact_phone"],
            fiscal_address=data["fiscal_address"],
            registration_date=data["registration_date"],
            # Los campos con valor por defecto se pueden omitir o pasar si están presentes
            id=data.get("id", str(uuid.uuid4())), 
            specialty_products=data.get("specialty_products", []),
        )
