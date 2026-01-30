"""
Package models

Expose les classes principales pour l'import depuis `medical_cabinet.models`.
"""

# Importer les classes principales (stubs) pour faciliter les imports externes
from .patient import Patient
from .consultation import Consultation
from .presciption import (
	Prescription,
	PrescriptionMedicamenteuse,
	PrescriptionExamen,
	PrescriptionKinesitherapie,
)

__all__ = [
	"Patient",
	"Consultation",
	"Prescription",
	"PrescriptionMedicamenteuse",
	"PrescriptionExamen",
	"PrescriptionKinesitherapie",
]

