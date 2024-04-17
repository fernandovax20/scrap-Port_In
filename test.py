import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import sys
import re
import time
from selenium.webdriver.common.by import By

# Lee las URLs desde un archivo
filename = sys.argv[1] if len(sys.argv) > 1 else 'urlsPropiedadesUsadas.txt'
with open(f"Data/{filename}", 'r') as file:
    lines = [line.strip() for line in file]

# Inicializa el navegador utilizando undetected_chromedriver
browser = uc.Chrome()

browser.get("https://valoruf.cl")

# Encuentra el valor de la UF en la página
ufpesor = browser.find_element(By.ID, "ufpesor").text.replace(".", "").replace(",", ".")
valor_uf = float(ufpesor)
print(valor_uf)


for url in lines:
    # Navegar a la página del inmueble
    browser.get(url)

    
    browser.implicitly_wait(10)

    # Encuentra el botón para aceptar cookies y haz clic en él si es necesario
    try:
        cookie_button = browser.find_element("xpath",'//*[@id="newCookieDisclaimerButton"]').click()
    except Exception as e:
        print("El botón de cookies no se encontró o no fue necesario clickearlo.")

    

    # Obtén el HTML de la página y crea un objeto BeautifulSoup
    html = browser.page_source
    soup = BeautifulSoup(html, "lxml")
    print("\n\n")
    # Utiliza BeautifulSoup para encontrar el párrafo que contiene la dirección
    direccion_container = soup.select_one(".ui-vip-location__subtitle .ui-pdp-media__title")
    if direccion_container:
        direccion = direccion_container.get_text(strip=True)
        
    else:
        direccion = None
    
    print(f"Dirección encontrada: {direccion}")

    price_container = soup.find("div", class_="ui-pdp-price__second-line") # Asegúrate de que esta clase sea correcta
    if price_container:
        price_span = price_container.find("span", class_="andes-money-amount__fraction") # Asegúrate de que esta clase sea correcta
        price_type = price_container.find("span", class_="andes-money-amount__currency-symbol") # Asegúrate de que esta clase sea correcta
        if price_span and price_type:
            price = price_span.get_text(strip=True).replace(".", "")
            price_type = price_type.get_text(strip=True)

            # Convierte el precio a UF si es necesario
            if price_type == "$":
                price = float(price) / valor_uf
                print(f"Valor en UF: {int(price)}")
            else:
                print(f"Valor en UF: {price}")
        else:
            print(f"No se pudo encontrar la información de precio en {url}")


    # Busca el contenedor de especificaciones
    specs_container = soup.find(id="highlighted_specs_res")
    if specs_container:
        spec_elements = specs_container.select(".ui-pdp-highlighted-specs-res__icon-label")
        
        # Diccionario para guardar los resultados
        data = {}

        # Extrae y muestra el número entero de cada elemento encontrado
        for spec in spec_elements:
            label = spec.select_one(".ui-pdp-label").text if spec.select_one(".ui-pdp-label") else ""
            # Extrae el número usando expresiones regulares
            numbers = re.findall(r"\d+\.?\d*", label)

            if 'm²' in label:
                # Calcula el promedio si hay un rango, de lo contrario toma el único número
                if len(numbers) == 2:
                    average = int((float(numbers[0]) + float(numbers[1])) / 2)
                    data['Metros cuadrados'] = average
                else:
                    data['Metros cuadrados'] = int(float(numbers[0]))
            elif 'dormitorio' in label:
                data['Dormitorios'] = int(numbers[0])
            elif 'baño' in label:
                data['Baños'] = int(numbers[0])

        # Imprime los resultados
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print("Contenedor de especificaciones no encontrado.")


    tab_buttons = browser.find_elements(By.CSS_SELECTOR, ".andes-tabs__container button")
    # Extrae los identificadores de los botones
    tab_ids = [button.get_attribute('id') for button in tab_buttons if button.get_attribute('id')]
    # Navegación entre pestañas de 'Transporte' y 'Educación'
    for tab_id in tab_ids:  # IDs de pestañas
        tab = browser.find_element(By.XPATH, f"//button[@id='{tab_id}']")
        tab.click()
        time.sleep(2)  # Espera para que el contenido se cargue

        # Extrae y procesa la pestaña actual
        tab_content_html = browser.page_source
        soup = BeautifulSoup(tab_content_html, 'lxml')
        current_tab = soup.find("div", {"aria-labelledby": tab_id})
        if current_tab:
            sections = current_tab.find_all("div", class_="ui-vip-poi__subsection")
            for section in sections:
                section_title = section.find("span", class_="ui-vip-poi__subsection-title").get_text(strip=True)
                print(section_title)
                items = section.find_all("div", class_="ui-vip-poi__item")
                for item in items:
                    item_title = item.find("span", class_="ui-pdp-color--BLACK").get_text(strip=True)
                    details = item.find("span", class_="ui-pdp-color--GRAY").get_text(strip=True)
                    
                    # Intenta extraer tiempo y distancia usando expresiones regulares
                    time_distance = re.findall(r"(\d+) mins - (\d+) metros", details)
                    
                    if time_distance:
                        print(f"    {item_title}: Tiempo (mins): {time_distance[0][0]}, Distancia (metros): {time_distance[0][1]}")
                    else:
                        print(f"    {item_title}: Tiempo y distancia no disponibles")
        else:
            print(f"Pestaña {tab_id} no contiene datos.")

    print("\n\n")

# Cierra el navegador después de iterar todas las URLs
browser.quit()
