from __future__ import annotations
from datetime import datetime, date
from pathlib import Path
import sys


# Ensure package imports work when running this file directly
try:
    from medical_cabinet.services import (
        PatientService,
        ConsultationService,
        PatientNotFoundError,
        ConsultationNotFoundError,
        InvalidSecurityNumberError,
        InvalidConsultationStatusError,
    )
    from medical_cabinet.models import Patient
except Exception:
    # Add project parent to path and retry
    base = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(base))
    from medical_cabinet.services import (
        PatientService,
        ConsultationService,
        PatientNotFoundError,
        ConsultationNotFoundError,
        InvalidSecurityNumberError,
        InvalidConsultationStatusError,
    )
    from medical_cabinet.models import Patient


def input_date(prompt: str) -> date:
    s = input(prompt + " (YYYY-MM-DD): ")
    return date.fromisoformat(s)


def main() -> None:
    ps = PatientService()
    cs = ConsultationService(patient_service=ps)

    while True:
        print("\n--- Cabinet médical ---")
        print("1) Ajouter patient")
        print("2) Lister patients")
        print("3) Planifier consultation")
        print("4) Lister consultations à venir")
        print("5) Marquer consultation réalisée")
        print("6) Annuler consultation")
        print("7) Ajouter diagnostic")
        print("8) Ajouter prescription (textuelle)")
        print("0) Quitter")
        choice = input("> ").strip()

        try:
            if choice == "1":
                num = input("Numéro de sécu (15 chiffres): ").strip()
                nom = input("Nom: ").strip()
                prenom = input("Prénom: ").strip()
                dob = input_date("Date de naissance")
                adresse = input("Adresse: ").strip()
                tel = input("Téléphone: ").strip()
                p = Patient(num_secu=num, nom=nom, prenom=prenom, date_naissance=dob, adresse=adresse, telephone=tel)
                ps.ajouter_patient(p)
                print("Patient ajouté.")

            elif choice == "2":
                for p in ps.lister_patients():
                    print(f"- {p.numero_secu} : {p.nom} {p.prenom} ({p.date_naissance.isoformat()})")

            elif choice == "3":
                num = input("Numéro de sécu du patient: ").strip()
                dt = input("Date et heure (YYYY-MM-DD HH:MM): ").strip()
                date_heure = datetime.fromisoformat(dt)
                med = input("Médecin: ").strip()
                motif = input("Motif: ").strip()
                c = cs.planifier_consultation(num, date_heure, med, motif)
                print(f"Consultation planifiée id={c['id']}")

            elif choice == "4":
                for c in cs.lister_consultations_a_venir():
                    print(f"- {c['id']} | {c['patient_num']} | {c['date_heure']} | {c['medecin']} | {c['motif']}")

            elif choice == "5":
                cid = input("ID consultation: ").strip()
                cs.marquer_realisee(cid)
                print("Marqué réalisée.")

            elif choice == "6":
                cid = input("ID consultation: ").strip()
                cs.annuler_consultation(cid)
                print("Consultation annulée.")

            elif choice == "7":
                cid = input("ID consultation: ").strip()
                diag = input("Diagnostic: ").strip()
                cs.ajouter_diagnostic(cid, diag)
                print("Diagnostic ajouté.")

            elif choice == "8":
                cid = input("ID consultation: ").strip()
                desc = input("Description prescription: ").strip()
                # créer une prescription simplifiée (dict) si models unavailable
                try:
                    from medical_cabinet.models import PrescriptionMedicamenteuse

                    presc = PrescriptionMedicamenteuse(description=desc, posologie="Selon prescripteur", duree="")
                    cs.ajouter_prescription(cid, presc)
                except Exception:
                    # fallback: ajouter dict
                    cs.ajouter_prescription(cid, type("P", (), {"description": desc}))
                print("Prescription ajoutée.")

            elif choice == "0":
                print("Au revoir")
                break

            else:
                print("Choix invalide")

        except (PatientNotFoundError, ConsultationNotFoundError) as e:
            print("Erreur:", e)
        except InvalidSecurityNumberError as e:
            print("Numéro de sécurité invalide:", e)
        except InvalidConsultationStatusError as e:
            print("Erreur statut consultation:", e)
        except Exception as e:
            print("Erreur inattendue:", type(e).__name__, e)


if __name__ == "__main__":
    main()
