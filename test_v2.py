import pandas as pd
import numpy as np
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import sys
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import unicodedata

def initialize_browser():
    options = uc.ChromeOptions()
    # Configuraciones para reducir el uso de caché y correr en modo incógnito
    options.add_argument("--disable-cache")  # Deshabilita la caché del navegador
    options.add_argument("--disable-application-cache")  # Deshabilita la caché de la aplicación
    options.add_argument("--no-sandbox")  # Deshabilita el modo sandbox para operaciones sin privilegios
    options.add_argument("--incognito")  # Usa el modo incógnito
    options.add_argument("--headless")  # Ejecuta el navegador en modo sin cabeza para no mostrar la UI
    options.add_argument("--disable-gpu")  # Deshabilita la GPU para reducir el uso de recursos
    options.add_argument("--disk-cache-size=1")  # Establece el tamaño máximo de la caché del disco a 1 byte
    browser = uc.Chrome(options=options)
    return browser

def calculate_stats(values):
    if not values:
        return None, None, None
    valid_values = [v for v in values if v is not None]
    if not valid_values:
        return None, None, None
    return round(min(valid_values), 1), round(max(valid_values), 1), round(np.mean(valid_values), 1)

def extract_time_distance(details):
    results = re.findall(r"(\d+)\s+mins\s+-\s+(\d+)\s+metros", details)
    return [(int(t), int(d)) for t, d in results] if results else []

def normalize_string(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    no_accents_str = ''.join([char for char in normalized_str if unicodedata.category(char) != 'Mn'])
    return no_accents_str.lower()

filename = sys.argv[1] if len(sys.argv) > 1 else 'urlsPropiedadesUsadas.txt'
with open(f"Data/{filename}", 'r') as file:
    urls = [line.strip() for line in file]

all_data = []
browser = initialize_browser()

# Navega a la página de valor de la UF
browser.get("https://valoruf.cl")
ufpesor = browser.find_element(By.ID, "ufpesor").text.replace(".", "").replace(",", ".")
valor_uf = float(ufpesor)

reset_interval = 50  # Número de URLs antes de reiniciar el navegador
urls_total = len(urls)

for index, url in enumerate(urls):
    
    
    try:
        browser.get(url)
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "footer")))
        html = browser.page_source
        soup = BeautifulSoup(html, "lxml")

        print(f"Procesando URL {index} de {urls_total}: {url}")

        try:
            cookie_button = WebDriverWait(browser, 2).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="newCookieDisclaimerButton"]')))
            cookie_button.click()
        except TimeoutException:
            print("El botón de cookies no fue necesario o no se pudo hacer clic en él.")

        # Extraer dirección
        direccion_container = soup.select_one(".ui-vip-location__subtitle .ui-pdp-media__title")
        direccion = direccion_container.get_text(strip=True) if direccion_container else None

        # Extraer precio en UF
        price_container = soup.find("div", class_="ui-pdp-price__second-line") 
        price = 0
        if price_container:
            price_span = price_container.find("span", class_="andes-money-amount__fraction") 
            price_type = price_container.find("span", class_="andes-money-amount__currency-symbol") 
            if price_span and price_type:
                price = price_span.get_text(strip=True).replace(".", "")
                price_type = price_type.get_text(strip=True)
                if price_type == "$":
                    price = float(price) / valor_uf
                    price = int(price)

        # Extraer información de la propiedad
        specs_container = soup.find(id="highlighted_specs_res")
        specs_data = {'metros_cuadrados': 0, 'dormitorios': 0, 'banios': 0}
        if specs_container:
            spec_elements = specs_container.select(".ui-pdp-highlighted-specs-res__icon-label")
            for spec in spec_elements:
                label = spec.select_one(".ui-pdp-label").text if spec.select_one(".ui-pdp-label") else ""
                numbers = re.findall(r"\d+\.?\d*", label)
                if 'm²' in label:
                    specs_data['metros_cuadrados'] = int(float(numbers[0])) if numbers else 0
                elif 'dormitorio' in label:
                    specs_data['dormitorios'] = int(float(numbers[0])) if numbers else 0
                elif 'baño' in label:
                    specs_data['banios'] = int(float(numbers[0])) if numbers else 0
        
        category_data = {}
        tab_buttons = browser.find_elements(By.CSS_SELECTOR, ".andes-tabs__container button")
        for button in tab_buttons:
            WebDriverWait(browser, 3).until(EC.element_to_be_clickable(button)).click()
            time.sleep(1)  # Permitir que se cargue el contenido

            tab_content_html = browser.page_source
            tab_soup = BeautifulSoup(tab_content_html, 'lxml')
            current_tab = tab_soup.find("div", {"aria-labelledby": button.get_attribute('id')})
            if current_tab:
                sections = current_tab.find_all("div", class_="ui-vip-poi__subsection")
                for section in sections:
                    section_title = normalize_string(section.find("span", class_="ui-vip-poi__subsection-title").get_text(strip=True).replace(" ", "_"))
                    items = section.find_all("div", class_="ui-vip-poi__item")
                    times_distances = [extract_time_distance(item.find("span", class_="ui-pdp-color--GRAY").get_text(strip=True)) for item in items]
                    times, distances = zip(*[td for sublist in times_distances for td in sublist]) if any(times_distances) else ([], [])
                    tmin, tmax, tavg = calculate_stats(times)
                    dmin, dmax, davg = calculate_stats(distances)
                    category_data[f'{section_title}_tmin'] = tmin
                    category_data[f'{section_title}_tmax'] = tmax
                    category_data[f'{section_title}_tavg'] = tavg
                    category_data[f'{section_title}_dmin'] = dmin
                    category_data[f'{section_title}_dmax'] = dmax
                    category_data[f'{section_title}_davg'] = davg
        
        all_data.append({
            "direccion": direccion,
            "precio_uf": price,
            **specs_data,
            **category_data
        })

        if index % reset_interval == 0 and index != 0:
            browser.quit()
            browser = initialize_browser()

    except Exception as e:
        print(f"Error procesando la URL {url}: {str(e)}")

browser.quit()
df = pd.DataFrame(all_data)
df.to_csv('Ds_Output/output_data.csv', sep='|', index=False)
