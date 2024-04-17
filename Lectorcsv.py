import pandas as pd

# Reemplaza 'ruta_del_archivo.csv' con la ruta real de tu archivo
archivo = 'output_data.csv'
df = pd.read_csv(archivo, delimiter='|', nrows=0)  # nrows=0 carga solo las cabeceras

# Mostrar las cabeceras originales
original_headers = df.columns.tolist()
original_headers

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
cabeceras_unicas, len(cabeceras_unicas)

print(len(cabeceras_unicas), "cabeceras únicas")
print(cabeceras_unicas)