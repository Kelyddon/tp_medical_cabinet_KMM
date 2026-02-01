"""Exceptions personnalisées partagées du projet."""
from __future__ import annotations


class PatientNotFoundError(Exception):
    """Patient introuvable."""


class ConsultationNotFoundError(Exception):
    """Consultation introuvable."""


class InvalidSecurityNumberError(Exception):
    """Numéro de sécurité sociale invalide."""


class InvalidConsultationStatusError(Exception):
    """Statut de consultation invalide pour l'opération demandée."""
