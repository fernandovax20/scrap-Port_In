import pandas as pd
import numpy as np
import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import re
import sys
import unicodedata
from pathlib import Path
import shutil

async def setup_browser():
    user_data_dir = Path.cwd() / 'temp' / 'pyppeteer_data_dir'
    user_data_dir.mkdir(parents=True, exist_ok=True)  # Crea el directorio si no existe
    
    browser = await launch(
        executablePath='C:/Program Files (x86)/chrome-win/chrome.exe', 
        headless=True, 
        args=[
            '--no-sandbox', 
            '--disable-setuid-sandbox', 
            f'--user-data-dir={user_data_dir.resolve()}'
        ]
    )
    return browser, user_data_dir

async def close_browser(browser, user_data_dir):
    await browser.close()
    try:
        shutil.rmtree(user_data_dir)  # Intentar eliminar el directorio después de cerrar el navegador
    except Exception as e:
        print(f"Error al limpiar el directorio de datos del usuario: {e}")

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

async def scrape(urls, valor_uf):
    
    browser, user_data_dir = await setup_browser()
    all_data = []
    page = await browser.newPage()
    reset_interval = 20  # Reiniciar navegador cada 50 URLs

    for index, url in enumerate(urls):
        page = await browser.newPage()
        try:
            await page.goto(url)
            await page.waitForSelector("footer", {'timeout': 10000})
            content = await page.content()
            soup = BeautifulSoup(content, "lxml")

            print(f"Procesando URL {index + 1} de {len(urls)}: {url}")

            try:
                # Esperar por el botón de cookies durante un tiempo máximo de 2 segundos
                cookie_button = await page.waitForSelector('#newCookieDisclaimerButton', {'timeout': 2000})
                if cookie_button:
                    await cookie_button.click()
                    print("Botón de cookies clickeado.")
            except Exception as e:
                # Si el selector no es encontrado o el tiempo se agota, se maneja el error.
                print("El botón de cookies no fue necesario")


            try:
                # Intenta extraer la dirección
                direccion_container = soup.select_one(".ui-vip-location__subtitle .ui-pdp-media__title")
                direccion = direccion_container.get_text(strip=True) if direccion_container else None
            except Exception as e:
                print(f"No se pudo extraer la dirección: {str(e)}")
                direccion = None

            # Extraer precio en UF
            try:
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
            except Exception as e:
                print(f"No se pudo extraer el precio: {str(e)}")
                price = 0

            # Extraer información de la propiedad
            try:
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
            except Exception as e:
                print(f"No se pudo extraer la información de la propiedad: {str(e)}")
                specs_data = {'metros_cuadrados': 0, 'dormitorios': 0, 'banios': 0}

            
            # Interactuar con elementos dinámicos
            try:
                category_data = {}
                tab_buttons = await page.querySelectorAll(".andes-tabs__container button")
                for button in tab_buttons:
                    button_id = await button.getProperty('id')  # Obtener la propiedad 'id' del botón
                    button_id = await button_id.jsonValue()  # Convertir la propiedad a un valor JSON/String
                    await button.click()
                    await page.waitFor(1000)  # Esperar que se cargue el contenido
                    content = await page.content()
                    tab_soup = BeautifulSoup(content, 'lxml')
                    current_tab = tab_soup.find("div", {"aria-labelledby": button_id})  # Usar button_id aquí

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
            except Exception as e:
                print(f"No se pudo interactuar con elementos dinámicos: {str(e)}")
                category_data = {}
            
            all_data.append({
                "direccion": direccion,
                "precio_uf": price,
                **specs_data,
                **category_data
            })
            
        # Cerrar la pestaña después de procesar cada URL
            await page.close()

            if (index + 1) % reset_interval == 0 or (index + 1) == len(urls):
                # Guarda los datos actuales en el CSV
                df = pd.DataFrame(all_data)
                if not df.empty:
                    df.to_csv('Ds_Output/output_data.csv', mode='a', sep='|', index=False, header=not Path('Ds_Output/output_data.csv').exists())
                # Limpia all_data
                all_data = []
                # Reinicia el navegador si no has terminado
                if (index + 1) != len(urls):
                    browser, user_data_dir = await setup_browser()

        except Exception as e:
            print(f"Error procesando la URL {url}: {str(e)}")
            await page.close()
            # Cierra la pestaña actual para liberar recursos
    # Cierra el navegador al final del scraping
    await close_browser(browser, user_data_dir)

filename = sys.argv[1] if len(sys.argv) > 1 else 'urlsPropiedadesUsadas.txt'
with open(f"Data/{filename}", 'r') as file:
    urls = [line.strip() for line in file]

# Obtener el valor de la UF de alguna forma aquí, por ejemplo con requests-html o una función específica
async def fetch_uf_value():
    browser, user_data_dir = await setup_browser()
    page = await browser.newPage()
    await page.goto("https://valoruf.cl")
    await page.waitForSelector('#ufpesor', {'timeout': 10000})
    ufpesor = await page.evaluate('() => document.getElementById("ufpesor").innerText')
    ufpesor = ufpesor.replace(".", "").replace(",", ".")
    valor_uf = float(ufpesor)
    await close_browser(browser, user_data_dir)
    return valor_uf


valor_uf = asyncio.run(fetch_uf_value())
# Ejecutar el scraper
data = asyncio.run(scrape(urls, valor_uf))
print("Scraping completado.")
