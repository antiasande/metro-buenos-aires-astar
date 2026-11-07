"""
Datos de la red del Subte de Buenos Aires usados en el proyecto.

Incluye el tramo de cada línea que pide el enunciado, las coordenadas de cada
estación (obtenidas de Google Maps), los transbordos entre líneas, la velocidad
comercial media de cada línea y el calendario de festivos.

Las estaciones que tienen el mismo nombre en dos líneas distintas llevan un
sufijo interno (``Callao_B`` / ``Callao_D``, ``Independencia_C`` /
``Independencia_E``) para que sean nodos diferentes del grafo. En la interfaz
se muestran sin el sufijo mediante :func:`nombre_visible`.
"""

# --------------------------------------------------------------------------- #
# Coordenadas (latitud, longitud) de cada estación, en orden de recorrido.
# El orden importa: dos estaciones consecutivas de una línea quedan unidas
# por una arista en el grafo.
# --------------------------------------------------------------------------- #
LINEAS = {
    "LINEA_A": {
        "Alberti": (-34.60979154021843, -58.40086740463643),
        "Pasco": (-34.609455989895245, -58.39833539938651),
        "Congreso": (-34.608996813572965, -58.39268130286541),
        "Sáenz Peña": (-34.609350026351635, -58.38669461230903),
        "Lima": (-34.60904096524644, -58.382553281561165),
        "Piedras": (-34.60886435838594, -58.37861579874318),
        "Perú": (-34.60857295624564, -58.37492507907565),
        "Plaza de Mayo": (-34.60875839408815, -58.37151330936176),
    },
    "LINEA_B": {
        "Pasteur": (-34.60409382222638, -58.39968610352264),
        "Callao_B": (-34.60434108592872, -58.39243341083207),
        "Uruguay": (-34.60400961150244, -58.38674150304544),
        "Carlos Pellegrini": (-34.60370936151744, -58.381380708823514),
        "Florida": (-34.603244782294965, -58.37454489610343),
        "Leandro N. Alem": (-34.60302925135683, -58.37004749037363),
    },
    "LINEA_C": {
        "Constitución": (-34.62753942668646, -58.38156121435256),
        "San Juan": (-34.622153370728164, -58.37994066311232),
        "Independencia_C": (-34.6180519466846, -58.380256098860485),
        "Moreno": (-34.61237244698663, -58.38060876062811),
        "Avenida de Mayo": (-34.60899098423044, -58.38066790483753),
        "Diagonal Norte": (-34.60482400192541, -58.379488963667214),
        "Lavalle": (-34.60207510706261, -58.37814441867528),
        "General San Martín": (-34.59553840845914, -58.37745834587982),
        "Retiro": (-34.59238671801715, -58.37594819705223),
    },
    "LINEA_D": {
        "Facultad de Medicina": (-34.5993682836706, -58.3977359491304),
        "Callao_D": (-34.59957140474557, -58.392307158181815),
        "Tribunales": (-34.60176154833913, -58.38456093858365),
        "9 de Julio": (-34.60453888530524, -58.38014065809253),
        "Catedral": (-34.60757221396939, -58.37419688300631),
    },
    "LINEA_E": {
        "Pichincha": (-34.62304099718662, -58.39710097116426),
        "Entre Ríos": (-34.62270550042393, -58.391489789929345),
        "San José": (-34.62224639739259, -58.385224149714155),
        "Independencia_E": (-34.61812318513492, -58.380224512115895),
        "Belgrano": (-34.6128518852584, -58.37787489702144),
        "Bolívar": (-34.60961123829135, -58.37401251606132),
    },
}

# Colores oficiales aproximados de cada línea (nombres válidos para Folium).
COLORES_LINEA = {
    "LINEA_A": "lightblue",
    "LINEA_B": "red",
    "LINEA_C": "darkblue",
    "LINEA_D": "green",
    "LINEA_E": "purple",
}
COLOR_TRANSBORDO = "orange"

# --------------------------------------------------------------------------- #
# Transbordos indicados en el enunciado. Cada pareja es una arista entre dos
# estaciones de líneas distintas que están conectadas a pie.
# --------------------------------------------------------------------------- #
TRANSBORDOS = [
    ("Independencia_C", "Independencia_E"),  # C <-> E
    ("Bolívar", "Perú"),                     # E <-> A
    ("Bolívar", "Catedral"),                 # E <-> D
    ("Perú", "Catedral"),                    # A <-> D
    ("Lima", "Avenida de Mayo"),             # A <-> C
    ("Diagonal Norte", "9 de Julio"),        # C <-> D
    ("Diagonal Norte", "Carlos Pellegrini"),  # C <-> B
    ("9 de Julio", "Carlos Pellegrini"),     # D <-> B
]

# Tiempo fijo que se asigna a un transbordo: minutos andando entre andenes
# (estimación media). En distancia, el transbordo cuenta como la distancia en
# línea recta entre las dos estaciones (ver grafo.py).
TIEMPO_TRANSBORDO_MIN = 2.0

# --------------------------------------------------------------------------- #
# Velocidad comercial media de cada línea en m/s.
# Se obtiene dividiendo la longitud total de la línea entre el tiempo que
# tarda el tren en recorrerla de punta a punta (ver scripts/calculo_velocidades.py).
# --------------------------------------------------------------------------- #
VELOCIDADES = {
    "LINEA_A": 5.860,
    "LINEA_B": 7.414,
    "LINEA_C": 5.120,
    "LINEA_D": 6.425,
    "LINEA_E": 6.464,
}
VELOCIDAD_MAX = max(VELOCIDADES.values())

# Festivos nacionales de Argentina usados en el cálculo de horarios (formato DD-MM).
FESTIVOS = [
    "01-01", "24-03", "02-04", "01-05", "25-05", "20-06",
    "09-07", "17-08", "12-10", "20-11", "08-12", "25-12",
]


def linea_de(estacion: str) -> str:
    """Devuelve la clave de la línea a la que pertenece una estación."""
    for linea, estaciones in LINEAS.items():
        if estacion in estaciones:
            return linea
    raise KeyError(f"Estación desconocida: {estacion}")


def nombre_visible(estacion: str) -> str:
    """Quita el sufijo interno de línea: 'Callao_B' -> 'Callao (B)'."""
    if "_" in estacion:
        nombre, letra = estacion.rsplit("_", 1)
        return f"{nombre} ({letra})"
    return estacion


def nombre_linea(linea: str) -> str:
    """'LINEA_A' -> 'Línea A'."""
    return "Línea " + linea.split("_")[1]
