"""
Module models.patient
Contient la classe `Patient` et les méthodes de base.

Remarques sur la conception :
- Les attributs sensibles sont protégés par convention (préfixe `_`).
- La validation du numéro de sécurité sociale (15 chiffres) se fera via `utils.validators`
- La méthode `calculer_age` calcule l'âge à partir de la date de naissance.
"""
from __future__ import annotations
from datetime import date, datetime
from typing import List


class Patient:
	"""
	Représente un patient du cabinet.

	Attributs principaux (encapsulés) :
	- _num_secu : str -> numéro de sécurité sociale (15 chiffres)
	- _nom : str
	- _prenom : str
	- _date_naissance : date
	- _adresse : str
	- _telephone : str
	- _consultations : List -> liste d'objets `Consultation`

	Nota : la validation détaillée (format du numéro, etc.) est déléguée
	aux utilitaires de validation (module `utils.validators`).
	"""

	def __init__(
		self,
		num_secu: str,
		nom: str,
		prenom: str,
		date_naissance: date,
		adresse: str = "",
		telephone: str = "",
	) -> None:
		# attributs protégés
		self._num_secu = num_secu
		self._nom = nom
		self._prenom = prenom
		self._date_naissance = date_naissance
		self._adresse = adresse
		self._telephone = telephone
		self._consultations: List[object] = []  # type: ignore[assignment]

	# Propriétés pour l'accès contrôlé aux attributs
	@property
	def numero_secu(self) -> str:
		return self._num_secu

	@property
	def nom(self) -> str:
		return self._nom

	@property
	def prenom(self) -> str:
		return self._prenom

	@property
	def date_naissance(self) -> date:
		return self._date_naissance

	@property
	def adresse(self) -> str:
		return self._adresse

	@adresse.setter
	def adresse(self, value: str) -> None:
		self._adresse = value

	@property
	def telephone(self) -> str:
		return self._telephone

	@telephone.setter
	def telephone(self, value: str) -> None:
		self._telephone = value

	@property
	def consultations(self) -> List[object]:
		"""Retourne la liste des consultations (lecture seule)."""
		return list(self._consultations)

	def ajouter_consultation(self, consultation: object) -> None:
		"""Ajoute une consultation au dossier du patient.

		La logique (par ex. vérifier doublons) peut être ajoutée ici.
		"""
		self._consultations.append(consultation)

	def calculer_age(self, au_jour: date | None = None) -> int:
		"""Calcule l'âge du patient à la date fournie (ou aujourd'hui).

		Retourne un entier représentant les années complètes.
		"""
		today = au_jour or date.today()
		born = self._date_naissance
		age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
		return age

	def __repr__(self) -> str:
		return f"Patient({self._num_secu}, {self._nom} {self._prenom})"
