"""
Services pour la gestion des patients.

Ce module fournit :
- `PatientService` : CRUD minimal sur les patients + persistance JSON
- Exceptions personnalisées utilisées par les services

Remarque : Le module tente d'utiliser les décorateurs de `utils.decorators`.
S'ils sont absents, des décorateurs no-op ou équivalents sont définis localement
pour assurer le fonctionnement sans modifier le dossier `utils`.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import date
import uuid

from medical_cabinet.models import Patient

# Chemin des données
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "cabinet_data.json"
LOG_FILE = BASE_DIR / "logs.txt"


# Exceptions personnalisées
class PatientNotFoundError(Exception):
	pass


class InvalidSecurityNumberError(Exception):
	pass


# Tentative d'import des décorateurs depuis utils; sinon fallback.
# Wrap imported `log_action` into `log_action` name that supports both forms:
#   @log_action  and @log_action("desc")
try:
	from medical_cabinet.utils.decorators import log_action as _imported_log_action, validate_patient  # type: ignore
except Exception:
	def log_action(func):
		def wrapper(*args, **kwargs):
			try:
				res = func(*args, **kwargs)
				with open(LOG_FILE, "a", encoding="utf-8") as f:
					from datetime import datetime

					f.write(f"[{datetime.now().isoformat()}] Action effectuée: {func.__name__}\n")
				return res
			except Exception:
				raise

		return wrapper
	def validate_patient(func):
		return func
else:
	# Adapter to accept either decorator usage style
	def log_action(*d_args, **d_kwargs):
		def _decorator(fn):
			try:
				# try factory style: log_action("desc")(fn)
				return _imported_log_action(*d_args, **d_kwargs)(fn)
			except TypeError:
				try:
					# try direct decorator style: log_action(fn)
					return _imported_log_action(fn)
				except Exception:
					return fn

		# used as @log_action without args
		if len(d_args) == 1 and callable(d_args[0]) and not d_kwargs:
			return _decorator(d_args[0])
		return _decorator


class PatientService:
	"""Service pour gérer les patients et la persistance.

	- stocke en mémoire un dict `patients` indexé par numéro de sécurité
	- lit/écrit `DATA_FILE` au format JSON
	"""

	def __init__(self) -> None:
		self.patients: Dict[str, Patient] = {}
		self._load()

	def _load(self) -> None:
		if not DATA_FILE.exists():
			self._dump_empty()
			return
		try:
			with open(DATA_FILE, "r", encoding="utf-8") as f:
				data = json.load(f) or {}
		except Exception:
			data = {}

		patients = data.get("patients", [])
		for p in patients:
			# reconstruction minimale : date_naissance attendu en ISO YYYY-MM-DD
			dob = date.fromisoformat(p["date_naissance"]) if p.get("date_naissance") else date.today()
			patient = Patient(
				num_secu=p["numero_secu"],
				nom=p.get("nom", ""),
				prenom=p.get("prenom", ""),
				date_naissance=dob,
				adresse=p.get("adresse", ""),
				telephone=p.get("telephone", ""),
			)
			self.patients[patient.numero_secu] = patient

	def _dump_empty(self) -> None:
		DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
		with open(DATA_FILE, "w", encoding="utf-8") as f:
			json.dump({"patients": [], "consultations": []}, f, ensure_ascii=False, indent=2)

	def _save(self, consultations_serialized: Optional[List[dict]] = None) -> None:
		# Sauvegarde patients + éventuellement consultations passées en param
		patients_list = [
			{
				"numero_secu": p.numero_secu,
				"nom": p.nom,
				"prenom": p.prenom,
				"date_naissance": p.date_naissance.isoformat(),
				"adresse": p.adresse,
				"telephone": p.telephone,
			}
			for p in self.patients.values()
		]
		# charger existant puis mettre à jour
		obj = {"patients": patients_list}
		if consultations_serialized is not None:
			obj["consultations"] = consultations_serialized
		else:
			# préserver consultations si existant
			try:
				with open(DATA_FILE, "r", encoding="utf-8") as f:
					existing = json.load(f) or {}
			except Exception:
				existing = {}
			obj["consultations"] = existing.get("consultations", [])

		with open(DATA_FILE, "w", encoding="utf-8") as f:
			json.dump(obj, f, ensure_ascii=False, indent=2)

	@log_action
	def ajouter_patient(self, patient: Patient) -> None:
		"""Ajoute un nouveau patient après validation du numéro de sécurité.

		Lève `InvalidSecurityNumberError` si le numéro n'a pas 15 chiffres.
		"""
		num = patient.numero_secu
		if not (isinstance(num, str) and num.isdigit() and len(num) == 15):
			raise InvalidSecurityNumberError("Le numéro de sécurité sociale doit contenir 15 chiffres")
		if num in self.patients:
			# on écrase volontairement
			self.patients[num] = patient
		else:
			self.patients[num] = patient
		self._save()

	def rechercher_patient(self, numero_secu: str) -> Patient:
		"""Recherche un patient par son numéro de sécurité sociale.

		Lève `PatientNotFoundError` si absent.
		"""
		patient = self.patients.get(numero_secu)
		if not patient:
			raise PatientNotFoundError(f"Patient {numero_secu} introuvable")
		return patient

	def lister_patients(self) -> List[Patient]:
		return list(self.patients.values())

	def historique_patient(self, numero_secu: str, consultations: List[dict]) -> List[dict]:
		"""Retourne l'historique des consultations pour un patient.

		`consultations` est la liste sérialisée lue depuis le fichier JSON.
		"""
		if numero_secu not in self.patients:
			raise PatientNotFoundError(f"Patient {numero_secu} introuvable")
		hist = [c for c in consultations if c.get("patient_num") == numero_secu]
		return hist

