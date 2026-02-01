from functools import wraps
from datetime import datetime


# Exceptions personnalisées

class PatientNotFoundError(Exception):
    """Patient introuvable"""
    pass


class ConsultationNotFoundError(Exception):
    """Consultation introuvable"""
    pass

# Décorateurs

LOG_FILE = "logs.txt"


def log_action(description: str):
    """
    Enregistre une action dans le fichier logs.txt
    Format : [Date/Heure] Action effectuée : description
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            with open(LOG_FILE, "a", encoding="utf-8") as file:
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                file.write(f"[{timestamp}] Action effectuée : {description}\n")

            return result

        return wrapper

    return decorator


def validate_patient(func):
    """
    Vérifie qu'un patient existe avant d'exécuter une opération
    Le service doit contenir un dictionnaire self.patients
    """

    @wraps(func)
    def wrapper(self, patient_id, *args, **kwargs):
        if patient_id not in self.patients:
            raise PatientNotFoundError(
                f"Aucun patient trouvé avec le numéro : {patient_id}"
            )

        return func(self, patient_id, *args, **kwargs)

    return wrapper