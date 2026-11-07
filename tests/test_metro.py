"""
Pruebas del cálculo de rutas.

Se ejecutan con:  python -m pytest
"""

from datetime import date, time
from itertools import permutations

import networkx as nx
import pytest

from metro.astar import HEURISTICAS, buscar_ruta
from metro.datos import LINEAS, TRANSBORDOS
from metro.grafo import construir_grafo, haversine
from metro.horario import comprobar_horario

G = construir_grafo()
PARES = list(permutations(G.nodes, 2))
PESOS = {"tiempo": "time", "distancia": "length"}


def test_grafo_tiene_todas_las_estaciones_y_tramos():
    n_estaciones = sum(len(e) for e in LINEAS.values())
    n_tramos = sum(len(e) - 1 for e in LINEAS.values())
    assert G.number_of_nodes() == n_estaciones == 34
    assert G.number_of_edges() == n_tramos + len(TRANSBORDOS)
    assert nx.is_connected(G)


def test_haversine_valor_conocido():
    # Madrid (Puerta del Sol) - Barcelona (Plaça Catalunya): ~505 km en línea recta
    d = haversine(40.4169, -3.7035, 41.3870, 2.1700)
    assert 500_000 < d < 510_000


@pytest.mark.parametrize("criterio", ["tiempo", "distancia"])
def test_heuristica_admisible(criterio):
    """h(n) nunca supera el coste real mínimo hasta el destino."""
    h = HEURISTICAS[criterio]
    peso = PESOS[criterio]
    for destino in G.nodes:
        coste_real = nx.single_source_dijkstra_path_length(G, destino, weight=peso)
        for nodo in G.nodes:
            assert h(G, nodo, destino) <= coste_real[nodo] + 1e-9


@pytest.mark.parametrize("criterio", ["tiempo", "distancia"])
def test_astar_es_optimo_para_todos_los_pares(criterio):
    """A* devuelve el mismo coste que Dijkstra para los 1.122 pares de estaciones."""
    peso = PESOS[criterio]
    for origen, destino in PARES:
        ruta = buscar_ruta(G, origen, destino, criterio)
        optimo = nx.dijkstra_path_length(G, origen, destino, weight=peso)
        coste = ruta.minutos if criterio == "tiempo" else ruta.metros
        assert coste == pytest.approx(optimo)


def test_ruta_con_transbordo():
    ruta = buscar_ruta(G, "Pasteur", "Plaza de Mayo", "tiempo")
    assert ruta.estaciones[0] == "Pasteur" and ruta.estaciones[-1] == "Plaza de Mayo"
    assert len(ruta.transbordos) >= 1


def test_misma_estacion():
    ruta = buscar_ruta(G, "Retiro", "Retiro")
    assert ruta.estaciones == ["Retiro"]
    assert ruta.minutos == 0 and ruta.metros == 0


def test_criterio_invalido():
    with pytest.raises(ValueError):
        buscar_ruta(G, "Retiro", "Constitución", "precio")


def test_horarios():
    lunes, domingo = date(2024, 12, 2), date(2024, 12, 1)
    assert comprobar_horario(lunes, time(4, 30))[0] is False
    assert comprobar_horario(lunes, time(12, 0)) == (True, "")
    assert comprobar_horario(domingo, time(7, 0))[0] is False   # domingos abre a las 8
    assert comprobar_horario(lunes, time(21, 45))[0] is True     # con aviso de cierre
    assert comprobar_horario(lunes, time(22, 15), minutos_viaje=15)[0] is False
    navidad = date(2024, 12, 25)                                 # festivo
    assert comprobar_horario(navidad, time(7, 30))[0] is False
