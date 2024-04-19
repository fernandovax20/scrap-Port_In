import scrapy
import pandas as pd
import numpy as np
import re
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class PropertySpider(scrapy.Spider):
    name = "property_spider"

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'AUTOTHROTTLE_ENABLED': True,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }


    def start_requests(self):
        filename = 'urlsPropiedadesUsadas.txt'  # Asumiendo que el archivo está en el mismo directorio
        with open(f"Data/{filename}", 'r') as file:
            urls = [line.strip() for line in file]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Extraer dirección
        direccion = response.css(".ui-vip-location__subtitle .ui-pdp-media__title::text").get()

        # Extraer precio en UF
        price = 0
        price_container = response.css("div.ui-pdp-price__second-line")
        if price_container:
            price_span = price_container.css("span.andes-money-amount__fraction::text").get()
            price_type = price_container.css("span.andes-money-amount__currency-symbol::text").get()
            if price_span and price_type and price_type == "$":
                price = float(price_span.replace(".", "")) / self.valor_uf
                price = int(price)

        # Extraer información de la propiedad
        specs_data = {'metros_cuadrados': 0, 'dormitorios': 0, 'banios': 0}
        specs_container = response.css("#highlighted_specs_res")
        if specs_container:
            spec_elements = specs_container.css(".ui-pdp-highlighted-specs-res__icon-label")
            for spec in spec_elements:
                label = spec.css(".ui-pdp-label::text").get()
                numbers = re.findall(r"\d+\.?\d*", label)
                if 'm²' in label:
                    specs_data['metros_cuadrados'] = int(float(numbers[0])) if numbers else 0
                elif 'dormitorio' in label:
                    specs_data['dormitorios'] = int(float(numbers[0])) if numbers else 0
                elif 'baño' in label:
                    specs_data['banios'] = int(float(numbers[0])) if numbers else 0

        # Luego de extraer todos los datos
        yield {
            "direccion": direccion,
            "precio_uf": price,
            **specs_data
        }

    def closed(self, reason):
        all_data = self.crawler.stats.get_value('item_scraped_count')
        df = pd.DataFrame(all_data)
        df.to_csv('Ds_Output/output_data.csv', sep='|', index=False)

# Valor de UF debería ser definido o extraído de alguna manera.
# Este ejemplo asume que el valor de UF es conocido previamente.
PropertySpider.valor_uf = 30000  # Valor de ejemplo

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(PropertySpider)
    process.start()
