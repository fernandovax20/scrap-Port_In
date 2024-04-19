import pandas as pd
import os

def merge_csv_files(input_folder, output_file, delimiter='|'):
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
    
    # Guardar el dataframe combinado en un nuevo archivo CSV
    combined_df.to_csv(output_file, index=False, sep=delimiter)
    print(f'Archivo combinado guardado en: {output_file}')

# Configuración de rutas de archivo
input_folder_path = 'Ds_Output'  # Asegúrate de que esta ruta sea correcta
output_csv_path = 'Ds_Output/combined_output.csv'  # Ajusta esta ruta y nombre de archivo como prefieras

# Llamar a la función con las rutas de los archivos
merge_csv_files(input_folder_path, output_csv_path)
