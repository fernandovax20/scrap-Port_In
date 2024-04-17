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
import unicodedata

def calculate_stats(values):
    if not values:
        return None, None, None
    valid_values = [v for v in values if v is not None]
    if not valid_values:
        return None, None, None
    # Redondeamos los resultados a un decimal
    return round(min(valid_values), 1), round(max(valid_values), 1), round(np.mean(valid_values), 1)

def extract_time_distance(details):
    results = re.findall(r"(\d+)\s+mins\s+-\s+(\d+)\s+metros", details)
    return [(int(t), int(d)) for t, d in results] if results else []

def normalize_string(input_str):
    normalized_str = unicodedata.normalize('NFD', input_str)
    no_accents_str = ''.join([char for char in normalized_str if unicodedata.category(char) != 'Mn'])
    lower_str = no_accents_str.lower()
    return lower_str

filename = sys.argv[1] if len(sys.argv) > 1 else 'urlsPropiedadesUsadas.txt'
with open(f"Data/{filename}", 'r') as file:
    urls = [line.strip() for line in file]

browser = uc.Chrome()

# Navega a la página de valor de la UF
browser.get("https://valoruf.cl")
# Encuentra el valor de la UF en la página
ufpesor = browser.find_element(By.ID, "ufpesor").text.replace(".", "").replace(",", ".")
valor_uf = float(ufpesor)


all_data = []
for url in urls:
    browser.get(url)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "footer")))
    
    try:
        cookie_button = browser.find_element("xpath", '//*[@id="newCookieDisclaimerButton"]').click()
    except Exception as e:
        print("El botón de cookies no se encontró o no fue necesario clickearlo.")

    html = browser.page_source
    soup = BeautifulSoup(html, "lxml")

    #Direccion
    direccion_container = soup.select_one(".ui-vip-location__subtitle .ui-pdp-media__title")
    direccion = direccion_container.get_text(strip=True) if direccion_container else None

    #Precio en UF
    price_container = soup.find("div", class_="ui-pdp-price__second-line") 
    price = 0
    if price_container:
        price_span = price_container.find("span", class_="andes-money-amount__fraction") 
        price_type = price_container.find("span", class_="andes-money-amount__currency-symbol") 
        if price_span and price_type:
            price = price_span.get_text(strip=True).replace(".", "")
            price_type = price_type.get_text(strip=True)

            # Convierte el precio a UF si es necesario
            if price_type == "$":
                price = float(price) / valor_uf
                price = int(price)

    #Información de la propiedad
    specs_container = soup.find(id="highlighted_specs_res")
    specs_data = {'metros_cuadrados': 0, 'dormitorios': 0, 'Banios': 0}
    if specs_container:
        spec_elements = specs_container.select(".ui-pdp-highlighted-specs-res__icon-label")
        for spec in spec_elements:
            label = spec.select_one(".ui-pdp-label").text if spec.select_one(".ui-pdp-label") else ""
            numbers = re.findall(r"\d+\.?\d*", label)
            if 'm²' in label:
                specs_data['metros_cuadrados'] = int(numbers[0]) if numbers else 0
            elif 'dormitorio' in label:
                specs_data['dormitorios'] = int(numbers[0]) if numbers else 0
            elif 'baño' in label:
                specs_data['Banios'] = int(numbers[0]) if numbers else 0


    #Información de cercanías y servicios de la propiedad
    tab_buttons = browser.find_elements(By.CSS_SELECTOR, ".andes-tabs__container button")
    category_data = {}

    for button in tab_buttons:
        button_id = button.get_attribute('id')
        button.click()
        time.sleep(2)  # Allow for content to load

        tab_content_html = browser.page_source
        tab_soup = BeautifulSoup(tab_content_html, 'lxml')
        current_tab = tab_soup.find("div", {"aria-labelledby": button_id})

        if current_tab:
            sections = current_tab.find_all("div", class_="ui-vip-poi__subsection")
            for section in sections:
                section_title = section.find("span", class_="ui-vip-poi__subsection-title").get_text(strip=True).replace(" ", "_")
                section_title = normalize_string(section_title)
                items = section.find_all("div", class_="ui-vip-poi__item")
                
                times_distances = [extract_time_distance(item.find("span", class_="ui-pdp-color--GRAY").get_text(strip=True)) for item in items]
                if times_distances:
                    times, distances = zip(*[td for sublist in times_distances for td in sublist]) if any(times_distances) else ([], [])
                else:
                    times, distances = ([], [])

                tmin, tmax, tavg = calculate_stats(times)
                dmin, dmax, davg = calculate_stats(distances)
                
                category_data[f'{section_title}_tmin'] = tmin
                category_data[f'{section_title}_tmax'] = tmax
                category_data[f'{section_title}_tavg'] = tavg
                category_data[f'{section_title}_dmin'] = dmin
                category_data[f'{section_title}_dmax'] = dmax
                category_data[f'{section_title}_davg'] = davg

    all_data.append({
        "Direccion": direccion,
        "Precio_UF": price,
        **specs_data,
        **category_data
    })

df = pd.DataFrame(all_data)
df.to_csv('Ds_Output/output_data.csv', sep='|', index=False)
browser.quit()
