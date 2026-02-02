import os
import time
import smtplib
import mimetypes
import logging
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders



# Renseigne EMAIL_ADDRESS et EMAIL_PASSWORD dans les variables d'environnement avant d'exécuter.
# Renseigne Chemin CV et modifie ton texte a envoyer avant d'exécuter.

# --- CONFIGURATION ---
SMTP_SERVER = "smtp.gmail.com" #Exemple avec Gmail A MODIFIER
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")  # mettre en variable d'env (ou .env) OU remplacer os.environ.get("EMAIL_ADRESS") par ton adresse Mail
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # mettre en variable d'env (ou .env) OU remplacer os.environ.get("EMAIL_PASSWORD") par le mot de passe directement

# OPTIONS
DRY_RUN = False          # True = n'envoie rien, imprime seulement
DELAY_SECONDS = 1.0     # pause entre envois pour éviter throttling
LOG_LEVEL = logging.INFO

# Logging
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")


def build_message(from_addr, to_addr, subject, html_body, attachment_path=None):
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    if attachment_path:
        if not os.path.isfile(attachment_path):
            raise FileNotFoundError(f"Attachment not found: {attachment_path}")
        ctype, encoding = mimetypes.guess_type(attachment_path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(attachment_path, "rb") as f:
            part = MIMEBase(maintype, subtype)
            part.set_payload(f.read())
            encoders.encode_base64(part)
            filename = os.path.basename(attachment_path)
            part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
            msg.attach(part)
    return msg


def envoyer_email(destinataire, sujet, contenu_html, chemin_cv):
    if DRY_RUN:
        logging.info("[DRY RUN] Prépare à envoyer à %s sujet=%s pièce=%s", destinataire, sujet, chemin_cv)
        return True

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logging.error("EMAIL_ADDRESS ou EMAIL_PASSWORD non configurés dans les variables d'environnement.")
        return False

    try:
        msg = build_message(EMAIL_ADDRESS, destinataire, sujet, contenu_html, chemin_cv)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=60) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        logging.info("Email envoyé à %s", destinataire)
        return True
    except Exception as e:
        logging.exception("Erreur lors de l'envoi à %s: %s", destinataire, e)
        return False


