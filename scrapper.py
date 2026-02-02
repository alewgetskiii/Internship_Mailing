import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import time
import csv
from bs4 import BeautifulSoup
import re
from collections import OrderedDict

# === Configuration rapide ===
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "alexandre-gerard@live.fr")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
COMPANY_NAME = os.getenv("LINKEDIN_COMPANY_NAME", "Touton")
COMPANY_ID = os.getenv("LINKEDIN_COMPANY_ID", "9183372")
JOB_TITLES = [t.strip() for t in os.getenv("LINKEDIN_JOB_TITLES", "Trader").split(",") if t.strip()]

# Configuration initiale
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    chrome_binary = os.getenv("CHROME_BINARY")
    if chrome_binary:
        chrome_options.binary_location = chrome_binary

    driver_path = os.getenv("CHROMEDRIVER_PATH")
    if driver_path:
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    return driver

# Connexion à LinkedIn
def linkedin_login(driver, email, password):
    print("Tentative de connexion à LinkedIn...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)  # Attendre la fin de la connexion
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav")))
        print("Connexion réussie.")
        return True
    except TimeoutException:
        print("Erreur : Échec de la connexion (timeout ou CAPTCHA). Vérifiez le navigateur.")
        return False

# Recherche de profils
def search_profiles(driver, company, job_title, compagny_id):
    print(f"Lancement de la recherche pour '{job_title}' chez '{company}'...")
    driver.get("https://www.linkedin.com/search/results/people/?currentCompany=%5B%"+compagny_id+"%5D&keywords="+job_title+"&origin=FACETED_SEARCH&page=1")  # Aller à la page d'accueil d'abord
    time.sleep(3)
    return driver
    

def extract_profile_data(driver, url, company):
    print(f"Extraction des données pour {url}...")
    if "?miniProfileUrn=" in url:
        url = url.split("?")[0]
    driver.get(url)
    
    # Attendre que les données soient chargées
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
    except TimeoutException:
        print(f"Erreur : Le nom ne s'est pas chargé pour {url}")
        return None

    # Analyser la page avec BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print("le nom est chargé")
    
    try:
        # Extraire le nom (en supposant qu'il est toujours dans un h1)
        full_name = soup.find("h1").text.strip()
        name_parts = full_name.split(",")[0].split(" ", 1)  # Suppression des suffixes comme "CFA"
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
    except Exception as e:
        print(f"Erreur lors de l'extraction du nom : {e}")
        first_name, last_name = "", ""

    try:
        location = soup.find("span", class_="text-body-small inline t-black--light break-words").text.strip()
    except:
        location = ""

    try:
        bio = soup.find("div", class_="text-body-medium").text.strip()
    except:
        bio = ""

    data = {
        "Prénom": first_name,
        "Nom": last_name,
        "Entreprise": company,
        "Bio": bio,
        "sector": "Commodities",
        "email":"",
        "Lieu": location,
        "Lien LinkedIn": url
    }
    print(f"Données extraites : {data['Prénom']} {data['Nom']}")
    return data

# Fonction principale
def main():

    # ID LinkedIn de l'entreprise se trouve dans l'url de recherche de personnes travaillant dans l'entreprise
    # ex : https://www.linkedin.com/search/results/people/?keywords=trader&origin=FACETED_SEARCH&currentCompany=%5B%229183372%22%5D -> 9183372
    csv_name = f"linkedin_profile_{COMPANY_NAME}_{JOB_TITLES[0]}.csv"
    
    driver = setup_driver()
    
    if not linkedin_login(driver, LINKEDIN_EMAIL, LINKEDIN_PASSWORD):
        print("Arrêt du programme suite à l'échec de la connexion.")
        driver.quit()
        return
    

    with open(csv_name, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ["Prénom", "Nom", "Entreprise", "Bio","sector","email", "Lieu", "Lien LinkedIn"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for role in JOB_TITLES:
            driver = search_profiles(driver, COMPANY_NAME, role, COMPANY_ID)
            if driver is None:
                print("Arrêt du programme : échec de la recherche.")
                driver.quit() if 'driver' in locals() else None
                return
        
            page_count = 1
            max_pages = 25
            visited_profiles = set()

            while page_count < max_pages:
                print(f"Traitement de la page {page_count}...")
                nb_profile_scrapped = 0

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  

                soup = BeautifulSoup(driver.page_source, 'html.parser')
                profiles = soup.find_all("a", href=re.compile(r"^https://www.linkedin.com/in/"))


                profiles_to_scrape = list(OrderedDict.fromkeys(
                    profile.get("href") for profile in profiles
                    if "linkedin.com/in/" in profile.get("href", "") and not profile.get("href", "").endswith("/overlay")
                ))[:40]
            
                if not profiles_to_scrape:
                    print("Aucun profil trouvé sur cette page.")
                    break
                
                nb_profile = len(profiles_to_scrape)
                print("nombre profile page" + str(page_count) + " : " + str(nb_profile))

                for href in profiles_to_scrape:
                    if href in visited_profiles:
                        print(f"Profil déjà traité : {href}")
                        continue
                    visited_profiles.add(href)

                    try:
                        # Extraire les données du profil
                        profile_data = extract_profile_data(driver, href, COMPANY_NAME)
                        writer.writerow(profile_data)
                        nb_profile_scrapped += 1
                        time.sleep(1)
                    except Exception as e:
                        print(f"Erreur sur profil {href} : {e}")
                        continue
                
                print("page "+ str(page_count)+" scrappé : "+str(nb_profile_scrapped)+" / "+str(nb_profile))
                page_count += 1
                time.sleep(2)
                driver.get("https://www.linkedin.com/search/results/people/?currentCompany=%5B%"+COMPANY_ID+"%5D&keywords="+role+"&origin=FACETED_SEARCH&page="+str(page_count))
                time.sleep(2)

    print("Scrapping terminé.")
    driver.quit()



if __name__ == "__main__":
    main()
