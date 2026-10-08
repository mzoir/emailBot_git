Steps for anyone to download and run the project
git clone https://github.com/mzoir/emailBot_git.git
cd emailBot_git


1. Install Python 3.
2. Install dependencies:
pip install -r requirements.txt


3. Create Google OAuth credentials and download credentials.json.
4. Place credentials.json in the project folder, using that exact filename.
5. Open bot.py and fill in your personal information and CV filename.
6. Create companies.csv with the company names and email addresses to contact.
7. Run the bot:
python bot.py


# emailBot_git
automation bot using gmail api
# 📧 Gmail Application Bot

> Automated tool for sending personalized spontaneous job applications through the Gmail API, with email validation, CV attachment, duplicate prevention, and sending history tracking.

## 🚀 Overview

**Gmail Application Bot** is a Python automation tool designed to simplify the process of sending spontaneous job applications to multiple companies.

The bot reads company information from a CSV file, validates email addresses using DNS/MX records, generates a personalized application email, attaches your CV, sends the email through the **Gmail API**, and records every operation in a history file.

### ✨ Main Features

- 📧 Send emails automatically through Gmail API
- 📎 Attach a CV automatically
- 🏢 Personalize the email with the company name
- 🔎 Validate email addresses
- 🌐 Check whether the recipient domain has an MX record
- 💾 Keep a complete sending history
- ⏭️ Skip companies already contacted successfully
- 🔄 Retry failed emails on future executions
- ⚡ DNS MX lookup cache
- 🛡️ OAuth 2.0 authentication with Google
- 📊 Display a detailed execution summary

---

## 🏗️ Project Structure

```text
gmail-application-bot/
│
├── bot.py
├── companies.csv
├── sent.csv
├── credentials.json
├── token.json
├── Urcv.pdf
├── .gitignore
└── README.md
```

### Files

| File | Description |
|---|---|
| `bot.py` | Main Python automation script |
| `companies.csv` | List of companies and recipient emails |
| `sent.csv` | Sending history generated automatically |
| `credentials.json` | Google OAuth credentials |
| `token.json` | OAuth access/refresh token generated after authentication |
| `Urcv.pdf` | CV attached to applications |
| `.gitignore` | Prevents sensitive files from being uploaded |
| `README.md` | Project documentation |

---

# ⚙️ Requirements

- Python 3.9+
- A Gmail account
- Google Cloud project
- Gmail API enabled
- OAuth 2.0 Desktop Application credentials
- Internet connection

### Python Dependencies

Install the required packages:

```bash
pip install google-api-python-client google-auth google-auth-oauthlib dnspython
```

Or create a `requirements.txt`:

```txt
google-api-python-client
google-auth
google-auth-oauthlib
dnspython
```

Then install:

```bash
pip install -r requirements.txt
```

---

# 🔐 Gmail API Configuration

The application uses Google's **Gmail API** with OAuth 2.0.

## 1. Create a Google Cloud Project

Go to:

https://console.cloud.google.com/

Create a new project.

## 2. Enable Gmail API

In Google Cloud Console:

```text
APIs & Services
      ↓
Library
      ↓
Gmail API
      ↓
Enable
```

## 3. Configure OAuth Consent Screen

Create an OAuth consent screen and configure the application.

For personal testing, you can use the application in testing mode.

## 4. Create OAuth Credentials

Go to:

```text
APIs & Services
      ↓
Credentials
      ↓
Create Credentials
      ↓
OAuth Client ID
```

Choose:

```text
Desktop application
```

Download the credentials file and rename it:

```text
credentials.json
```

Place it in the project root.

---

# 📂 Configure Your CV

Place your CV in the project directory.

The current configuration expects:

```text
Urcv.pdf
```

You can change the filename in `bot.py`:

```python
CV_FILE = "Urcv.pdf"
```

For example:

```python
CV_FILE = "mazoirzakariae_ia.pdf"
```

---

# 📝 Configure Personal Information

Update the following variables in `bot.py`:

```python
YOUR_NAME = "Your Name"
YOUR_PHONE = "+212XXXXXXXXX"

YOUR_GITHUB = "https://github.com/username"
YOUR_LINKEDIN = "https://www.linkedin.com/in/username/"
YOUR_PORTFOLIO = "https://yourportfolio.com/"
```

These values are automatically inserted into the application email.

---

# 🏢 Configure Companies

Create a `companies.csv` file.

The required columns are:

```csv
company,email
```

Example:

```csv
company,email
Company A,recruitment@company-a.com
Company B,hr@company-b.com
Company C,careers@company-c.com
```

You can add as many companies as needed.

---

# ✉️ Email Template

The bot automatically generates an email containing:

- Company name
- Candidate introduction
- Technical skills
- Desired positions
- CV attachment
- Contact information

The subject is:

```text
Candidature spontanée – AI Engineer / Full-Stack Developer
```

The email body can be customized directly inside:

```python
create_message()
```

---

# 🔎 Email Validation

Before sending an application, the bot checks the recipient address.

### Step 1 — Email format

The address must follow a basic structure:

```text
name@domain.com
```

### Step 2 — DNS/MX verification

The bot checks whether the domain has an MX record.

For example:

```text
company.com
     ↓
DNS lookup
     ↓
MX record found
     ↓
valid
```

The possible results are:

```text
valid
invalid
unknown
```

### Important

An MX record only confirms that the domain is configured to receive email.

It **does not guarantee that the specific email address exists**.

---

# 🧠 Duplicate Prevention

The bot maintains a history file:

```text
sent.csv
```

Example:

```csv
company,email,status,message_id,date
Company A,hr@company-a.com,sent,18c123abc,2026-10-08 10:30:21
Company B,contact@company-b.com,error,,2026-10-08 10:30:35
Company C,test@invalid.com,invalid_email,,2026-10-08 10:30:40
```

