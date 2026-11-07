"""
Calculadora de rutas del Subte de Buenos Aires (interfaz web con Streamlit).

Ejecutar con:
    streamlit run app.py
"""

from datetime import datetime, timedelta

import folium
import networkx as nx
import streamlit as st
from streamlit_folium import st_folium

from metro import buscar_ruta, construir_grafo
from metro.datos import COLOR_TRANSBORDO, COLORES_LINEA, LINEAS, nombre_linea, nombre_visible
from metro.horario import comprobar_horario

CENTRO_MAPA = (-34.6085, -58.3840)

st.set_page_config(page_title="Rutas Subte Buenos Aires", page_icon="🚇", layout="wide")


@st.cache_resource
def obtener_grafo() -> nx.Graph:
    """El grafo se construye una sola vez y se reutiliza entre recargas."""
    return construir_grafo()


G = obtener_grafo()


# --------------------------------------------------------------------------- #
# Mapa
# --------------------------------------------------------------------------- #
def dibujar_mapa(ruta=None) -> folium.Map:
    """Dibuja la red completa y, si se pasa una ruta, la resalta encima."""
    mapa = folium.Map(location=CENTRO_MAPA, zoom_start=14, tiles="cartodbpositron")

    # Tramos de cada línea y transbordos
    for a, b, datos in G.edges(data=True):
        es_transbordo = datos["line"] == "transbordo"
        folium.PolyLine(
            [G.nodes[a]["pos"], G.nodes[b]["pos"]],
            color=COLOR_TRANSBORDO if es_transbordo else COLORES_LINEA[datos["line"]],
            weight=3 if es_transbordo else 5,
            dash_array="6" if es_transbordo else None,
            opacity=0.6 if ruta else 0.9,
        ).add_to(mapa)

    # Estaciones
    for estacion, datos in G.nodes(data=True):
        folium.CircleMarker(
            datos["pos"],
            radius=5,
            color=COLORES_LINEA[datos["line"]],
            fill=True,
            fill_opacity=1,
            tooltip=f"{nombre_visible(estacion)} · {nombre_linea(datos['line'])}",
        ).add_to(mapa)

    # Ruta calculada
    if ruta:
        coords = [G.nodes[e]["pos"] for e in ruta.estaciones]
        folium.PolyLine(coords, color="black", weight=7, opacity=0.85).add_to(mapa)
        folium.Marker(coords[0], tooltip="Origen", icon=folium.Icon(color="green", icon="play")).add_to(mapa)
        folium.Marker(coords[-1], tooltip="Destino", icon=folium.Icon(color="red", icon="flag")).add_to(mapa)
        mapa.fit_bounds(coords, padding=(40, 40))

    return mapa


# --------------------------------------------------------------------------- #
# Indicaciones paso a paso
# --------------------------------------------------------------------------- #
def indicaciones(ruta) -> list:
    """Agrupa la ruta en tramos: 'Línea B de X a Y (n paradas)' y transbordos."""
    pasos = []
    tramo_inicio, linea_actual, paradas = ruta.estaciones[0], None, 0
    for a, b in zip(ruta.estaciones, ruta.estaciones[1:]):
        linea = G.edges[a, b]["line"]
        if linea == "transbordo":
            if linea_actual:
                pasos.append((linea_actual, tramo_inicio, a, paradas))
            pasos.append(("transbordo", a, b, 0))
            tramo_inicio, linea_actual, paradas = b, None, 0
        else:
            linea_actual, paradas = linea, paradas + 1
    if linea_actual:
        pasos.append((linea_actual, tramo_inicio, ruta.estaciones[-1], paradas))

    textos = []
    for linea, desde, hasta, n in pasos:
        if linea == "transbordo":
            textos.append(f"🚶 Transbordo a pie de **{nombre_visible(desde)}** a **{nombre_visible(hasta)}**")
        else:
            textos.append(
                f"🚇 **{nombre_linea(linea)}** de {nombre_visible(desde)} a {nombre_visible(hasta)} "
                f"({n} parada{'s' if n != 1 else ''})"
            )
    return textos


# --------------------------------------------------------------------------- #
# Interfaz
# --------------------------------------------------------------------------- #
st.title("🚇 Calculadora de rutas · Subte de Buenos Aires")
st.caption(
    "Ruta óptima entre dos estaciones calculada con el algoritmo de búsqueda **A\\***. "
    "Puedes optimizar por tiempo de viaje o por distancia recorrida."
)

