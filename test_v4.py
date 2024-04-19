import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy_playwright.page import PageMethod
import re

class PropertySpider(scrapy.Spider):
    name = 'property_spider'
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'output_data.csv',
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_playwright.middleware.PlaywrightMiddleware': 800
        }
    }

    def start_requests(self):
        url_uf = "https://valoruf.cl"
        yield scrapy.Request(
            url=url_uf,
            callback=self.parse_uf,
            meta={
                'playwright': True,
                'playwright_include_page': True,
                'playwright_page_coroutines': [
                    PageMethod('wait_for_selector', '#ufpesor')
                ]
            }
        )

    def parse_uf(self, response, page):
        ufpesor = response.css("#ufpesor::text").get().replace(".", "").replace(",", ".")
        self.valor_uf = float(ufpesor)
        page.close()
        # Continúa con la apertura del archivo y la programación de las solicitudes de propiedad
        with open('Data/test.txt', 'r') as file:
            urls = [line.strip() for line in file]
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_property,
                meta={
                    'valor_uf': self.valor_uf,
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_coroutines': [
                        PageMethod('wait_for_selector', '.ui-vip-location__subtitle .ui-pdp-media__title'),
                        PageMethod('wait_for_selector', '#highlighted_specs_res')
                    ]
                }
            )

    def parse_property(self, response, page):
        # Extracción de datos usando la respuesta y el objeto page si es necesario
        direccion = response.css(".ui-vip-location__subtitle .ui-pdp-media__title::text").get()
        price_container = response.css("div.ui-pdp-price__second-line")
        price = 0
        if price_container:
            price_span = price_container.css("span.andes-money-amount__fraction::text").get()
            price_type = price_container.css("span.andes-money-amount__currency-symbol::text").get()
            if price_span and price_type == "$":
                price = float(price_span.replace(".", "")) / response.meta['valor_uf']
                price = int(price)

        specs_data = self.extract_specs(response)
        latitude, longitude = self.extract_coordinates(response)

        yield {
            'url': response.url,
            'direccion': direccion,
            'precio_uf': price,
            **specs_data,
            'latitude': latitude,
            'longitude': longitude
        }
        page.close()

    def extract_specs(self, response):
        specs_data = {'metros_cuadrados': 0, 'dormitorios': 0, 'banios': 0}
        specs_container = response.css("#highlighted_specs_res")
        if specs_container:
            spec_elements = specs_container.css(".ui-pdp-highlighted-specs-res__icon-label")
            for spec in spec_elements:
                label = spec.css(".ui-pdp-label::text").get()
                if label:
                    numbers = re.findall(r"\d+\.?\d*", label)
                    if 'm²' in label:
                        specs_data['metros_cuadrados'] = int(float(numbers[0])) if numbers else 0
                    elif 'dormitorio' in label:
                        specs_data['dormitorios'] = int(float(numbers[0])) if numbers else 0
                    elif 'baño' in label:
                        specs_data['banios'] = int(float(numbers[0])) if numbers else 0
        return specs_data


    def extract_coordinates(self, response):
        latitude, longitude = None, None
        map_container = response.css("#ui-vip-location__map img::attr(srcset)").get()
        if map_container:
            coords_match = re.search(r'center=(-?\d+\.\d+),(-?\d+\.\d+)', map_container.replace("%2C", ","))
            if coords_match:
                latitude, longitude = map(float, coords_match.groups())
        return latitude, longitude

if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(PropertySpider)
    process.start()