def envoyer_emails_depuis_csv(fichier_csv, chemin_cv):
    envoies = 0
    erreurs = 0
    try:
        with open(fichier_csv, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=1):
                # Validation des champs attendus
                name = row.get("name", "").strip()
                surname = row.get("surname", "").strip()
                company = row.get("compagny", "").strip() or row.get("company", "").strip()
                email = row.get("email", "").strip()
                sector = row.get("sector", "").strip()
                location = row.get("location", "").strip()

                if not email:
                    logging.warning("Ligne %d: email vide, sautée.", row_idx)
                    erreurs += 1
                    continue

                # Regle pour envoie differents EMAILS selon location et sector
                if location == "London":
                    if sector == "Commodities":
                        if company.lower() == "jera":
                            sujet = "Opportunity"
                            contenu = (
                                f"Dear {surname or name},<br><br>"
                                "My name is Alexandre, and I have applied for the LNG Structured Trading Intern position at JERA Global Markets via your website. "
                                "As a top-performing graduate of ESCP's Master in Finance and ESME’s Master in Engineering, excelling in Python programming and commodities, "
                                "I believe my skills and background would be a valuable asset to JERA Global Markets. "
                                "My expertise in quantitative modeling, options pricing, and LNG market analysis, developed through projects at Kepler Cheuvreux and Moody’s, aligns with JERA’s innovative trading strategies.<br><br>"
                                "I am based in London and available for an interview immediately. You’ll find more details in my attached CV.<br><br>"
                                "Thank you for your time, and I remain at your disposal for any further information.<br><br>"
                                "Best regards,<br><br>"
                                "Alexandre"
                            )
                        else:
                            sujet = "Opportunity"
                            contenu = (
                                f"Dear {surname or name},<br><br>"
                                f"My name is Alexandre, and I am currently pursuing a Master’s in Finance at ESCP after completing an engineering degree in finance. "
                                f"I am passionate about the commodities sector and am currently writing a thesis on price anomalies in the commodities market using neural networks. I would love to contribute to your team at {company}, <strong>are you planning to recruit a junior or an intern in the near future?</strong><br><br>"
                                f"You’ll find more details in my attached CV.<br><br>"
                                f"I am currently in London and available to meet.<br><br>"
                                f"Best regards,<br>"
                                f"Alexandre"
                            )
                    elif sector == "HR":
                        sujet = "Commodities Internship or Junior Position"
                        contenu = (
                            f"Dear {surname or name},<br><br>"
                            "My name is Alexandre, and I am currently pursuing a Master’s in Finance at ESCP after completing an engineering degree in finance. "
                            f"I would love to contribute to your team at {company}, <strong>are you planning to recruit a junior or an intern in the near future?</strong><br><br>"
                            "You’ll find more details in my attached CV.<br><br>"
                            "Looking forward to hearing from you.<br><br>"
                            "Best regards,<br>"
                            "Alexandre"
                        )
                    elif sector == "Asset Management":
                        sujet = "Asset Management Internship or Junior Position"
                        contenu = (
                            f"Dear {surname or name},<br><br>"
                            "My name is Alexandre, and I am currently pursuing a Master’s in Finance at ESCP after completing an engineering degree in finance. "
                            "<strong>Are you planning to recruit a junior or an intern in the near future?</strong><br><br>"
                            "You’ll find more details in my attached CV.<br><br>"
                            "I am currently in London if you want to meet.<br><br>"
                            "Best regards,<br><br>"
                            "Alexandre"
                        )
                    else:
                        sujet = "Trader Internship or Junior Position"
                        contenu = (
                            f"Dear {surname or name},<br><br>"
                            "My name is Alexandre, and I am currently pursuing a Master’s in Finance at ESCP after completing an engineering degree in finance. "
                            "<strong>Are you planning to recruit a junior or an intern in the near future?</strong><br><br>"
                            "You’ll find more details in my attached CV.<br><br>"
                            "I am currently in London if you want to meet.<br><br>"
                            "Best regards,<br><br>"
                            "Alexandre"
                        )
                else:
                    if sector == "Commodities":
                        sujet = "Opportunity"
                        contenu = (
                            f"Dear {surname or name},<br><br>"
                            "My name is Alexandre, and I am currently pursuing a Master’s in Finance at ESCP after completing an engineering degree in finance. "
                            "I am passionate about the commodities sector and am currently writing a thesis on price anomalies in the commodities market using neural networks. I would love to contribute to your team, <strong>are you planning to recruit a junior or an intern in the near future?</strong><br><br>"
                            "You’ll find more details in my attached CV.<br><br>"
                            "Looking forward to hearing from you.<br><br>"
                            "Best regards,<br>"
                            "Alexandre"
                        )
                    elif sector == "HR":
                        sujet = "Commodities Internship or Junior Position"
                        contenu = (
                            f"Dear {surname or name},<br><br>"
                            "My name is Alexandre, and I am currently pursuing a Master’s in Finance at ESCP after completing an engineering degree in finance. "
                            "I would love to contribute to your team, <strong>are you planning to recruit a junior or an intern in the near future?</strong><br><br>"
                            "You’ll find more details in my attached CV.<br><br>"
                            "Looking forward to hearing from you.<br><br>"
                            "Best regards,<br>"
                            "Alexandre"
                        )
                    elif sector == "Asset Management":
                        sujet = "Asset Management Internship or Junior Position"
                        contenu = (
                            f"Dear {surname or name},<br><br>"
                            "My name is Alexandre, and I am currently pursuing a Master’s in Finance at ESCP after completing an engineering degree in finance. "
                            "<strong>Are you planning to recruit a junior or an intern in the near future?</strong><br><br>"
                            "You’ll find more details in my attached CV.<br><br>"
                            "Thank you for your time.<br><br>"
                            "Best regards,<br><br>"
                            "Alexandre"
                        )
                    else:
                        sujet = "Trader Internship or Junior Position"
                        contenu = (
                            f"Dear {surname or name},<br><br>"
                            "My name is Alexandre, and I am currently pursuing a Master’s in Finance at ESCP after completing an engineering degree in finance. "
                            "<strong>Are you planning to recruit a junior or an intern in the near future?</strong><br><br>"
                            "You’ll find more details in my attached CV.<br><br>"
                            "Best regards,<br><br>"
                            "Alexandre"
                        )

                success = envoyer_email(email, sujet, contenu, chemin_cv)
                if success:
                    envoies += 1
                else:
                    erreurs += 1

                time.sleep(DELAY_SECONDS)

    except FileNotFoundError:
        logging.error("Fichier CSV introuvable: %s", fichier_csv)
    except Exception:
        logging.exception("Erreur lors de la lecture du fichier CSV.")
    finally:
        logging.info("%d emails envoyés, %d erreurs", envoies, erreurs)
        return envoies, erreurs


if __name__ == "__main__":
    chemin_cv = "CV.pdf"
    fichier_contacts = "contacts.csv"

    envoyer_emails_depuis_csv(fichier_contacts)
