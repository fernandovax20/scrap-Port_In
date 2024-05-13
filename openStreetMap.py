import pandas as pd
import overpy
from geopy.distance import geodesic

def calcular_distancias_y_tiempo(nodos, origen):
    velocidad_caminata_kmh = 5
    # Inicializa todas las variables a None
    min_dist = max_dist = total_dist = promedio_dist = None
    min_tiempo = max_tiempo = promedio_tiempo = None

    total_nodos = len(nodos)

    if total_nodos > 0:
        min_dist = float('inf')
        max_dist = total_dist = 0

        # Calcula distancias para cada nodo
        for nodo in nodos:
            destino = (nodo.lat, nodo.lon)
            distancia = geodesic(origen, destino).meters
            min_dist = min(min_dist, distancia)
            max_dist = max(max_dist, distancia)
            total_dist += distancia

        promedio_dist = total_dist / total_nodos
        min_tiempo = (min_dist / 1000) / velocidad_caminata_kmh * 60
        max_tiempo = (max_dist / 1000) / velocidad_caminata_kmh * 60
        promedio_tiempo = (promedio_dist / 1000) / velocidad_caminata_kmh * 60

        return {
            'tiempo(minutos)_min': round(min_tiempo, 1),
            'tiempo(minutos)_max': round(max_tiempo, 1),
            'tiempo(minutos)_avg': round(promedio_tiempo, 1),
            'dist(metros)_min': round(min_dist, 1),
            'dist(metros)_max': round(max_dist, 1),
            'dist(metros)_avg': round(promedio_dist, 1)
        }
    else:
        return {
            'tiempo(minutos)_min': None,
            'tiempo(minutos)_max': None,
            'tiempo(minutos)_avg': None,
            'dist(metros)_min': None,
            'dist(metros)_max': None,
            'dist(metros)_avg': None
        }

def buscar_entidades(lat, lon, radio=1000):
    api = overpy.Overpass()
    origen = (lat, lon)
    tipos_entidades = {
        "centros_comerciales": '"shop"="mall"',
        "clinicas": '"amenity"="clinic"',
        "colegios": '"amenity"="school"',
        "estaciones_de_metro": '"railway"="subway_entrance"',
        "farmacias": '"amenity"="pharmacy"',
        "hospitales": '"amenity"="hospital"',
        "jardines_infantiles": '"amenity"="kindergarten"',
        "paraderos": '"highway"="bus_stop"',
        "plazas": '"leisure"="park"',
        "supermercados": '"shop"="supermarket"',
        "universidades": '"amenity"="university"'
    }

    resultados = {}
    for tipo, etiqueta in tipos_entidades.items():
        consulta = f"""
        [out:json];
        (
          node[{etiqueta}](around:{radio},{lat},{lon});
        );
        out body;
        """
        resultado = api.query(consulta)
        distancias = calcular_distancias_y_tiempo(resultado.nodes, origen)
        resultados.update({f"{tipo}_{k}": v for k, v in distancias.items()})

    return resultados

ruta_archivo_original = "Ds_Output/combined_clean_output_test.csv"
df_original = pd.read_csv(ruta_archivo_original, sep='|')
url_index = df_original.columns.get_loc("url")

# Preparar para procesar las filas y guardar cada 10 iteraciones
batch_size = 10
batch_number = 0

for idx, row in df_original.iterrows():
    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
        print(f"Procesando fila {idx + 1}...")
        datos_osm = buscar_entidades(row['latitude'], row['longitude'])
        for key, value in datos_osm.items():
            if key not in df_original:
                df_original.insert(loc=url_index, column=key, value=pd.NA)
                url_index += 1
            df_original.at[idx, key] = value

    # Guardar en el archivo CSV cada 10 filas
    if (idx + 1) % batch_size == 0:
        batch_number += 1
        print(f"Guardando lote {batch_number} en el archivo...")
        df_original.to_csv("Ds_Output/output_data_enriched.csv", sep='|', index=False)

# Asegúrate de guardar los datos restantes si no son múltiplos de 10
if len(df_original) % batch_size != 0:
    print("Guardando las filas finales...")
    df_original.to_csv("Ds_Output/output_data_enriched.csv", sep='|', index=False)

print("Datos combinados y guardados exitosamente.")