estaciones = [e for linea in LINEAS.values() for e in linea]  # ordenadas por línea

with st.sidebar:
    st.header("Configura tu viaje")
    origen = st.selectbox(
        "Estación de origen", estaciones, index=None, placeholder="Elige una estación",
        format_func=lambda e: f"{nombre_visible(e)} · {nombre_linea(G.nodes[e]['line'])}",
    )
    destino = st.selectbox(
        "Estación de destino", estaciones, index=None, placeholder="Elige una estación",
        format_func=lambda e: f"{nombre_visible(e)} · {nombre_linea(G.nodes[e]['line'])}",
    )
    criterio = st.radio(
        "Optimizar por", ["tiempo", "distancia"], horizontal=True,
        format_func=lambda c: "⏱️ Tiempo" if c == "tiempo" else "📏 Distancia",
    )
    ahora = datetime.now()
    fecha = st.date_input("Fecha de salida", value=ahora.date(), min_value=ahora.date(), format="DD/MM/YYYY")
    hora = st.time_input("Hora de salida", value=ahora.time().replace(second=0, microsecond=0), step=300)
    calcular = st.button("Calcular ruta", type="primary", use_container_width=True)

if calcular:
    st.session_state.pop("ruta", None)
    st.session_state.pop("aviso", None)
    if not origen or not destino:
        st.session_state["error"] = "Selecciona una estación de origen y otra de destino."
    elif origen == destino:
        st.session_state["error"] = "El origen y el destino son la misma estación: no hace falta desplazarse."
    else:
        ruta = buscar_ruta(G, origen, destino, criterio)
        operativo, mensaje = comprobar_horario(fecha, hora, ruta.minutos)
        if not operativo:
            st.session_state["error"] = mensaje
        else:
            st.session_state.pop("error", None)
            st.session_state["ruta"] = ruta
            st.session_state["aviso"] = mensaje
            st.session_state["salida"] = datetime.combine(fecha, hora)

if st.session_state.get("error"):
    st.warning(st.session_state["error"])

ruta = st.session_state.get("ruta")
col_mapa, col_info = st.columns([3, 2], gap="large")

with col_mapa:
    st_folium(dibujar_mapa(ruta), height=560, use_container_width=True, returned_objects=[])

with col_info:
    if ruta:
        llegada = st.session_state["salida"] + timedelta(minutes=ruta.minutos)
        if st.session_state.get("aviso"):
            st.info(st.session_state["aviso"])
        m1, m2 = st.columns(2)
        m1.metric("Duración", f"{ruta.minutos:.0f} min")
        m2.metric("Distancia", f"{ruta.metros / 1000:.2f} km")
        m3, m4 = st.columns(2)
        m3.metric("Transbordos", len(ruta.transbordos))
        m4.metric("Llegada", f"{llegada:%H:%M}")

        st.subheader("Indicaciones")
        for paso in indicaciones(ruta):
            st.markdown(f"- {paso}")

        with st.expander("Detalles del algoritmo"):
            st.write(
                f"A* evaluó la heurística en **{ruta.nodos_explorados}** de las "
                f"{G.number_of_nodes()} estaciones de la red."
            )
            st.write(" → ".join(nombre_visible(e) for e in ruta.estaciones))
    else:
        st.subheader("¿Cómo funciona?")
        st.markdown(
            "1. Elige origen, destino, fecha y hora en el panel lateral.\n"
            "2. Decide si quieres la ruta **más rápida** o la **más corta**.\n"
            "3. Pulsa **Calcular ruta**: verás el recorrido sobre el mapa, la hora "
            "de llegada estimada y las indicaciones paso a paso.\n\n"
            "La app avisa si el metro está cerrado a esa hora (horarios distintos "
            "para laborables, sábados, domingos y festivos)."
        )
        st.markdown("**Leyenda**")
        for linea, color in COLORES_LINEA.items():
            st.markdown(
                f"<span style='color:{color};font-size:1.3em'>━━</span> {nombre_linea(linea)}",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<span style='color:{COLOR_TRANSBORDO};font-size:1.3em'>╍╍</span> Transbordo",
            unsafe_allow_html=True,
        )
