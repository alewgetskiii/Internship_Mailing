# Mailling — Guide de préparation et exécution (FR)

Ce README est conçu pour être exécuté **intégralement par un agent IA**. Il détaille toutes les étapes nécessaires avant de lancer le script.

## Pré‑requis

- Accès au terminal sur la machine.
- `conda` installé et disponible dans le PATH.
- Accès internet (LinkedIn + téléchargement des dépendances).

## 1) Installer l’environnement + Chromium

Depuis la racine du repo :

```bash
bash mailling/setup_env.sh
```

Cela crée/actualise l’environnement `mailling` et installe Chromium si possible (via le gestionnaire de paquets du système).

## 2) Activer l’environnement

```bash
conda activate mailling
```

## 3) Configurer les variables d’environnement (recommandé)

Ces variables sont lues automatiquement par `mailling/scrapper.py`.  
Tu peux les exporter dans le terminal **avant** d’exécuter le script :

```bash
export LINKEDIN_EMAIL="ton.email@domaine.com"
export LINKEDIN_PASSWORD="ton_mot_de_passe"
```

Notes :
- Si tu ne définis pas ces variables, le script utilise des valeurs par défaut définies en haut de des scriptes.

## 4) (Optionnel) Définir le chemin de Chrome/Chromedriver

En général Selenium gère tout seul.  
Si besoin, tu peux fixer explicitement :

```bash
export CHROME_BINARY="/usr/bin/chromium"
export CHROMEDRIVER_PATH="/usr/bin/chromedriver"
```

## 5) Lancer le script (scrapper LinkedIn)

```bash
python mailling/scrapper.py
```

Le CSV sera créé dans le dossier courant avec un nom du type :
`linkedin_profile_<COMPANY_NAME>_<JOB_TITLE>.csv`

## 6) Envoyer des emails (mail_sender)

Le script `mailling/mail_sender.py` lit un CSV de contacts et envoie un email personnalisé.

### 6.1 Préparer les variables d’environnement

```bash
export EMAIL_ADDRESS="ton.email@gmail.com"
export EMAIL_PASSWORD="ton_mot_de_passe_ou_app_password"
```

Si tu utilises Gmail, il faut souvent un **App Password** (mot de passe d’application) si la double authentification est activée.

### 6.2 Préparer les fichiers

- `contacts.csv` : doit être dans le même dossier d’exécution
- `CV.pdf` : pièce jointe, même dossier

Champs CSV attendus (minimaux) :
- `email`
- `name` / `surname`
- `company` (ou `compagny`)
- `sector`
- `location`

### 6.3 Lancer l’envoi

```bash
python mailling/mail_sender.py
```

## 7) (Optionnel) Utiliser un fichier `.env`

Le paquet `python-dotenv` est inclus dans l’environnement.  
Tu peux créer un fichier `.env` à la racine et le charger manuellement si tu le souhaites.

## Dépannage rapide

- Si `conda` est introuvable : installer Miniconda/Anaconda.
- Si Chromium n’a pas pu s’installer via `setup_env.sh`, l’installer manuellement via le gestionnaire de paquets.
- Si LinkedIn affiche un CAPTCHA, relancer plus tard ou passer en mode manuel.
- Si SMTP refuse la connexion : vérifier serveur, port, et mot de passe d’application.
## Dépannage rapide

- Si `conda` est introuvable : installer Miniconda/Anaconda.
- Si Chromium n’a pas pu s’installer via `setup_env.sh`, l’installer manuellement via le gestionnaire de paquets.
- Si LinkedIn affiche un CAPTCHA, relancer plus tard ou passer en mode manuel.
