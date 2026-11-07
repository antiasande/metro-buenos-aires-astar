"""
Comprobación del horario de servicio del Subte según el día de la semana.

Horarios usados (aproximados, según la web del operador en 2024):

* Lunes a viernes: 05:00 - 22:20
* Sábados: 05:00 - 22:30
* Domingos y festivos: 08:00 - 22:00
"""

from datetime import date, datetime, time, timedelta

from .datos import FESTIVOS

AVISO_CIERRE = time(21, 30)


def es_festivo(fecha: date) -> bool:
    """True si la fecha es festivo nacional en Argentina (lista fija en datos.py)."""
    return fecha.strftime("%d-%m") in FESTIVOS


def horario_servicio(fecha: date) -> tuple:
    """Devuelve (hora de apertura, hora de cierre) para una fecha."""
    if es_festivo(fecha) or fecha.weekday() == 6:  # domingo o festivo
        return time(8, 0), time(22, 0)
    if fecha.weekday() == 5:  # sábado
        return time(5, 0), time(22, 30)
    return time(5, 0), time(22, 20)  # lunes a viernes


def comprobar_horario(fecha: date, hora: time, minutos_viaje: float = 0.0) -> tuple:
    """
    Comprueba si se puede hacer el viaje a esa hora.

    Devuelve ``(operativo, mensaje)``. Si el metro está cerrado al salir o
    cerraría antes de llegar, ``operativo`` es False.
    """
    apertura, cierre = horario_servicio(fecha)
    if not apertura <= hora <= cierre:
        return False, (
            f"El metro no funciona a esa hora. Ese día abre a las "
            f"{apertura:%H:%M} y cierra a las {cierre:%H:%M}."
        )

    llegada = (datetime.combine(fecha, hora) + timedelta(minutes=minutos_viaje)).time()
    if llegada > cierre:
        return False, f"El metro cierra a las {cierre:%H:%M} y no daría tiempo a llegar."

    if hora >= AVISO_CIERRE:
        return True, f"Atención: el servicio termina a las {cierre:%H:%M}."
    return True, ""
