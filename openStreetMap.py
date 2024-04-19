import pandas as pd
import overpy
from geopy.distance import geodesic

def calcular_distancias_y_tiempo(nodos, origen):
    velocidad_caminata_kmh = 5
    min_dist = float('inf')
    max_dist = 0
    total_dist = 0
    total_nodos = len(nodos)

    for nodo in nodos:
        destino = (nodo.lat, nodo.lon)
        distancia = geodesic(origen, destino).meters
        min_dist = min(min_dist, distancia)
        max_dist = max(max_dist, distancia)
        total_dist += distancia

    promedio_dist = total_dist / total_nodos if total_nodos > 0 else 0
    min_tiempo = (min_dist / 1000) / velocidad_caminata_kmh * 60
    max_tiempo = (max_dist / 1000) / velocidad_caminata_kmh * 60
    promedio_tiempo = (promedio_dist / 1000) / velocidad_caminata_kmh * 60

    return {
        'tmin': round(min_tiempo, 1),
        'tmax': round(max_tiempo, 1),
        'tavg': round(promedio_tiempo, 1),
        'dmin': round(min_dist, 1),
        'dmax': round(max_dist, 1),
        'davg': round(promedio_dist, 1)
    }

def buscar_entidades(lat, lon, radio=8000):
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

# Coordenadas de ejemplo cerca de Santiago de Chile
latitud = -33.448609
longitud = -70.633739

resultados = buscar_entidades(latitud, longitud)
# Convertir los resultados en un DataFrame y guardarlo en CSV
df = pd.DataFrame([resultados])
df.to_csv('resultados_entidades.csv', sep='|', index=False)
