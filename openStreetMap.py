import pandas as pd
import overpy
from geopy.distance import geodesic
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

        # Redondea los resultados si hay nodos
        return {
            'tiempo(minutos)_min': round(min_tiempo, 1),
            'tiempo(minutos)_max': round(max_tiempo, 1),
            'tiempo(minutos)_avg': round(promedio_tiempo, 1),
            'dist(metros)_min': round(min_dist, 1),
            'dist(metros)_max': round(max_dist, 1),
            'dist(metros)_avg': round(promedio_dist, 1)
        }
    else:
        # Devuelve None para todos los valores si no hay nodos
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

# Cargar archivo original y procesar solo las primeras 10 filas
ruta_archivo_original = "Ds_Output/output_data_2024-04-18_22-28-33.csv"
df_original = pd.read_csv(ruta_archivo_original, sep='|')

url_index = df_original.columns.get_loc("url")  # Encontrar el índice de la columna 'url'

# Preparar para procesar solo las primeras 10 filas
for idx, row in df_original.head(10).iterrows():
    if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
        print(f"Procesando fila {idx + 1}...")
        datos_osm = buscar_entidades(row['latitude'], row['longitude'])
        
        # Añadir nuevas columnas si no existen y asignar valores
        for key, value in datos_osm.items():
            if key not in df_original:
                df_original.insert(loc=url_index, column=key, value=pd.NA)
                url_index += 1  # Incrementar para la siguiente inserción
            df_original.at[idx, key] = value  # Asignar valor a la fila actual
            
    print(f"Fila {idx + 1} completada.")

# Guardar el DataFrame actualizado
df_original.to_csv("Ds_Output/output_data_enriched.csv", sep='|', index=False)
print("Datos combinados y guardados exitosamente.")