import pandas as pd
import os

def merge_and_clean_csv_files(input_folder, output_file, delimiter='|'):
    dataframes = []
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_folder, filename)
            # Leer cada archivo usando el delimitador proporcionado
            df = pd.read_csv(file_path, sep=delimiter, on_bad_lines='skip')  # Usar 'skip' para omitir líneas mal formadas
            dataframes.append(df)
    
    # Combinar todos los dataframes en uno solo
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Eliminar duplicados basándonos en la columna 'url'
    combined_df = combined_df.drop_duplicates(subset=['url'])

    # Columnas a verificar por valores nulos
    columns_to_check = ['direccion', 'precio_uf', 'metros_cuadrados', 'dormitorios', 'banios', 'latitude', 'longitude']

    # Filtrar filas que no tengan nulos en 'columns_to_check'
    clean_df = combined_df[~combined_df[columns_to_check].isnull().any(axis=1)]

    # Guardar el DataFrame limpio en un nuevo archivo CSV
    clean_df.to_csv(output_file, index=False, sep=delimiter)
    print(f'Archivo combinado y limpio guardado en: {output_file}')

# Configuración de rutas de archivo
input_folder_path = 'Ds_Output'  # Asegúrate de que esta ruta sea correcta
output_csv_path = 'Ds_Output/combined_clean_output.csv'  # Ajusta esta ruta y nombre de archivo como prefieras

# Llamar a la función con las rutas de los archivos
merge_and_clean_csv_files(input_folder_path, output_csv_path)
