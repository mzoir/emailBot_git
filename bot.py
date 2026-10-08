import csv
import os
import time
import base64
import re
from datetime import datetime
from email.message import EmailMessage

import dns.resolver

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# ============================================================
# CONFIGURATION
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

CV_FILE = "Urcv.pdf"
COMPANIES_FILE = "companies.csv"
SENT_FILE = "sent.csv"

YOUR_NAME = ""
YOUR_PHONE = ""

YOUR_GITHUB = ""
YOUR_LINKEDIN = ""
YOUR_PORTFOLIO = ""

# Temps d'attente entre deux emails
DELAY_SECONDS = 10


# ============================================================
# CACHE DNS
# ============================================================

# Évite de refaire plusieurs fois la même recherche MX
# si plusieurs entreprises utilisent le même domaine.
MX_CACHE = {}


# ============================================================
# VÉRIFICATION EMAIL
# ============================================================

def verify_email(email):
    """
    Vérifie :
    1. Le format de l'adresse
    2. Le domaine
    3. La présence d'un enregistrement MX

    Retourne :
        valid   -> format correct + MX trouvé
        invalid -> format incorrect ou domaine inexistant
        unknown -> impossible de confirmer
    """

    email = email.strip().lower()

    # --------------------------------------------------------
    # Vérification du format
    # --------------------------------------------------------

    email_regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(email_regex, email):
        return "invalid"

    try:
        local, domain = email.rsplit("@", 1)
    except ValueError:
        return "invalid"

    if not local or not domain:
        return "invalid"

    domain = domain.strip().lower()

    # --------------------------------------------------------
    # Vérifier le cache
    # --------------------------------------------------------

    if domain in MX_CACHE:
        return MX_CACHE[domain]

    # --------------------------------------------------------
    # Vérification MX
    # --------------------------------------------------------

    try:

        mx_records = dns.resolver.resolve(
            domain,
            "MX",
            lifetime=5
        )

        if mx_records:
            MX_CACHE[domain] = "valid"
            return "valid"

        MX_CACHE[domain] = "invalid"
        return "invalid"

    except dns.resolver.NXDOMAIN:

        # Domaine inexistant
        MX_CACHE[domain] = "invalid"
        return "invalid"

    except (
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.exception.Timeout
    ):

        # Impossible de confirmer
        MX_CACHE[domain] = "unknown"
        return "unknown"

    except Exception as e:

        print(
            f"⚠️ Vérification impossible pour {email}: {e}"
        )

        MX_CACHE[domain] = "unknown"
        return "unknown"


# ============================================================
# AUTHENTIFICATION GMAIL
# ============================================================

def authenticate():

    creds = None

    # --------------------------------------------------------
    # Charger token.json
    # --------------------------------------------------------

    if os.path.exists("token.json"):

        try:

            creds = Credentials.from_authorized_user_file(
                "token.json",
                SCOPES
            )

        except Exception:

            print("⚠️ token.json invalide.")
            creds = None

    # --------------------------------------------------------
    # Vérifier credentials
    # --------------------------------------------------------

    if not creds or not creds.valid:

        # ----------------------------------------------------
        # Rafraîchir le token
        # ----------------------------------------------------

        if (
            creds
            and creds.expired
            and creds.refresh_token
        ):

            try:

                print("🔄 Rafraîchissement du token...")

                creds.refresh(Request())

            except Exception as e:

                print(
                    "⚠️ Impossible de rafraîchir le token."
                )

                print(e)

                creds = None

        # ----------------------------------------------------
        # Nouvelle authentification
        # ----------------------------------------------------

        if not creds or not creds.valid:

            print("🔐 Ouverture de Google OAuth...")

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )

            creds = flow.run_local_server(
                port=0
            )

        # ----------------------------------------------------
        # Sauvegarder token
        # ----------------------------------------------------

        with open(
            "token.json",
            "w",
            encoding="utf-8"
        ) as token:

            token.write(
                creds.to_json()
            )

    # --------------------------------------------------------
    # Gmail API
    # --------------------------------------------------------

    return build(
        "gmail",
        "v1",
        credentials=creds
    )


# ============================================================
# CHARGER LES EMAILS DÉJÀ ENVOYÉS
# ============================================================