Only emails with:

```text
status = sent
```

are considered successfully sent.

Therefore, running the bot again will automatically skip companies that were already contacted successfully.

---

# 🔄 Retry Failed Emails

If an email fails:

```text
status = error
```

the address is **not** added to the successful sending list.

On the next execution, the bot can attempt to send it again.

This makes the process resilient to temporary Gmail/API/network errors.

---

# ⏱️ Delay Between Emails

The default delay is:

```python
DELAY_SECONDS = 10
```

This means the bot waits 10 seconds between successful emails.

You can change it:

```python
DELAY_SECONDS = 20
```

or:

```python
DELAY_SECONDS = 30
```

Use reasonable sending rates and comply with Gmail's current sending limits and Google's policies.

---

# ▶️ Running the Bot

After configuring the project:

```bash
python bot.py
```

The first execution will open the Google OAuth authentication flow.

After successful authentication, a:

```text
token.json
```

file will be created.

Future executions can reuse the saved credentials.

---

# 📊 Example Output

```text
=================================================================
       BOT CANDIDATURES GMAIL
=================================================================

📄 CV : Urcv.pdf
📋 Entreprises dans CSV : 40
✅ Emails déjà envoyés : 12

🔐 Connexion à Gmail...
✅ Gmail connecté.

=================================================================
[13/40] Example Company
=================================================================

📧 hr@example.com
🟡 Statut : PAS ENCORE ENVOYÉ

🔎 Vérification de l'adresse email...
   📊 Résultat : valid

✅ Domaine email valide avec serveur MX.

📨 Envoi en cours...

✅ EMAIL ENVOYÉ
   🏢 Example Company
   📧 hr@example.com
   🆔 Message ID : 18c123456789

⏳ Attente 10 secondes...
```

At the end:

```text
=================================================================
                    RÉSUMÉ
=================================================================
📋 Total CSV        : 40
📨 Envoyés          : 25
⏭️ Déjà envoyés     : 10
❌ Erreurs           : 2
🚫 Emails invalides : 2
⚠️ Emails inconnus  : 1
⚠️ Données vides    : 0
=================================================================
🏁 Programme terminé.
=================================================================
```

---

# 🔒 Security

**Never upload the following files to GitHub:**

```text
credentials.json
token.json
sent.csv
*.pdf
```

Add them to `.gitignore`:

```gitignore
# Google OAuth
credentials.json
token.json

# Sending history
sent.csv

# CV / personal documents
*.pdf

# Python
__pycache__/
*.pyc

# Environment
.env
```

### ⚠️ Important

`credentials.json` and especially `token.json` may contain sensitive authentication information.

Do not share them publicly.

---

# 🧩 How It Works

The application follows this workflow:

```text
             companies.csv
                   │
                   ▼
          Load company data
                   │
                   ▼
          Check sending history
                   │
          ┌────────┴────────┐
          │                 │
       Already sent       New email
          │                 │
          ▼                 ▼
        Skip          Validate email
                            │
                            ▼
                       DNS / MX check
                            │
                            ▼
                    Generate application
                            │
                            ▼
                       Attach CV
                            │
                            ▼
                       Gmail API
                            │
                            ▼
                    Send application
                            │
                            ▼
                     Save message ID
                            │
                            ▼
                       sent.csv
```

---

# 🛠️ Technologies

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Gmail API | Email delivery |
| Google OAuth 2.0 | Authentication |
| `dnspython` | DNS/MX verification |
| CSV | Company database and history |
| EmailMessage | Email construction |
| Base64 | Gmail API message encoding |

---

# 📌 Limitations

This project intentionally performs **basic email validation**.

DNS/MX validation can determine whether a domain is configured for email, but it cannot reliably determine whether:

```text
hr@company.com
```

actually exists.

The project also does not currently implement:

- Email open tracking
- Click tracking
- Bounce detection
- Automatic follow-ups
- Personalized content generated from company websites
- CRM integration
- Automatic job matching
- Advanced rate limiting
- Email verification through a dedicated verification service

---

# 🚀 Possible Improvements

Future versions could include:

### 🤖 AI Personalization

Generate a different introduction for every company using an LLM.

```text
Company information
        ↓
      LLM
        ↓
Personalized application
```

### 🔁 Follow-up Automation

Automatically send a follow-up after a configurable number of days.

### 📊 Application Dashboard

Track:

```text
Companies contacted
Applications sent
Errors
Follow-ups
Responses
Interviews
Rejected
```

### 🧠 Job Matching

Automatically analyze job descriptions and determine whether the position matches the candidate's skills.

### 🏢 Company Research

Automatically collect information about each company and adapt the application message accordingly.

---

# ⚠️ Responsible Usage

This tool is intended to automate legitimate job applications and professional outreach.

Use it responsibly:

- Contact relevant companies.
- Avoid sending excessive unsolicited messages.
- Respect Gmail sending limits.
- Respect company recruitment/contact preferences.
- Do not use the tool for spam.
- Keep personal data secure.

---

# 👨‍💻 Author

**Mazoir Zakariae**

AI Engineer | Full-Stack Developer

Specialized in:

```text
Python
Machine Learning
Generative AI
LLM / RAG
Laravel
Vue.js
PostgreSQL
API Development
Automation
```

---

# 📄 License

This project can be used and modified for personal and educational purposes.

If you publish a modified version, consider keeping attribution to the original project.

---

## ⭐ Project Goal

The goal of this project is to demonstrate how Python, Gmail API, DNS validation, OAuth 2.0 and automation can be combined to build a practical **job application automation system**.
