"""
Module models.presciption
Contient la hiérarchie de prescriptions : classe abstraite `Prescription`
et classes dérivées spécifiques.

Remarque : le nom du fichier suit l'énoncé initial (orthographe "presciption").
On pourra renommer le fichier plus tard si nécessaire.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class Prescription(ABC):
	"""Classe abstraite représentant une prescription générique.

	Attributs communs :
	- description (médicament ou type de traitement)
	- posologie (str)
	- duree (str)

	Méthode abstraite : afficher_details()
	"""

	def __init__(self, description: str, posologie: str, duree: str) -> None:
		self.description = description
		self.posologie = posologie
		self.duree = duree

	@abstractmethod
	def afficher_details(self) -> str:
		"""Retourne une représentation textuelle détaillée de la prescription."""
		raise NotImplementedError()


class PrescriptionMedicamenteuse(Prescription):
	"""Prescription médicamentale (médicament, dosage, fréquence)."""

	def __init__(self, medicament: str, dosage: str, frequence: str, duree: str) -> None:
		super().__init__(description=medicament, posologie=dosage, duree=duree)
		self.frequence = frequence

	def afficher_details(self) -> str:
		return f"Médicament: {self.description}, dosage: {self.posologie}, fréquence: {self.frequence}, durée: {self.duree}"


class PrescriptionExamen(Prescription):
	"""Prescription pour un examen (radio, analyse, etc.)."""

	def __init__(self, type_examen: str, laboratoire: Optional[str] = None) -> None:
		super().__init__(description=type_examen, posologie="n/a", duree="n/a")
		self.laboratoire = laboratoire

	def afficher_details(self) -> str:
		lab = f", laboratoire: {self.laboratoire}" if self.laboratoire else ""
		return f"Examen: {self.description}{lab}"


class PrescriptionKinesitherapie(Prescription):
	"""Prescription de kinésithérapie (nombre de séances, zone à traiter)."""

	def __init__(self, nb_seances: int, zone: str) -> None:
		super().__init__(description="kinésithérapie", posologie=f"{nb_seances} séances", duree="par séances")
		self.nb_seances = nb_seances
		self.zone = zone

	def afficher_details(self) -> str:
		return f"Kinésithérapie: {self.nb_seances} séances, zone: {self.zone}"
