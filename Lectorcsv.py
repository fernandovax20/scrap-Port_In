import pandas as pd

# Reemplaza 'ruta_del_archivo.csv' con la ruta real de tu archivo
archivo = 'Ds_output/output_data.csv'
df = pd.read_csv(archivo, delimiter='|')  # Carga todo el DataFrame sin el parámetro nrows

# Mostrar las cabeceras originales
original_headers = df.columns.tolist()

def limpiar_cabecera(cabecera):
    sufijos = ['_tmin', '_tmax', '_tavg', '_dmin', '_dmax', '_davg']
    for sufijo in sufijos:
        cabecera = cabecera.replace(sufijo, '')
    return cabecera

# Limpiar las cabeceras
cabeceras_limpias = [limpiar_cabecera(cabecera) for cabecera in original_headers]

# Hacer las cabeceras únicas
cabeceras_unicas = list(set(cabeceras_limpias))

# Ordenar las cabeceras únicas para mejor visualización
cabeceras_unicas.sort()

# Mostrar las cabeceras únicas y contar cuántas son
print(f"{len(cabeceras_unicas)} cabeceras únicas:", cabeceras_unicas)

# Contar el número de filas en el dataset
numero_de_filas = df.shape[0]

# Imprimir los resultados
print(f"Número de filas en el dataset: {numero_de_filas}")


columna_primera = df.columns[0]  # Asumiendo que es la primera columna

# Contar cuántas filas tienen la primera columna vacía o nula
filas_con_primera_columna_vacia = df[columna_primera].isna().sum()

# Imprimir el resultado
print(f"Número de filas con la primera columna ({columna_primera}) vacía o nula: {filas_con_primera_columna_vacia}")