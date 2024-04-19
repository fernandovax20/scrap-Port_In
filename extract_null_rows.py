import pandas as pd

def filter_and_save_urls(file_path, output_file_path):
    # Leer el archivo CSV
    df = pd.read_csv(file_path, sep='|')

    # Columnas a verificar por valores nulos
    columns_to_check = ['direccion', 'precio_uf', 'metros_cuadrados', 'dormitorios', 'banios', 'latitude', 'longitude']

    # Filtrar filas con cualquier columna nula en 'columns_to_check'
    filtered_urls = df[df[columns_to_check].isnull().any(axis=1)]['url']

    # Guardar las URLs filtradas en un archivo de texto
    with open(output_file_path, 'w') as file:
        for url in filtered_urls:
            file.write(url + '\n')

    print(f'URLs guardadas en {output_file_path}')

# Configuración de rutas de archivo de ejemplo (ajusta según tus necesidades)
input_csv_path = 'Ds_Output/combined_output.csv'  # Ajusta esta ruta al lugar donde tienes el archivo CSV
output_txt_path = 'Data/filtered_urls.txt'  # Ajusta esta ruta a donde quieres guardar el archivo

# Llamar a la función con las rutas de los archivos
filter_and_save_urls(input_csv_path, output_txt_path)
