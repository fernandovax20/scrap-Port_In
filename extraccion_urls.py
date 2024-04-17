import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

links = [
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/bulnes-santiago-santiago-metropolitana/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYQnVsbmVzVFV4RFExTkJUams0TTJN%26applied_value_name%3DBulnes%26applied_value_order%3D8%26applied_value_results%3D991%26is_custom%3Dfalse",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/centro-historico-de-santiago-santiago-santiago-metropolitana/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYQ2VudHJvIEhpc3TDs3JpY28gZGUgU2Fud%26applied_value_name%3DCentro+Hist%C3%B3rico+de+Santiago%26applied_value_order%3D9%26applied_value_results%3D2434%26is_custom%3Dfalse",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/santa-isabel-santiago-santiago-metropolitana/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYU2FudGEgSXNhYmVsVFV4RFExTkJUams0T%26applied_value_name%3DSanta+Isabel%26applied_value_order%3D19%26applied_value_results%3D2002%26is_custom%3Dfalse",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/rm-metropolitana/santiago/san-diego/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYU2FuIERpZWdvVFV4RFExTkJUams0TTJN%26applied_value_name%3DSan+Diego%26applied_value_order%3D18%26applied_value_results%3D834%26is_custom%3Dfalse",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/parque-ohiggins-santiago-santiago-metropolitana/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYUGFycXVlIE8nSGlnZ2luc1RVeERRMU5CV%26applied_value_name%3DParque+O%27Higgins%26applied_value_order%3D17%26applied_value_results%3D803%26is_custom%3Dfalse",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/rm-metropolitana/santiago/parque-almagro/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYUGFycXVlIEFsbWFncm9UVXhEUTFOQlRqa%26applied_value_name%3DParque+Almagro%26applied_value_order%3D15%26applied_value_results%3D646%26is_custom%3Dfalse",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/bogota-sierra-bella-santiago-santiago-metropolitana/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYQm9nb3TDoSAtIFNpZXJyYSBCZWxsYVRVe%26applied_value_name%3DBogot%C3%A1+-+Sierra+Bella%26applied_value_order%3D7%26applied_value_results%3D586%26is_custom%3Dfalse",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/rm-metropolitana/santiago/barrio-diez-de-julio/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYQmFycmlvIERpZXogZGUgSnVsaW9UVXhEU%26applied_value_name%3DBarrio+Diez+de+Julio%26applied_value_order%3D2%26applied_value_results%3D556%26is_custom%3Dfalse",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/rm-metropolitana/santiago/ejercito---toesca/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYRWrDqXJjaXRvIC0gVG9lc2NhVFV4RFExT%26applied_value_name%3DEj%C3%A9rcito+-+Toesca%26applied_value_order%3D12%26applied_value_results%3D418%26is_custom%3Dfalse",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/barrio-brasil-santiago-santiago-metropolitana",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/barrio-republica-santiago-santiago-metropolitana",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/club-hipico-santiago-santiago-metropolitana",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/franklin-biobio-santiago-santiago-metropolitana",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/rm-metropolitana/santiago/parque-los-reyes",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/rm-metropolitana/santiago/barrio-san-borja",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/rm-metropolitana/santiago/dieciocho",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/rm-metropolitana/santiago/meiggs",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/barrio-lastarria-santiago-santiago-metropolitana",
    "https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/barrio-yungay-santiago-santiago-metropolitana",
    "https://www.portalinmobiliario.com/tienda-oficial/venta/departamento/santiago-metropolitana/_Tienda_all#applied_filter_id%3Dofficial_store%26applied_filter_name%3DTiendas+oficiales%26applied_filter_order%3D3%26applied_value_id%3Dall%26applied_value_name%3DSolo+tiendas+oficiales%26applied_value_order%3D1%26applied_value_results%3D1985%26is_custom%3Dfalse"
]

# Inicializa el navegador con undetected_chromedriver
browser = uc.Chrome()
#browser.get("https://www.portalinmobiliario.com/venta/departamento/propiedades-usadas/bulnes-santiago-santiago-metropolitana/_NoIndex_True#applied_filter_id%3Dneighborhood%26applied_filter_name%3DBarrios%26applied_filter_order%3D4%26applied_value_id%3DTVhYQnVsbmVzVFV4RFExTkJUams0TTJN%26applied_value_name%3DBulnes%26applied_value_order%3D8%26applied_value_results%3D991%26is_custom%3Dfalse")

# Conjunto para almacenar enlaces únicos
unique_links = set()

# Recorre cada URL de la lista
for link in links:
    browser.get(link)
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ol')))
    try:
        cookie_button = browser.find_element("xpath",'//*[@id="newCookieDisclaimerButton"]').click()
    except Exception as e:
        print("El botón de cookies no se encontró o no fue necesario clickearlo.")


    # Procesa múltiples páginas si es necesario
    while True:
        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        list_items = soup.find('ol').find_all('li')

        for li in list_items:
            a_tag = li.find('a', class_='ui-search-result__image ui-search-link')
            if a_tag and a_tag['href'] not in unique_links:
                unique_links.add(a_tag['href'])

        # Navegar a la siguiente página si es posible
        try:
            next_button = browser.find_element(By.CSS_SELECTOR, 'li.andes-pagination__button--next a.andes-pagination__link')
            if "disabled" in next_button.get_attribute("class"):
                break
            next_button.click()
            WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'ol')))
        except Exception as e:
            print("No se encontró más páginas o ocurrió un error:", e)
            break

# Cierra el navegador
browser.quit()

# Guardar los enlaces únicos en un archivo de texto
with open('unique_links.txt', 'w', encoding='utf-8') as file:
    for link in unique_links:
        file.write(link + '\n')

print("Se han guardado los enlaces únicos en 'unique_links.txt'.")
