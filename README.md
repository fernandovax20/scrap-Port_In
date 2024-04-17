# Web Scraper de Propiedades

Este script en Python utiliza Selenium y BeautifulSoup para automatizar la extracción de información detallada sobre propiedades inmobiliarias desde páginas web especificadas en un archivo de texto. Está diseñado para ayudar en la agregación de datos y análisis inmobiliario.

## Requisitos

- Python 3.x
- Bibliotecas Python:
  - `selenium`
  - `undetected_chromedriver`
  - `beautifulsoup4`
  - `re`
  - `time`
  - `sys`

Instale las dependencias necesarias con:
```bash
pip install selenium undetected_chromedriver beautifulsoup4
```

## Configuración y Uso

1. **Archivo de URLs**: El script lee las URLs de las propiedades desde un archivo de texto. Por defecto, el archivo debe llamarse `urlsPropiedadesNuevas.txt` y estar ubicado en la carpeta `Data`.

2. **Valor de UF**: El valor de la Unidad de Fomento (UF) debe ser actualizado en el script según sea necesario. Este valor se utiliza para convertir precios desde CLP a UF.

## Funcionalidades

- **Navegación Automatizada**: Usa `undetected_chromedriver` para controlar un navegador de manera automatizada y acceder a las URLs especificadas.
  
- **Extracción de Datos**: Analiza las páginas de propiedades para obtener:
  - Direcciones
  - Precios y su conversión a UF si están en pesos chilenos.
  - Metros cuadrados, número de dormitorios y baños.
  
- **Interacción con Pestañas**: Navega entre pestañas de información adicional como Transporte y Educación para extraer más datos sobre los servicios cercanos a la propiedad.

- **Manejo de Excepciones**: Gestiona situaciones donde elementos como botones de aceptar cookies no se encuentran o no son necesarios.

## Ejecución del Script

Ejecute el script desde la línea de comandos:
```bash
python script_name.py [nombre_archivo_urls]
```

Si no se especifica un archivo de URLs, el script buscará `urlsPropiedadesNuevas.txt` por defecto.

## Cierre del Navegador

El navegador se cierra automáticamente al finalizar la ejecución para liberar recursos.

## Notas

- Asegúrese de que las clases y selectores usados para buscar elementos en las páginas web estén actualizados según los cambios que puedan realizar los sitios web objetivo.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.

