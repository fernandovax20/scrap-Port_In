import overpy
from geopy.distance import geodesic

def calcular_distancias_y_tiempo(nodos, origen):
    # Velocidad de caminata promedio en km/h
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
    min_tiempo = (min_dist / 1000) / velocidad_caminata_kmh * 60  # Convertir a minutos
    max_tiempo = (max_dist / 1000) / velocidad_caminata_kmh * 60
    promedio_tiempo = (promedio_dist / 1000) / velocidad_caminata_kmh * 60

    return min_dist, max_dist, promedio_dist, min_tiempo, max_tiempo, promedio_tiempo

def buscar_entidades(lat, lon, radio=8000):
    api = overpy.Overpass()
    origen = (lat, lon)

    tipos_entidades = {
        "universidades": '"amenity"="university"',
        "paraderos": '"highway"="bus_stop"',
        "metros": '"railway"="subway_entrance"',
        "clínicas": '"amenity"="clinic"',
        "hospitales": '"amenity"="hospital"',
        "parques": '"leisure"="park"'
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
        resultados[tipo] = distancias

    return resultados

# Coordenadas de ejemplo cerca de Santiago de Chile
latitud = -33.448609
longitud = -70.633739

resultados = buscar_entidades(latitud, longitud)
for tipo, distancias in resultados.items():
    print(f"{tipo} - Distancia mínima: {distancias[0]:.2f} m, Máxima: {distancias[1]:.2f} m, Promedio: {distancias[2]:.2f} m")
    print(f"  Tiempo mínimo: {distancias[3]:.2f} min, Máximo: {distancias[4]:.2f} min, Promedio: {distancias[5]:.2f} min")
