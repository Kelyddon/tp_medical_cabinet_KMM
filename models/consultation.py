"""
Module models.consultation
Contient la classe `Consultation`.

Contrainte importantes (implémenter dans la suite) :
- Une consultation ne peut être modifiée que si son statut le permet.
- Le diagnostic ne peut être ajouté que si la consultation est réalisée.
"""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional


class Consultation:
	"""
	Représente une consultation (rendez-vous).

	Attributs :
	- date_heure : datetime
	- patient : Patient (référence)
	- medecin : str
	- motif : str
	- diagnostic : Optional[str]
	- prescriptions : List[Prescription]
	- statut : str (valeurs : 'planifiée', 'réalisée', 'annulée')

	Méthodes principales à implémenter :
	- modifier_consultation
	- marquer_realisee
	- annuler
	- ajouter_diagnostic (seulement si réalisée)
	- ajouter_prescription
	"""

	STATUS_PLANIFIEE = "planifiée"
	STATUS_REALISEE = "réalisée"
	STATUS_ANNULEE = "annulée"

	def __init__(
		self,
		date_heure: datetime,
		patient: object,
		medecin: str,
		motif: str,
	) -> None:
		self.date_heure = date_heure
		self.patient = patient
		self.medecin = medecin
		self.motif = motif
		self.diagnostic: Optional[str] = None
		self.prescriptions: List[object] = []  # type: ignore[assignment]
		self.statut: str = Consultation.STATUS_PLANIFIEE

	def peut_modifier(self) -> bool:
		"""Retourne True si la consultation peut être modifiée selon son statut."""
		return self.statut == Consultation.STATUS_PLANIFIEE

	def modifier_consultation(self, **changes) -> None:
		"""Modifie la consultation lorsque le statut le permet.

		Exemple d'utilisation : modifier_consultation(motif='nouveau motif')
		"""
		if not self.peut_modifier():
			raise RuntimeError("Consultation ne peut être modifiée dans cet état")
		for k, v in changes.items():
			if hasattr(self, k):
				setattr(self, k, v)

	def marquer_realisee(self) -> None:
		"""Marque la consultation comme réalisée."""
		self.statut = Consultation.STATUS_REALISEE

	def annuler(self) -> None:
		"""Annule la consultation."""
		self.statut = Consultation.STATUS_ANNULEE

	def ajouter_diagnostic(self, diagnostic: str) -> None:
		"""Ajoute un diagnostic uniquement si la consultation est réalisée."""
		if self.statut != Consultation.STATUS_REALISEE:
			raise RuntimeError("Le diagnostic ne peut être ajouté que si la consultation est réalisée")
		self.diagnostic = diagnostic

	def ajouter_prescription(self, prescription: object) -> None:
		"""Ajoute une prescription à la consultation (n'importe quel type dérivé de Prescription)."""
		self.prescriptions.append(prescription)

	def __repr__(self) -> str:
		return f"Consultation({self.date_heure!r}, {self.patient!r}, {self.medecin})"
