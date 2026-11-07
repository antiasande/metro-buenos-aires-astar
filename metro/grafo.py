"""
Construcción del grafo de la red de metro con NetworkX.

Cada estación es un nodo con su posición geográfica. Cada arista guarda tres
atributos:

* ``length``: distancia en metros (fórmula de Haversine entre las dos estaciones).
* ``time``: tiempo en minutos (distancia / velocidad comercial de la línea).
* ``line``: línea a la que pertenece la arista, o ``"transbordo"``.
"""

from math import atan2, cos, radians, sin, sqrt

import networkx as nx

from .datos import (
    LINEAS,
    TIEMPO_TRANSBORDO_MIN,
    TRANSBORDOS,
    VELOCIDADES,
)

RADIO_TIERRA_M = 6_371_000


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Distancia en metros entre dos puntos dados en grados decimales.

    Tiene en cuenta la curvatura de la Tierra, así que es más precisa que la
    distancia euclídea sobre latitud/longitud.
    """
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    return RADIO_TIERRA_M * 2 * atan2(sqrt(a), sqrt(1 - a))


def distancia_entre(coord1, coord2) -> float:
    """Distancia Haversine entre dos tuplas (lat, lon)."""
    return haversine(coord1[0], coord1[1], coord2[0], coord2[1])


def construir_grafo() -> nx.Graph:
    """Crea el grafo completo: estaciones, tramos de cada línea y transbordos."""
    grafo = nx.Graph()

    # 1) Nodos: una estación = un nodo, con su posición y su línea.
    for linea, estaciones in LINEAS.items():
        for estacion, coord in estaciones.items():
            grafo.add_node(estacion, pos=coord, line=linea)

    # 2) Aristas entre estaciones consecutivas de la misma línea.
    for linea, estaciones in LINEAS.items():
        nombres = list(estaciones)
        for origen, destino in zip(nombres, nombres[1:]):
            metros = distancia_entre(estaciones[origen], estaciones[destino])
            minutos = metros / VELOCIDADES[linea] / 60
            grafo.add_edge(origen, destino, length=metros, time=minutos, line=linea)

    # 3) Aristas de transbordo.
    #    - Tiempo: coste fijo de TIEMPO_TRANSBORDO_MIN minutos.
    #    - Distancia: línea recta entre las dos estaciones. Usar la distancia
    #      real (y no un valor pequeño fijo) mantiene la heurística admisible,
    #      porque el pasillo nunca es más corto que la línea recta.
    for est1, est2 in TRANSBORDOS:
        grafo.add_edge(
            est1,
            est2,
            length=distancia_entre(grafo.nodes[est1]["pos"], grafo.nodes[est2]["pos"]),
            time=TIEMPO_TRANSBORDO_MIN,
            line="transbordo",
        )

    return grafo
