"""
Services pour la gestion des consultations.

Fournit :
- `ConsultationService` pour planifier, lister, modifier, annuler,
  ajouter diagnostics et prescriptions.

Ce module travaille avec `PatientService` et sérialise les consultations
dans `data/cabinet_data.json` (même structure que PatientService).
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
from pathlib import Path
import uuid

from medical_cabinet.models import Consultation, Prescription
from medical_cabinet.services.patient_service import PatientService, PatientNotFoundError

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "cabinet_data.json"
LOG_FILE = BASE_DIR / "logs.txt"


class ConsultationNotFoundError(Exception):
	pass


class InvalidConsultationStatusError(Exception):
	pass


try:
	from medical_cabinet.utils.decorators import log_action as _imported_log_action  # type: ignore
except Exception:
	def log_action(func):
		def wrapper(*args, **kwargs):
			res = func(*args, **kwargs)
			try:
				with open(LOG_FILE, "a", encoding="utf-8") as f:
					from datetime import datetime

					f.write(f"[{datetime.now().isoformat()}] Action effectuée: {func.__name__}\n")
			except Exception:
				pass
			return res

		return wrapper
else:
	def log_action(*d_args, **d_kwargs):
		def _decorator(fn):
			try:
				return _imported_log_action(*d_args, **d_kwargs)(fn)
			except TypeError:
				try:
					return _imported_log_action(fn)
				except Exception:
					return fn

		if len(d_args) == 1 and callable(d_args[0]) and not d_kwargs:
			return _decorator(d_args[0])
		return _decorator


class ConsultationService:
	"""Service gérant les consultations.

	- stocke en mémoire `consultations` : liste de dicts sérialisés contenant un `id` unique
	- fournit des méthodes pour manipuler ces consultations et sauvegarder l'état
	"""

	def __init__(self, patient_service: Optional[PatientService] = None) -> None:
		self.patient_service = patient_service or PatientService()
		self.consultations: List[Dict[str, Any]] = []
		self._load()

	def _load(self) -> None:
		if not DATA_FILE.exists():
			return
		try:
			with open(DATA_FILE, "r", encoding="utf-8") as f:
				data = json.load(f) or {}
		except Exception:
			data = {}
		self.consultations = data.get("consultations", [])

	def _save(self) -> None:
		# demander au patient_service d'écrire patients et nous fournir les consultations sérialisées
		consultations_serialized = self.consultations
		self.patient_service._save(consultations_serialized=consultations_serialized)

	def _serialize_prescription(self, presc: Prescription) -> Dict[str, Any]:
		# très simple : enregistrer la classe et ses attributs publics
		return {"_type": presc.__class__.__name__, "description": getattr(presc, "description", ""), "posologie": getattr(presc, "posologie", ""), "duree": getattr(presc, "duree", "")}

	def _deserialize_prescription(self, data: Dict[str, Any]) -> Dict[str, Any]:
		# on retourne le dict brut ; reconstruction complète peut être faite plus tard
		return data

	@log_action
	def planifier_consultation(self, patient_num: str, date_heure: datetime, medecin: str, motif: str) -> Dict[str, Any]:
		# vérifier patient
		try:
			patient = self.patient_service.rechercher_patient(patient_num)
		except PatientNotFoundError:
			raise

		cid = str(uuid.uuid4())
		c = {
			"id": cid,
			"patient_num": patient_num,
			"date_heure": date_heure.isoformat(),
			"medecin": medecin,
			"motif": motif,
			"diagnostic": None,
			"prescriptions": [],
			"statut": Consultation.STATUS_PLANIFIEE if hasattr(Consultation, "STATUS_PLANIFIEE") else "planifiée",
		}
		self.consultations.append(c)
		# ajouter à l'objet patient en mémoire si possible
		try:
			patient.ajouter_consultation(c)
		except Exception:
			pass
		self._save()
		return c

	def lister_consultations_a_venir(self) -> List[Dict[str, Any]]:
		now = datetime.now()
		upcoming = [c for c in self.consultations if c.get("statut") in ("planifiée", "planifiee") and datetime.fromisoformat(c["date_heure"]) >= now]
		return sorted(upcoming, key=lambda x: x["date_heure"])

	def _find_by_id(self, consultation_id: str) -> Dict[str, Any]:
		for c in self.consultations:
			if c.get("id") == consultation_id:
				return c
		raise ConsultationNotFoundError(f"Consultation {consultation_id} introuvable")

	@log_action
	def marquer_realisee(self, consultation_id: str) -> None:
		c = self._find_by_id(consultation_id)
		if c.get("statut") == Consultation.STATUS_ANNULEE if hasattr(Consultation, "STATUS_ANNULEE") else "annulée":
			raise InvalidConsultationStatusError("Impossible de réaliser une consultation annulée")
		c["statut"] = Consultation.STATUS_REALISEE if hasattr(Consultation, "STATUS_REALISEE") else "réalisée"
		self._save()

	@log_action
	def annuler_consultation(self, consultation_id: str) -> None:
		c = self._find_by_id(consultation_id)
		if c.get("statut") == (Consultation.STATUS_REALISEE if hasattr(Consultation, "STATUS_REALISEE") else "réalisée"):
			raise InvalidConsultationStatusError("Impossible d'annuler une consultation déjà réalisée")
		c["statut"] = Consultation.STATUS_ANNULEE if hasattr(Consultation, "STATUS_ANNULEE") else "annulée"
		self._save()

	@log_action
	def ajouter_diagnostic(self, consultation_id: str, diagnostic: str) -> None:
		c = self._find_by_id(consultation_id)
		if c.get("statut") != (Consultation.STATUS_REALISEE if hasattr(Consultation, "STATUS_REALISEE") else "réalisée"):
			raise InvalidConsultationStatusError("Le diagnostic ne peut être ajouté que si la consultation est réalisée")
		c["diagnostic"] = diagnostic
		self._save()

	@log_action
	def ajouter_prescription(self, consultation_id: str, prescription: Prescription) -> None:
		c = self._find_by_id(consultation_id)
		c_presc = self._serialize_prescription(prescription)
		c["prescriptions"].append(c_presc)
		self._save()

