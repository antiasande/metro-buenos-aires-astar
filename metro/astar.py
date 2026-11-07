"""
Búsqueda del camino óptimo con el algoritmo A*.

A* expande en cada paso el nodo con menor f(n) = g(n) + h(n):

* g(n): coste real acumulado desde el origen hasta n (suma de pesos de aristas).
* h(n): estimación del coste que falta desde n hasta el destino.

Si h(n) nunca sobreestima el coste real (heurística admisible), A* garantiza
encontrar el camino óptimo. Aquí se ofrecen dos criterios de optimización:

* ``"tiempo"``: g(n) en minutos; h(n) = distancia en línea recta hasta el
  destino / velocidad de la línea más rápida. Es admisible porque ningún
  tren puede ir más rápido que la línea más rápida ni recorrer menos que la
  línea recta.
* ``"distancia"``: g(n) en metros; h(n) = distancia en línea recta hasta el
  destino. Es admisible porque todos los tramos (también los transbordos) se
  miden en línea recta y, por la desigualdad triangular, la suma de varios
  tramos nunca es menor que el tramo directo.
"""

from dataclasses import dataclass, field

import networkx as nx

from .datos import VELOCIDAD_MAX
from .grafo import distancia_entre

CRITERIOS = {"tiempo": "time", "distancia": "length"}


def heuristica_distancia(grafo: nx.Graph, nodo: str, destino: str) -> float:
    """h(n) en metros: distancia en línea recta (Haversine) hasta el destino."""
    return distancia_entre(grafo.nodes[nodo]["pos"], grafo.nodes[destino]["pos"])


def heuristica_tiempo(grafo: nx.Graph, nodo: str, destino: str) -> float:
    """h(n) en minutos: línea recta hasta el destino a la velocidad máxima de la red."""
    return heuristica_distancia(grafo, nodo, destino) / VELOCIDAD_MAX / 60


HEURISTICAS = {"tiempo": heuristica_tiempo, "distancia": heuristica_distancia}


@dataclass
class Ruta:
    """Resultado de una búsqueda."""

    estaciones: list
    minutos: float
    metros: float
    transbordos: list = field(default_factory=list)
    nodos_explorados: int = 0


def buscar_ruta(grafo: nx.Graph, origen: str, destino: str, criterio: str = "tiempo") -> Ruta:
    """
    Calcula la ruta óptima entre ``origen`` y ``destino`` con A*.

    Devuelve un objeto :class:`Ruta` con las estaciones del camino, su duración
    total, su longitud total, los transbordos que incluye y el número de nodos
    para los que se evaluó la heurística (útil para comparar con Dijkstra).
    """
    if criterio not in CRITERIOS:
        raise ValueError(f"Criterio no válido: {criterio!r}. Usa 'tiempo' o 'distancia'.")

    peso = CRITERIOS[criterio]
    h = HEURISTICAS[criterio]
    evaluados = set()

    def heuristica(nodo, objetivo):
        evaluados.add(nodo)
        return h(grafo, nodo, objetivo)

    camino = nx.astar_path(grafo, origen, destino, heuristic=heuristica, weight=peso)

    aristas = [grafo.edges[a, b] for a, b in zip(camino, camino[1:])]
    return Ruta(
        estaciones=camino,
        minutos=sum(e["time"] for e in aristas),
        metros=sum(e["length"] for e in aristas),
        transbordos=[
            (a, b) for (a, b), e in zip(zip(camino, camino[1:]), aristas) if e["line"] == "transbordo"
        ],
        nodos_explorados=len(evaluados),
    )
