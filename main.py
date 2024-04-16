from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pandas as pd
from openpyxl import Workbook

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://guiatic.com/co/directorio")
empresas_container = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "#__layout > div > main > section > div > div > div:nth-child(3) > div"))
)

enlaces_empresas = empresas_container.find_elements(By.TAG_NAME, 'a')
urls_empresas = [enlace.get_attribute('href') for enlace in enlaces_empresas if 'http' in enlace.get_attribute('href')]
informacion_empresas = {}

for url in urls_empresas:
    driver.get(url)

    linkedin_link = None

    try:
        linkedin_link = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#__layout > div > main > div > section.dm-section.g-bg-main.g-py-35 > div > div.row.align-items-end > div.col-7 > div > div > ul > li:nth-child(4) > a"))
        )
        linkedin_link = linkedin_link.get_attribute('href')
    except TimeoutException:
        print(f"No se encontró el enlace de LinkedIn para {url}")

    if not linkedin_link:
        try:
            sitio_web_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#__layout > div > main > div > section.dm-section.g-bg-main.g-py-35 > div > div.row.align-items-end > div.col-5.text-right > a"))
            )
            linkedin_link = sitio_web_btn.get_attribute('href')
        except TimeoutException:
            print(f"No se encontró el botón del sitio web para {url}")
    informacion_empresas[url] = linkedin_link or "No se encontró LinkedIn ni sitio web"
    time.sleep(2)

driver.quit()
lista_empresas = []
for empresa, info in informacion_empresas.items():
    nombre_empresa = empresa.split('/')[-1] if '/' in empresa else empresa
    empresa_info = {
        "Empresa": nombre_empresa,
        "LinkedIn": None,
        "Sitio Web": None
    }

    if info and 'linkedin' in info:
        empresa_info['LinkedIn'] = info
    elif info and not 'linkedin' in info:
        empresa_info['Sitio Web'] = info

    lista_empresas.append(empresa_info)

df_empresas = pd.DataFrame(lista_empresas)
df_empresas.to_excel('prueba.xlsx', engine='openpyxl', index=False)