def load_sent():

    sent = set()

    if not os.path.exists(SENT_FILE):
        return sent

    try:

        with open(
            SENT_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            reader = csv.DictReader(f)

            for row in reader:

                email = (
                    row.get("email", "")
                    .strip()
                    .lower()
                )

                status = (
                    row.get("status", "")
                    .strip()
                    .lower()
                )

                # Seulement les vrais envois réussis
                if email and status == "sent":

                    sent.add(email)

    except Exception as e:

        print(
            f"⚠️ Impossible de lire {SENT_FILE}: {e}"
        )

    return sent


# ============================================================
# ENREGISTRER UNE OPÉRATION
# ============================================================

def save_sent(
    company,
    email,
    status,
    message_id=""
):

    file_exists = os.path.exists(
        SENT_FILE
    )

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        SENT_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        # Créer l'en-tête si nécessaire
        if not file_exists:

            writer.writerow([
                "company",
                "email",
                "status",
                "message_id",
                "date"
            ])

        writer.writerow([
            company,
            email,
            status,
            message_id,
            now
        ])


# ============================================================
# CRÉER LE MESSAGE
# ============================================================

def create_message(
    company,
    recipient
):

    message = EmailMessage()

    # --------------------------------------------------------
    # Destinataire
    # --------------------------------------------------------

    message["To"] = recipient

    # --------------------------------------------------------
    # Objet
    # --------------------------------------------------------

    message["Subject"] = (
        "Candidature spontanée – "
        "AI Engineer / Full-Stack Developer"
    )

    # --------------------------------------------------------
    # Corps
    # --------------------------------------------------------

    body = f"""\
Madame, Monsieur,

Je vous adresse ma candidature spontanée pour une opportunité au sein de {company}, dans les domaines du développement logiciel, de l’intelligence artificielle et de la data.

Titulaire d’un ////, je dispose de compétences en développement Full-Stack, Machine Learning, IA générative, LLM/RAG et développement d’API. Je travaille notamment avec Python, Laravel, Vue.js, PostgreSQL et différentes technologies liées à l’intelligence artificielle.

Je suis à la recherche d’une opportunité en tant qu’AI Engineer, Machine Learning Engineer, Full-Stack Developer ou Software Engineer, et je serais ravi de pouvoir mettre mes compétences au service de vos projets.

Vous trouverez mon CV en pièce jointe. Je reste à votre disposition pour un entretien afin d’échanger davantage sur mon profil et les opportunités au sein de votre entreprise.

Cordialement,

{YOUR_NAME}
AI Engineer | Full-Stack Developer

Téléphone : {YOUR_PHONE}
GitHub : {YOUR_GITHUB}
LinkedIn : {YOUR_LINKEDIN}
Portfolio : {YOUR_PORTFOLIO}
"""

    message.set_content(body)

    # --------------------------------------------------------
    # Ajouter le CV
    # --------------------------------------------------------

    with open(
        CV_FILE,
        "rb"
    ) as f:

        cv_data = f.read()

    message.add_attachment(
        cv_data,
        maintype="application",
        subtype="pdf",
        filename=os.path.basename(
            CV_FILE
        )
    )

    # --------------------------------------------------------
    # Encodage Gmail
    # --------------------------------------------------------

    encoded_message = (
        base64.urlsafe_b64encode(
            message.as_bytes()
        )
        .decode()
    )

    return {
        "raw": encoded_message
    }


# ============================================================
# ENVOYER EMAIL
# ============================================================

def send_email(
    service,
    company,
    email
):

    message = create_message(
        company,
        email
    )

    result = (
        service.users()
        .messages()
        .send(
            userId="me",
            body=message
        )
        .execute()
    )

    return result


# ============================================================
# LIRE COMPANIES.CSV
# ============================================================

def load_companies():

    if not os.path.exists(
        COMPANIES_FILE
    ):

        print(
            f"❌ Fichier introuvable : "
            f"{COMPANIES_FILE}"
        )

        return []

    companies = []

    try:

        with open(
            COMPANIES_FILE,
            "r",
            encoding="utf-8-sig"
        ) as f:

            reader = csv.DictReader(f)

            # ------------------------------------------------
            # Vérifier les colonnes
            # ------------------------------------------------

            if (
                not reader.fieldnames
                or "company" not in reader.fieldnames
                or "email" not in reader.fieldnames
            ):

                print(
                    "❌ companies.csv doit contenir :"
                )

                print(
                    "company,email"
                )

                return []

            # ------------------------------------------------
            # Lire les entreprises
            # ------------------------------------------------

            for row in reader:

                company = (
                    row.get("company", "")
                    .strip()
                )

                email = (
                    row.get("email", "")
                    .strip()
                    .lower()
                )

                companies.append({
                    "company": company,
                    "email": email
                })

    except Exception as e:

        print(
            f"❌ Erreur lecture CSV : {e}"
        )

        return []

    return companies


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

def main():

    print()
    print("=" * 65)
    print("       BOT CANDIDATURES GMAIL")
    print("=" * 65)
    print()

    # ========================================================
    # VÉRIFIER LE CV
    # ========================================================

    if not os.path.exists(
        CV_FILE
    ):

        print(
            f"❌ CV introuvable : {CV_FILE}"
        )

        print(
            "Place ton CV dans le même dossier "
            "que bot.py."
        )

        return

    print(
        f"📄 CV : {CV_FILE}"
    )

    # ========================================================
    # CHARGER ENTREPRISES
    # ========================================================

    companies = load_companies()

    if not companies:

        print(
            "❌ Aucune entreprise trouvée."
        )

        return

    print(
        f"📋 Entreprises dans CSV : "
        f"{len(companies)}"
    )

    # ========================================================
    # CHARGER HISTORIQUE
    # ========================================================

    sent = load_sent()

    print(
        f"✅ Emails déjà envoyés : "
        f"{len(sent)}"
    )

    # ========================================================
    # AUTHENTIFICATION
    # ========================================================

    print()
    print("🔐 Connexion à Gmail...")

    try:

        service = authenticate()

    except Exception as e:

        print()
        print(
            "❌ Erreur authentification Gmail :"
        )

        print(e)

        return

    print(
        "✅ Gmail connecté."
    )

    print()

    # ========================================================
    # COMPTEURS
    # ========================================================

    total = len(companies)

    sent_count = 0
    skipped_count = 0
    error_count = 0
    empty_count = 0
    invalid_count = 0
    unknown_count = 0

    # ========================================================
    # TRAITEMENT
    # ========================================================

    for index, company_data in enumerate(
        companies,
        start=1
    ):

        company = company_data["company"]
        email = company_data["email"]

        print()
        print("=" * 65)

        print(
            f"[{index}/{total}] {company}"
        )

        print("=" * 65)

        # ====================================================
        # VÉRIFICATION DONNÉES
        # ====================================================

        if not company:

            print(
                "⚠️ Nom entreprise vide."
            )

            empty_count += 1

            continue

        if not email:

            print(
                f"⚠️ Email vide pour {company}."
            )

            empty_count += 1

            continue

        # ====================================================
        # VÉRIFICATION DÉJÀ ENVOYÉ
        # ====================================================

        if email in sent:

            print(
                "⏭️ DÉJÀ ENVOYÉ"
            )

            print(
                f"   📧 {email}"
            )

            skipped_count += 1

            continue

        # ====================================================
        # AFFICHER EMAIL
        # ====================================================

        print(
            f"📧 {email}"
        )

        print(
            "🟡 Statut : PAS ENCORE ENVOYÉ"
        )

        print()

        # ====================================================
        # VÉRIFICATION EMAIL
        # ====================================================

        print(
            "🔎 Vérification de l'adresse email..."
        )

        email_status = verify_email(
            email
        )

        print(
            f"   📊 Résultat : {email_status}"
        )

        # ====================================================
        # EMAIL INVALIDE
        # ====================================================

        if email_status == "invalid":

            print(
                "❌ Adresse email invalide "
                "ou domaine inexistant."
            )

            save_sent(
                company=company,
                email=email,
                status="invalid_email",
                message_id=""
            )

            invalid_count += 1

            continue

        # ====================================================
        # EMAIL UNKNOWN
        # ====================================================

        if email_status == "unknown":

            print(
                "⚠️ Impossible de confirmer "
                "le serveur mail."
            )

            print(
                "   → Envoi maintenu."
            )

            unknown_count += 1

        # ====================================================
        # EMAIL VALID
        # ====================================================

        if email_status == "valid":

            print(
                "✅ Domaine email valide "
                "avec serveur MX."
            )

        # ====================================================
        # ENVOI
        # ====================================================

        print()
        print(
            "📨 Envoi en cours..."
        )

        try:

            result = send_email(
                service,
                company,
                email
            )

            # ------------------------------------------------
            # ID Gmail
            # ------------------------------------------------

            message_id = result.get(
                "id",
                ""
            )

            # ------------------------------------------------
            # Sauvegarder succès
            # ------------------------------------------------

            save_sent(
                company=company,
                email=email,
                status="sent",
                message_id=message_id
            )

            sent.add(email)

            sent_count += 1

            print()
            print(
                "✅ EMAIL ENVOYÉ"
            )

            print(
                f"   🏢 {company}"
            )

            print(
                f"   📧 {email}"
            )

            print(
                f"   🆔 Message ID : {message_id}"
            )

            # ------------------------------------------------
            # Pause
            # ------------------------------------------------

            print()
            print(
                f"⏳ Attente {DELAY_SECONDS} secondes..."
            )

            time.sleep(
                DELAY_SECONDS
            )

        except Exception as e:

            # ------------------------------------------------
            # Erreur
            # ------------------------------------------------

            error_count += 1

            print()
            print(
                "❌ ERREUR ENVOI"
            )

            print(
                f"   🏢 {company}"
            )

            print(
                f"   📧 {email}"
            )

            print(
                f"   ⚠️ {e}"
            )

            save_sent(
                company=company,
                email=email,
                status="error",
                message_id=""
            )

            print()
            print(
                "🔄 Cet email pourra être "
                "réessayé au prochain lancement."
            )

    # ========================================================
    # RÉSUMÉ FINAL
    # ========================================================

    print()
    print()
    print("=" * 65)
    print("                    RÉSUMÉ")
    print("=" * 65)

    print(
        f"📋 Total CSV        : {total}"
    )

    print(
        f"📨 Envoyés          : {sent_count}"
    )

    print(
        f"⏭️ Déjà envoyés     : {skipped_count}"
    )

    print(
        f"❌ Erreurs           : {error_count}"
    )

    print(
        f"🚫 Emails invalides : {invalid_count}"
    )

    print(
        f"⚠️ Emails inconnus  : {unknown_count}"
    )

    print(
        f"⚠️ Données vides    : {empty_count}"
    )

    print("=" * 65)

    print(
        "🏁 Programme terminé."
    )

    print("=" * 65)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()