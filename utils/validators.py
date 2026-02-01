import re
from datetime import date
from __future__ import annotations
# Exceptions personnalisées

class InvalidSecurityNumberError(Exception):
    """Numéro de sécurité sociale invalide"""
    pass


class InvalidConsultationStatusError(Exception):
    """Statut de consultation invalide"""
    pass

# Fonctions de validation

def validate_security_number(security_number: str) -> None:
    """
    Vérifie que le numéro de sécurité sociale contient exactement 15 chiffres
    """
    if not re.fullmatch(r"\d{15}", security_number):
        raise InvalidSecurityNumberError(
            "Le numéro de sécurité sociale doit contenir exactement 15 chiffres."
        )


def calculate_age(birth_date: date) -> int:
    """
    Calcule l'âge du patient à partir de sa date de naissance
    """
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


class PatientNotFoundError(Exception):
    """Patient introuvable."""


class ConsultationNotFoundError(Exception):
    """Consultation introuvable."""


class InvalidSecurityNumberError(Exception):
    """Numéro de sécurité sociale invalide."""


class InvalidConsultationStatusError(Exception):
    """Statut de consultation invalide pour l'opération demandée."""