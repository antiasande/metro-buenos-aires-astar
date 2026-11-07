"""
Cálculo de la velocidad comercial media de cada línea del Subte.

Para estimar el tiempo de cada tramo necesitamos la velocidad de cada línea.
La obtenemos así:

1. Distancia total de la línea completa (de cabecera a cabecera), sumando las
   distancias Haversine entre estaciones consecutivas.
2. Tiempo que tarda el tren en recorrer la línea completa (horarios oficiales).
3. Velocidad media = distancia / tiempo, en m/s.

Los valores obtenidos se copian en ``metro/datos.py`` (VELOCIDADES).

Ejecutar con:  python scripts/calculo_velocidades.py
"""

# Distancias (m) entre estaciones consecutivas de cada línea COMPLETA.
DISTANCIAS_COMPLETAS = {
    "LINEA_A": [
        ("Carabobo", "Puan", 666.10),
        ("Puan", "Primera Junta", 770.65),
        ("Primera Junta", "Acoyte", 576.81),
        ("Acoyte", "Rio de Janeiro", 678.99),
        ("Rio de Janeiro", "Castro Barros", 799.44),
        ("Castro Barros", "Loria", 605.62),
        ("Loria", "Plaza Miserere", 755.08),
        ("Plaza Miserere", "Alberti", 536.48),
        ("Alberti", "Pasco", 234.71),
        ("Pasco", "Congreso", 519.97),
        ("Congreso", "Sáenz Peña", 549.30),
        ("Sáenz Peña", "Lima", 380.56),
        ("Lima", "Piedras", 360.89),
        ("Piedras", "Perú", 339.32),
        ("Perú", "Plaza de Mayo", 312.92)
    ],
    "LINEA_B": [
        ("De Los Incas", "Tronador", 738.35),
        ("Tronador", "Federico Lacroze", 1077.21),
        ("Federico Lacroze", "Dorrego", 857.96),
        ("Dorrego", "Malabia", 1096.97),
        ("Malabia", "Ángel Gallardo", 852.50),
        ("Ángel Gallardo", "Medrano", 910.95),
        ("Medrano", "Carlos Gardel", 870.01),
        ("Carlos Gardel", "Pueyrredón_B", 583.53),
        ("Pueyrredón_B", "Pasteur", 524.81),
        ("Pasteur", "Callao_B", 664.36),
        ("Callao_B", "Uruguay", 522.25),
        ("Uruguay", "Carlos Pellegrini", 491.78),
        ("Carlos Pellegrini", "Florida", 627.78),
        ("Florida", "Leandro N. Alem", 412.32)
    ],
    "LINEA_C": [
        ("Constitución", "San Juan", 616.99),
        ("San Juan", "Independencia_C", 456.97),
        ("Independencia_C", "Moreno", 632.36),
        ("Moreno", "Avenida de Mayo", 376.04),
        ("Avenida de Mayo", "Diagonal Norte", 475.74),
        ("Diagonal Norte", "Lavalle", 329.50),
        ("Lavalle", "General San Martin", 729.56),
        ("General San Martin", "Retiro", 376.73)
    ],
    "LINEA_D": [
        ("Congreso de Tucumán", "Juramento", 809.99),
        ("Juramento", "Jose Hernández", 561.80),
        ("Jose Hernández", "Olleros", 838.39),
        ("Olleros", "Mtro. Carranza", 1052.78),
        ("Mtro. Carranza", "Palermo", 857.24),
        ("Palermo", "Plaza Italia", 529.33),
        ("Plaza Italia", "Scalabrini Ortiz", 660.35),
        ("Scalabrini Ortiz", "Bulnes", 558.38),
        ("Bulnes", "Aguero", 529.27),
        ("Aguero", "Pueyrredón_D", 471.58),
        ("Pueyrredón_D", "Facultad de Medicina", 758.25),
        ("Facultad de Medicina", "Callao_D", 497.41),
        ("Callao_D", "Tribunales", 749.65),
        ("Tribunales", "9 de Julio", 508.97),
        ("9 de Julio", "Catedral", 640.07)
    ],
    "LINEA_E": [
        ("Plaza De Los Virreyes", "Varela", 460.01),
        ("Varela", "Medalla Milagrosa", 827.15),
        ("Medalla Milagrosa", "Emilio Mitre", 941.79),
        ("Emilio Mitre", "Jose María Moreno", 846.51),
        ("Jose María Moreno", "Av. La Plata", 672.50),
        ("Av. La Plata", "Boedo", 929.33),
        ("Boedo", "General Urquiza", 637.11),
        ("General Urquiza", "Jujuy", 601.21),
        ("Jujuy", "Pichincha", 525.94),
        ("Pichincha", "Entre Ríos", 514.80),
        ("Entre Ríos", "San José", 575.60),
        ("San José", "Independencia_E", 647.70),
        ("Independencia_E", "Belgrano", 624.34),
        ("Belgrano", "Bolívar", 504.77)
    ]
}


# Tiempo (min) que tarda un tren en recorrer cada línea de punta a punta.
TIEMPOS_LINEA_MIN = {
    "LINEA_A": 23,
    "LINEA_B": 23,
    "LINEA_C": 13,
    "LINEA_D": 26,
    "LINEA_E": 24,
}


def velocidad_media(distancia_m: float, tiempo_min: float) -> float:
    """Velocidad media en m/s."""
    return distancia_m / (tiempo_min * 60)


if __name__ == "__main__":
    print(f"{'Línea':<8}{'Distancia (m)':>15}{'Tiempo (min)':>14}{'Velocidad (m/s)':>17}{'(km/h)':>9}")
    for linea, tramos in DISTANCIAS_COMPLETAS.items():
        distancia = sum(d for _, _, d in tramos)
        tiempo = TIEMPOS_LINEA_MIN[linea]
        v = velocidad_media(distancia, tiempo)
        print(f"{linea:<8}{distancia:>15.0f}{tiempo:>14}{v:>17.3f}{v * 3.6:>9.1f}")
